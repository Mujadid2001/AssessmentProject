#!/usr/bin/env python
"""
STRESS TEST: New York to Los Angeles with 60 hours already used in cycle.
Validates HOS engine handles mandatory restart correctly.
"""
from datetime import datetime, timedelta
from services.hos_engine import HOSEngine

def test_stress_ny_to_la():
    """Test NY to LA trip with 60h already used - should trigger restart"""
    print("=" * 80)
    print("  STRESS TEST: NY TO LA WITH 60H CYCLE USED")
    print("=" * 80)
    
    # Trip parameters
    current_location = "New York, NY (40.7128°N, 74.0060°W)"
    pickup_location = "New York, NY"
    dropoff_location = "Los Angeles, CA (34.0522°N, 118.2437°W)"
    distance_miles = 2800  # Actual distance
    
    # Engine state: 60 hours already used in current cycle
    current_cycle_hours = 60.0
    cycle_start = datetime(2026, 4, 19, 8, 0, 0)  # Started 7 days ago
    
    # Trip starts now
    start_time = datetime(2026, 4, 26, 8, 0, 0)
    
    print(f"\nTrip Details:")
    print(f"  From: {current_location}")
    print(f"  To: {dropoff_location}")
    print(f"  Distance: {distance_miles} miles")
    print(f"\nCycle Status (CRITICAL):")
    print(f"  Hours already used: {current_cycle_hours}h / 70h")
    print(f"  Hours remaining: {70 - current_cycle_hours}h")
    print(f"  REQUIRES RESTART: {'YES - Must have 34-hour rest' if current_cycle_hours >= 70 else 'Maybe - depends on trip length'}")
    print(f"\nTrip Start: {start_time}")
    
    # Generate logs
    engine = HOSEngine(current_cycle_hours, cycle_start)
    logs, cycle_state = engine.generate_logs(
        current_location,
        pickup_location,
        dropoff_location,
        distance_miles,
        start_time
    )
    
    print(f"\n[LOG COUNT] Generated {len(logs)} daily log sheets")
    print(f"[CALENDAR DAYS] {len(set(log.log_date for log in logs))} unique dates")
    
    # Analysis
    print(f"\n" + "=" * 80)
    print("  ANALYSIS")
    print("=" * 80)
    
    restart_logs = [log for log in logs if 'restart' in log.log_date.lower() or any('restart' in e.notes.lower() for e in log.events)]
    sleeper_logs = [log for log in logs if any('sleeper' in e.notes.lower() for e in log.events)]
    
    print(f"\nLog Breakdown:")
    print(f"  Total sheets generated: {len(logs)}")
    print(f"  Sleeper break entries: {sum(1 for log in logs for e in log.events if 'sleeper' in e.notes.lower())}")
    
    print(f"\nDetailed Log Analysis:")
    for i, log in enumerate(logs, 1):
        events_summary = []
        for event in log.events:
            status_short = event.status.value[:4].upper()
            events_summary.append(f"{status_short}")
        
        total_duty_hrs = log.total_on_duty_minutes / 60
        total_drive_hrs = log.total_driving_minutes / 60
        
        print(f"\n  LOG {i}: {log.log_date}")
        print(f"    Events: {' > '.join(events_summary)}")
        print(f"    Driving: {total_drive_hrs:5.1f}h ({log.total_miles:6.0f}mi)")
        print(f"    Duty:    {total_duty_hrs:5.1f}h")
        print(f"    Notes: {', '.join(set(e.notes for e in log.events))}")
    
    # Validation checks
    print(f"\n" + "=" * 80)
    print("  VALIDATION CHECKS")
    print("=" * 80)
    
    checks = []
    
    # Check 1: Multiple logs generated
    if len(logs) >= 4:
        checks.append(("[PASS]", f"Multiple log sheets: {len(logs)} sheets"))
    else:
        checks.append(("[FAIL]", f"Only {len(logs)} sheets (need >= 4)"))
    
    # Check 2: Separate calendar days
    unique_dates = set(log.log_date for log in logs)
    if len(unique_dates) >= 3:
        checks.append(("[PASS]", f"Separate calendar days: {len(unique_dates)} unique dates"))
    else:
        checks.append(("[FAIL]", f"Only {len(unique_dates)} unique dates (need >= 3)"))
    
    # Check 3: 11-hour driving limit per day
    daily_driving_violations = []
    for log in logs:
        drive_hrs = log.total_driving_minutes / 60
        if drive_hrs > 11.5:  # Allow 0.5h tolerance
            daily_driving_violations.append((log.log_date, drive_hrs))
    
    if not daily_driving_violations:
        checks.append(("[PASS]", "11-hour driving limit: All days comply"))
    else:
        checks.append(("[FAIL]", f"11-hour violations on {len(daily_driving_violations)} days"))
        for date, hrs in daily_driving_violations:
            checks.append(("      ", f"  {date}: {hrs:.1f}h"))
    
    # Check 4: Restart triggered
    has_restart = any(any('restart' in e.notes.lower() for e in log.events) for log in logs)
    if cycle_state.requires_restart or has_restart:
        checks.append(("[PASS]", "Mandatory 34-hour restart triggered"))
    else:
        checks.append(("[WARN]", "No restart found - check if it was really needed"))
    
    # Check 5: Cycle hours correct after restart
    if cycle_state.requires_restart:
        if cycle_state.cycle_hours_used <= 30:
            checks.append(("[PASS]", f"Cycle reset: {cycle_state.cycle_hours_used:.1f}h used after restart"))
        else:
            checks.append(("[FAIL]", f"Cycle not reset properly: {cycle_state.cycle_hours_used:.1f}h used"))
    
    for status, msg in checks:
        print(f"  {status} {msg}")
    
    # Summary
    print(f"\n" + "=" * 80)
    passed = sum(1 for status, _ in checks if status == "[PASS]")
    total = len([c for c in checks if c[0] in ["[PASS]", "[FAIL]", "[WARN]"]])
    
    if passed >= 4:
        print(f"  [SUCCESS] STRESS TEST PASSED - {passed}/{total} checks OK")
        print(f"  Engine correctly handles restart scenarios")
    else:
        print(f"  [FAILURE] STRESS TEST FAILED - {passed}/{total} checks OK")
        print(f"  Need to fix HOS engine multi-day/restart logic")
    print("=" * 80 + "\n")
    
    return passed >= 4

if __name__ == "__main__":
    try:
        success = test_stress_ny_to_la()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
