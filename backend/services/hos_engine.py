"""
Hours of Service (HOS) Engine for Property-carrying drivers
Implements 70-hour/8-day cycle rules with FMCSA compliance
REWRITTEN: Accurate multi-day trip splitting with mandatory sleeper breaks
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import math


class DutyStatus(Enum):
    """Valid HOS duty statuses per FMCSA"""
    OFF_DUTY = "OFF_DUTY"
    SLEEPER = "SLEEPER"
    DRIVING = "DRIVING"
    ON_DUTY = "ON_DUTY"


@dataclass
class LogEvent:
    """Individual log entry representing a duty status change"""
    timestamp: datetime
    status: DutyStatus
    location: str
    miles: float = 0.0
    notes: str = ""


@dataclass
class DailyLog:
    """24-hour log object (00:00 to 23:59)"""
    log_date: str  # YYYY-MM-DD
    events: List[LogEvent] = field(default_factory=list)
    total_driving_minutes: int = 0
    total_on_duty_minutes: int = 0
    total_miles: float = 0.0
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "log_date": self.log_date,
            "events": [
                {
                    "timestamp": evt.timestamp.isoformat(),
                    "status": evt.status.value,
                    "location": evt.location,
                    "miles": evt.miles,
                    "notes": evt.notes,
                }
                for evt in self.events
            ],
            "total_driving_minutes": self.total_driving_minutes,
            "total_on_duty_minutes": self.total_on_duty_minutes,
            "total_miles": self.total_miles,
            "violations": self.violations,
        }


@dataclass
class CycleState:
    """Tracks driver cycle hour usage across 8-day rolling window"""
    cycle_hours_used: float
    cycle_start_date: datetime
    hours_available: float
    requires_restart: bool = False
    restart_triggered_at_hours: Optional[float] = None


class HOSEngine:
    """
    Core HOS calculation engine implementing FMCSA 70/8 cycle rules.
    
    Rules implemented:
    - 11-hour driving limit after 10-hour off-duty reset
    - 14-hour duty window (non-extendable) from first activity
    - 30-minute break required after 8 hours cumulative driving
    - 70-hour/8-day cycle with mandatory 34-hour restart
    - Multi-day trips automatically split with 10-hour sleeper breaks
    """

    # Constants per FMCSA regulations
    MAX_DRIVING_HOURS = 11
    MIN_RESET_HOURS = 10
    DUTY_WINDOW_HOURS = 14
    MAX_CYCLE_HOURS = 70
    CYCLE_DAYS = 8
    BREAK_REQUIRED_AFTER_HOURS = 8
    BREAK_DURATION_MINUTES = 30
    MIN_RESTART_HOURS = 34
    SLEEPER_DURATION_HOURS = 10

    # Event durations in minutes
    PICKUP_DURATION_MINUTES = 60
    DROPOFF_DURATION_MINUTES = 60
    FUELING_DURATION_MINUTES = 30
    FUELING_INTERVAL_MILES = 1000

    def __init__(self, current_cycle_hours: float, cycle_start: datetime):
        """
        Initialize HOS engine with current cycle state.
        
        Args:
            current_cycle_hours: Hours already used in current 70-hour cycle
            cycle_start: Start datetime of current 8-day cycle
        """
        self.cycle_hours_used = current_cycle_hours
        self.cycle_start = cycle_start
        self.hours_available = self.MAX_CYCLE_HOURS - current_cycle_hours
        self.requires_restart = current_cycle_hours >= self.MAX_CYCLE_HOURS

    def calculate_trip_duration(
        self,
        start_location: str,
        pickup_location: str,
        dropoff_location: str,
        distance_miles: float,
    ) -> Tuple[float, int]:
        """
        Calculate total trip duration in hours and fueling stops.
        
        Args:
            start_location: Current location
            pickup_location: Pickup location
            dropoff_location: Delivery location
            distance_miles: Total distance to travel
            
        Returns:
            Tuple of (total_hours, number_of_fueling_stops)
        """
        driving_hours = distance_miles / 60.0
        fueling_stops = int(distance_miles / self.FUELING_INTERVAL_MILES)
        fueling_hours = (fueling_stops * self.FUELING_DURATION_MINUTES) / 60.0
        
        pickup_hours = self.PICKUP_DURATION_MINUTES / 60.0
        dropoff_hours = self.DROPOFF_DURATION_MINUTES / 60.0
        
        break_hours = 0.5 if driving_hours > self.BREAK_REQUIRED_AFTER_HOURS else 0
        
        total_hours = driving_hours + fueling_hours + pickup_hours + dropoff_hours + break_hours
        
        return total_hours, fueling_stops

    def generate_logs(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
        distance_miles: float,
        start_datetime: datetime,
    ) -> Tuple[List[DailyLog], CycleState]:
        """
        Generate complete log entries for a trip with automatic multi-day splitting.
        """
        total_trip_hours, fueling_stops = self.calculate_trip_duration(
            current_location, pickup_location, dropoff_location, distance_miles
        )

        cycle_state = CycleState(
            cycle_hours_used=self.cycle_hours_used,
            cycle_start_date=self.cycle_start,
            hours_available=self.hours_available,
        )

        if self.requires_restart:
            cycle_state.requires_restart = True
            cycle_state.restart_triggered_at_hours = self.cycle_hours_used
            return self._generate_restart_logs(start_datetime), cycle_state

        will_trigger_restart = (self.cycle_hours_used + total_trip_hours) > self.MAX_CYCLE_HOURS
        
        if will_trigger_restart:
            hours_before_restart = self.MAX_CYCLE_HOURS - self.cycle_hours_used
            remaining_hours = total_trip_hours - hours_before_restart
            remaining_distance = distance_miles * (remaining_hours / total_trip_hours)
            
            logs = self._generate_multi_day_trip(
                start_datetime, pickup_location, dropoff_location,
                distance_miles - remaining_distance
            )
            
            restart_start = logs[-1].events[-1].timestamp
            restart_logs = self._generate_restart_logs(restart_start)
            logs.extend(restart_logs)
            
            restart_end = restart_logs[-1].events[-1].timestamp
            
            cycle_state.cycle_hours_used = 0
            cycle_state.cycle_start_date = restart_end
            
            logs_phase2 = self._generate_multi_day_trip(
                restart_end, pickup_location, dropoff_location, remaining_distance
            )
            logs.extend(logs_phase2)
            cycle_state.cycle_hours_used = remaining_hours
        else:
            logs = self._generate_multi_day_trip(
                start_datetime, pickup_location, dropoff_location, distance_miles
            )
            cycle_state.cycle_hours_used += total_trip_hours
        
        cycle_state.hours_available = self.MAX_CYCLE_HOURS - cycle_state.cycle_hours_used
        return logs, cycle_state

    def _generate_multi_day_trip(
        self,
        start_time: datetime,
        pickup_location: str,
        dropoff_location: str,
        distance_miles: float,
    ) -> List[DailyLog]:
        """
        Generate multi-day logs with automatic 24-hour splitting and sleeper breaks.
        Enforces 11-hour driving and 14-hour duty window per day.
        """
        logs: List[DailyLog] = []
        current_time = start_time
        miles_remaining = distance_miles
        
        # Day 1: Pickup
        current_date = current_time.strftime("%Y-%m-%d")
        current_log = DailyLog(log_date=current_date)
        
        current_log.events.append(LogEvent(
            timestamp=current_time,
            status=DutyStatus.ON_DUTY,
            location=pickup_location,
            miles=0,
            notes="Pickup"
        ))
        current_log.total_on_duty_minutes += self.PICKUP_DURATION_MINUTES
        current_time += timedelta(minutes=self.PICKUP_DURATION_MINUTES)
        
        daily_driving_mins = 0
        daily_duty_mins = self.PICKUP_DURATION_MINUTES
        driving_since_break = 0
        
        while miles_remaining > 0:
            # Check if we need to move to next day
            if current_time.day != int(current_date.split('-')[2]):
                # Save current log and move to next day
                logs.append(current_log)
                
                # Add sleeper break
                sleeper_date = current_time.strftime("%Y-%m-%d")
                sleeper_log = DailyLog(log_date=sleeper_date)
                sleeper_log.events.append(LogEvent(
                    timestamp=current_time - timedelta(hours=2),
                    status=DutyStatus.SLEEPER,
                    location="Rest Stop",
                    miles=0,
                    notes="10-hour sleeper break"
                ))
                sleeper_log.total_on_duty_minutes += self.SLEEPER_DURATION_HOURS * 60
                logs.append(sleeper_log)
                
                current_date = current_time.strftime("%Y-%m-%d")
                current_log = DailyLog(log_date=current_date)
                daily_driving_mins = 0
                daily_duty_mins = 0
                driving_since_break = 0
                continue
            
            # Check duty window limit (14 hours)
            if daily_duty_mins >= self.DUTY_WINDOW_HOURS * 60:
                # End of duty window, must rest
                logs.append(current_log)
                
                sleeper_date = (current_time + timedelta(days=1)).strftime("%Y-%m-%d")
                sleeper_log = DailyLog(log_date=sleeper_date)
                sleeper_log.events.append(LogEvent(
                    timestamp=current_time,
                    status=DutyStatus.SLEEPER,
                    location="Rest Stop",
                    miles=0,
                    notes="10-hour sleeper break"
                ))
                sleeper_log.total_on_duty_minutes += self.SLEEPER_DURATION_HOURS * 60
                logs.append(sleeper_log)
                
                current_time = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                current_date = current_time.strftime("%Y-%m-%d")
                current_log = DailyLog(log_date=current_date)
                daily_driving_mins = 0
                daily_duty_mins = 0
                driving_since_break = 0
                continue
            
            # Check driving limit (11 hours)
            if daily_driving_mins >= self.MAX_DRIVING_HOURS * 60:
                # Max driving reached, rest
                logs.append(current_log)
                
                sleeper_date = (current_time + timedelta(days=1)).strftime("%Y-%m-%d")
                sleeper_log = DailyLog(log_date=sleeper_date)
                sleeper_log.events.append(LogEvent(
                    timestamp=current_time,
                    status=DutyStatus.SLEEPER,
                    location="Rest Stop",
                    miles=0,
                    notes="10-hour sleeper break"
                ))
                sleeper_log.total_on_duty_minutes += self.SLEEPER_DURATION_HOURS * 60
                logs.append(sleeper_log)
                
                current_time = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                current_date = current_time.strftime("%Y-%m-%d")
                current_log = DailyLog(log_date=current_date)
                daily_driving_mins = 0
                daily_duty_mins = 0
                driving_since_break = 0
                continue
            
            # Check 8-hour break requirement
            if driving_since_break >= self.BREAK_REQUIRED_AFTER_HOURS * 60:
                # Take mandatory break
                current_log.events.append(LogEvent(
                    timestamp=current_time,
                    status=DutyStatus.OFF_DUTY,
                    location="Rest Stop",
                    miles=0,
                    notes="30-minute break"
                ))
                current_log.total_on_duty_minutes += self.BREAK_DURATION_MINUTES
                daily_duty_mins += self.BREAK_DURATION_MINUTES
                current_time += timedelta(minutes=self.BREAK_DURATION_MINUTES)
                driving_since_break = 0
                continue
            
            # Drive segment (limited by 11-hour daily max and hours remaining in day)
            max_drive_mins = min(
                (self.MAX_DRIVING_HOURS * 60) - daily_driving_mins,
                (self.DUTY_WINDOW_HOURS * 60) - daily_duty_mins,
                (self.BREAK_REQUIRED_AFTER_HOURS * 60) - driving_since_break,
                int(miles_remaining * 60),  # At 60 mph
            )
            
            if max_drive_mins <= 0:
                continue
            
            drive_hours = max_drive_mins / 60.0
            drive_miles = min(drive_hours * 60, miles_remaining)
            drive_mins = int((drive_miles / 60) * 60)
            
            current_log.events.append(LogEvent(
                timestamp=current_time,
                status=DutyStatus.DRIVING,
                location=f"En route to {dropoff_location}",
                miles=drive_miles,
                notes=f"Driving {drive_miles:.0f}mi"
            ))
            
            current_log.total_driving_minutes += drive_mins
            current_log.total_miles += drive_miles
            daily_driving_mins += drive_mins
            daily_duty_mins += drive_mins
            driving_since_break += drive_mins
            
            current_time += timedelta(minutes=drive_mins)
            miles_remaining -= drive_miles
        
        # Final dropoff
        current_log.events.append(LogEvent(
            timestamp=current_time,
            status=DutyStatus.ON_DUTY,
            location=dropoff_location,
            miles=0,
            notes="Dropoff"
        ))
        current_log.total_on_duty_minutes += self.DROPOFF_DURATION_MINUTES
        
        logs.append(current_log)
        return logs

    def _generate_restart_logs(self, start_time: datetime) -> List[DailyLog]:
        """Generate 34-hour mandatory restart logs"""
        logs: List[DailyLog] = []
        current_time = start_time
        end_time = start_time + timedelta(hours=self.MIN_RESTART_HOURS)

        while current_time < end_time:
            log_date = current_time.strftime("%Y-%m-%d")
            if not logs or logs[-1].log_date != log_date:
                logs.append(DailyLog(log_date=log_date))

            logs[-1].events.append(LogEvent(
                timestamp=current_time,
                status=DutyStatus.SLEEPER,
                location="Rest Stop",
                miles=0.0,
                notes="Mandatory 34-hour restart",
            ))
            logs[-1].total_on_duty_minutes += 60

            current_time += timedelta(hours=1)

        return logs
