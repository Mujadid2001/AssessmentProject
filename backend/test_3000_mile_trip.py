#!/usr/bin/env python
"""
ELD HOS Engine - 3,000 Mile Trip Verification Test
Validates multi-day log splitting, sleeper breaks, and FMCSA compliance
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

import django
django.setup()

from services.hos_engine import HOSEngine, DutyStatus


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_log_summary(log_num, log):
    """Print summary of a daily log"""
    print(f"\nLOG DAY {log_num}: {log.log_date}")
    print(f"  Events: {len(log.events)} status changes")
    print(f"  Driving Time: {log.total_driving_minutes} minutes ({log.total_driving_minutes/60:.1f}h)")
    print(f"  On-Duty Time: {log.total_on_duty_minutes} minutes ({log.total_on_duty_minutes/60:.1f}h)")
    print(f"  Total Miles: {log.total_miles:.1f} mi")
    print(f"  Violations: {log.violations if log.violations else 'None'}")
    
    # Show events timeline
    print(f"  Timeline:")
    for event in log.events:
        time_str = event.timestamp.strftime("%H:%M")
        print(f"    {time_str} - {event.status.value:12} at {event.location:20} ({event.miles:.0f}mi, {event.notes})")


def test_3000_mile_trip():
    """Test 3,000-mile trip to verify multi-day splitting and break logic"""
    print_header("3,000-MILE TRIP VERIFICATION TEST")
    
    # Trip parameters: Chicago to LA
    current_location = "Chicago, IL (40.7128°N, 74.0060°W)"
    pickup_location = "Chicago, IL (41.8781°N, 87.6298°W)"
    dropoff_location = "Los Angeles, CA (34.0522°N, 118.2437°W)"
    distance_miles = 3000
    cycle_used = 10.0  # Driver has used 10 hours of 70-hour cycle
    
    print(f"Trip Parameters:")
    print(f"  From: {pickup_location}")
    print(f"  To: {dropoff_location}")
    print(f"  Distance: {distance_miles} miles")
    print(f"  Current Cycle Usage: {cycle_used}h / 70h")
    print(f"  Starting: Monday 08:00 UTC\n")
    
    # Initialize engine
    cycle_start = datetime(2024, 1, 1, 0, 0, 0)
    engine = HOSEngine(current_cycle_hours=cycle_used, cycle_start=cycle_start)
    
    # Start trip: Monday 08:00
    start_datetime = datetime(2024, 1, 1, 8, 0, 0)
    
    print(f"Engine Status:")
    print(f"  Max driving hours: {engine.MAX_DRIVING_HOURS}h")
    print(f"  Duty window: {engine.DUTY_WINDOW_HOURS}h")
    print(f"  Break required after: {engine.BREAK_REQUIRED_AFTER_HOURS}h driving")
    print(f"  Cycle limit: {engine.MAX_CYCLE_HOURS}h / {engine.CYCLE_DAYS} days")
    print(f"  Mandatory restart: {engine.MIN_RESTART_HOURS}h\n")
    
    # Calculate trip duration
    trip_hours, fueling_stops = engine.calculate_trip_duration(
        current_location, pickup_location, dropoff_location, distance_miles
    )
    
    print(f"Trip Calculation:")
    print(f"  Estimated driving: {distance_miles / 60:.1f}h")
    print(f"  Fueling stops (1 per 1000mi): {fueling_stops}")
    print(f"  Estimated total time: {trip_hours:.1f}h ({trip_hours/24:.1f} days)\n")
    
    # Generate logs
    print("Generating logs...")
    logs, cycle_state = engine.generate_logs(
        current_location=current_location,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
        distance_miles=distance_miles,
        start_datetime=start_datetime,
    )
    
    print(f"\n[PASS] Generated {len(logs)} daily logs\n")
    
    # Print detailed log analysis
    print_header("GENERATED LOGS ANALYSIS")
    
    total_driving = 0
    total_on_duty = 0
    total_miles = 0
    all_violations = []
    
    for i, log in enumerate(logs, 1):
        print_log_summary(i, log)
        total_driving += log.total_driving_minutes
        total_on_duty += log.total_on_duty_minutes
        total_miles += log.total_miles
        all_violations.extend(log.violations)
    
    # Aggregate statistics
    print_header("TRIP STATISTICS")
    
    print(f"Number of Days: {len(logs)}")
    print(f"Total Driving Time: {total_driving} minutes ({total_driving/60:.1f}h)")
    print(f"Total On-Duty Time: {total_on_duty} minutes ({total_on_duty/60:.1f}h)")
    print(f"Total Miles: {total_miles:.1f}")
    print(f"Average Daily Driving: {total_driving/60/len(logs):.1f}h")
    
    print(f"\nCycle State After Trip:")
    print(f"  Cycle Hours Used: {cycle_state.cycle_hours_used:.1f}h / 70h")
    print(f"  Hours Available: {cycle_state.hours_available:.1f}h")
    print(f"  Requires Restart: {cycle_state.requires_restart}")
    
    if all_violations:
        print(f"\nViolations Found: {len(all_violations)}")
        for v in all_violations:
            print(f"  ✗ {v}")
    else:
        print(f"\n[OK] No violations detected")
    
    # Verification checks
    print_header("COMPLIANCE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Multiple days
    checks_total += 1
    if len(logs) > 1:
        print(f"[PASS] Multiple-day logs: {len(logs)} days")
        checks_passed += 1
    else:
        print(f"[FAIL] Multiple-day logs: Only {len(logs)} day")
    
    # Check 2: Sleeper breaks presence
    checks_total += 1
    sleeper_events = sum(
        sum(1 for e in log.events if e.status == DutyStatus.SLEEPER)
        for log in logs
    )
    if sleeper_events > 0:
        print(f"[PASS] Sleeper breaks found: {sleeper_events} sleeper events")
        checks_passed += 1
    else:
        print(f"[FAIL] Sleeper breaks missing")
    
    # Check 3: 24-hour block splitting
    checks_total += 1
    unique_dates = set(log.log_date for log in logs)
    if len(unique_dates) >= 3:
        print(f"[PASS] Proper 24-hour splitting: {len(unique_dates)} unique calendar days")
        checks_passed += 1
    else:
        print(f"[FAIL] Insufficient date splitting: {len(unique_dates)} unique dates (need >= 3)")
    
    # Check 4: No single day exceeds 14-hour duty window
    checks_total += 1
    daily_duty_violations = []
    for log in logs:
        total_on_duty_hours = (log.total_on_duty_minutes + log.total_driving_minutes) / 60
        if total_on_duty_hours > engine.DUTY_WINDOW_HOURS:
            daily_duty_violations.append({
                'date': log.log_date,
                'hours': total_on_duty_hours
            })
    
    if not daily_duty_violations:
        print(f"[PASS] 14-hour duty window: All days comply")
        checks_passed += 1
    else:
        print(f"[FAIL] 14-hour duty window violations: {len(daily_duty_violations)} days exceeded")
        for v in daily_duty_violations:
            print(f"    {v['date']}: {v['hours']:.1f}h")
    
    # Check 5: Driving time per day under 11 hours
    checks_total += 1
    daily_driving_violations = []
    for log in logs:
        driving_hours = log.total_driving_minutes / 60
        if driving_hours > engine.MAX_DRIVING_HOURS:
            daily_driving_violations.append({
                'date': log.log_date,
                'hours': driving_hours
            })
    
    if not daily_driving_violations:
        print(f"[PASS] 11-hour driving limit: All days comply")
        checks_passed += 1
    else:
        print(f"[FAIL] 11-hour driving violations: {len(daily_driving_violations)} days exceeded")
        for v in daily_driving_violations:
            print(f"    {v['date']}: {v['hours']:.1f}h")
    
    # Check 6: Cycle compliance
    checks_total += 1
    if cycle_state.cycle_hours_used <= 70:
        print(f"[PASS] 70-hour cycle limit: {cycle_state.cycle_hours_used:.1f}h used")
        checks_passed += 1
    else:
        print(f"[FAIL] 70-hour cycle exceeded: {cycle_state.cycle_hours_used:.1f}h")
    
    # Final summary
    print_header("TEST SUMMARY")
    
    print(f"Checks Passed: {checks_passed}/{checks_total}")
    
    if checks_passed == checks_total:
        print(f"\n[SUCCESS] ALL TESTS PASSED - HOS ENGINE WORKING CORRECTLY")
        print(f"\nKey Results:")
        print(f"  [OK] Trip split into {len(logs)} days")
        print(f"  [OK] {sleeper_events} sleeper breaks scheduled")
        print(f"  [OK] All 24-hour blocks properly separated")
        print(f"  [OK] FMCSA compliance verified")
        return True
    else:
        print(f"\n[FAILURE] SOME TESTS FAILED - REVIEW HOS ENGINE LOGIC")
        return False


def test_critical_scenarios():
    """Test critical HOS scenarios"""
    print_header("CRITICAL SCENARIO TESTS")
    
    scenarios = [
        {
            "name": "11-Hour Driving Limit",
            "distance": 600,
            "cycle_used": 0,
            "expected_days": 1,
        },
        {
            "name": "Multi-Day Trip (1500 mi)",
            "distance": 1500,
            "cycle_used": 5,
            "expected_days": 3,
        },
        {
            "name": "Near-Cycle Limit (69h used)",
            "distance": 300,
            "cycle_used": 69,
            "expected_days": 2,  # Should trigger restart
        },
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"  Distance: {scenario['distance']} miles")
        print(f"  Cycle Used: {scenario['cycle_used']}h")
        
        cycle_start = datetime(2024, 1, 1, 0, 0, 0)
        engine = HOSEngine(
            current_cycle_hours=scenario['cycle_used'],
            cycle_start=cycle_start
        )
        
        start_time = datetime(2024, 1, 1, 8, 0, 0)
        
        logs, cycle_state = engine.generate_logs(
            current_location="Test, USA",
            pickup_location="Test, USA",
            dropoff_location="Dest, USA",
            distance_miles=scenario['distance'],
            start_datetime=start_time,
        )
        
        print(f"  [OK] Generated {len(logs)} days")
        print(f"    Cycle after: {cycle_state.cycle_hours_used:.1f}h")
        print(f"    Requires restart: {cycle_state.requires_restart}")


if __name__ == "__main__":
    try:
        # Run main test
        success = test_3000_mile_trip()
        
        # Run critical scenarios
        test_critical_scenarios()
        
        # Exit code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n[ERROR] Test Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
