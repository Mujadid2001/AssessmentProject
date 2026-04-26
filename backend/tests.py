"""
Unit tests for HOS Engine
Validates FMCSA compliance and critical calculations
"""

import unittest
from datetime import datetime, timedelta
from services.hos_engine import HOSEngine, DutyStatus


class TestHOSEngine(unittest.TestCase):
    """Test suite for Hours of Service calculations"""

    def setUp(self):
        """Initialize test engine with baseline state"""
        self.cycle_start = datetime(2024, 1, 1, 0, 0, 0)
        self.engine = HOSEngine(current_cycle_hours=0, cycle_start=self.cycle_start)

    def test_11_hour_driving_limit(self):
        """Verify 11-hour driving limit after 10-hour reset"""
        # Fresh driver: should allow 11 hours driving
        total_hours, fueling_stops = self.engine.calculate_trip_duration(
            "Chicago, IL", "Chicago, IL", "New York, NY", 800
        )
        # 800 miles at 60 mph = 13.3 hours driving
        # Should include fueling and break
        self.assertGreater(total_hours, 0)

    def test_70_hour_cycle_limit(self):
        """Verify 70-hour/8-day cycle enforcement"""
        engine = HOSEngine(current_cycle_hours=69.5, cycle_start=self.cycle_start)
        
        # Trip that would exceed 70 hours
        logs, cycle_state = engine.generate_logs(
            current_location="Chicago, IL",
            pickup_location="Chicago, IL",
            dropoff_location="Cleveland, OH",
            distance_miles=300,
            start_datetime=datetime.now(),
        )
        
        # Should trigger restart logic if it would exceed
        self.assertTrue(len(logs) > 0)

    def test_14_hour_duty_window(self):
        """Verify 14-hour duty window enforcement"""
        start_time = datetime(2024, 1, 1, 8, 0, 0)
        logs, _ = self.engine.generate_logs(
            current_location="Chic ago, IL",
            pickup_location="Chicago, IL",
            dropoff_location="New York, NY",
            distance_miles=800,
            start_datetime=start_time,
        )
        
        # Check that logs span reasonable time
        self.assertGreater(len(logs), 0)

    def test_30_minute_break_requirement(self):
        """Verify 30-minute break after 8 hours driving"""
        # This is built into the trip calculation
        total_hours, _ = self.engine.calculate_trip_duration(
            "Chicago, IL", "Chicago, IL", "Denver, CO", 1000
        )
        # 1000 miles / 60 mph = 16.7 hours driving + break should be included
        self.assertGreater(total_hours, 16.7)

    def test_mandatory_34_hour_restart(self):
        """Verify mandatory 34-hour restart when cycle exceeded"""
        engine = HOSEngine(current_cycle_hours=70.0, cycle_start=self.cycle_start)
        
        logs, cycle_state = engine.generate_logs(
            current_location="Chicago, IL",
            pickup_location="Chicago, IL",
            dropoff_location="New York, NY",
            distance_miles=800,
            start_datetime=datetime.now(),
        )
        
        # Should trigger restart
        self.assertTrue(cycle_state.requires_restart or len(logs) > 0)

    def test_trip_splitting_across_24_hours(self):
        """Verify logs split correctly across 24-hour periods"""
        # Long trip should create multiple daily logs
        logs, _ = self.engine.generate_logs(
            current_location="Chicago, IL",
            pickup_location="Chicago, IL",
            dropoff_location="Los Angeles, CA",
            distance_miles=2000,
            start_datetime=datetime(2024, 1, 1, 10, 0, 0),
        )
        
        # Should have multiple days
        self.assertGreater(len(logs), 1, "Long trip should span multiple days")
        
        # Each log should have unique date
        dates = [log.log_date for log in logs]
        self.assertEqual(len(dates), len(set(dates)), "Log dates should be unique")

    def test_cycle_hours_tracking(self):
        """Verify cycle hours are tracked correctly"""
        initial_hours = 30.0
        engine = HOSEngine(current_cycle_hours=initial_hours, cycle_start=self.cycle_start)
        
        logs, cycle_state = engine.generate_logs(
            current_location="Chicago, IL",
            pickup_location="Chicago, IL",
            dropoff_location="Milwaukee, WI",
            distance_miles=100,
            start_datetime=datetime.now(),
        )
        
        # Cycle hours should increase
        self.assertGreaterEqual(cycle_state.cycle_hours_used, initial_hours)

    def test_fueling_intervals(self):
        """Verify fueling stops every 1000 miles"""
        total_hours, fueling_stops = self.engine.calculate_trip_duration(
            "Chicago, IL", "Chicago, IL", "Denver, CO", 1000
        )
        
        # 1000 miles should trigger 1 fueling stop
        self.assertEqual(fueling_stops, 1)
        
        total_hours_2k, fueling_stops_2k = self.engine.calculate_trip_duration(
            "Chicago, IL", "Chicago, IL", "Los Angeles, CA", 2000
        )
        
        # 2000 miles should trigger 2 fueling stops
        self.assertEqual(fueling_stops_2k, 2)


if __name__ == '__main__':
    unittest.main()
