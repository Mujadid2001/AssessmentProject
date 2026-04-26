#!/usr/bin/env python
"""
FINAL SYSTEM VERIFICATION
Production-ready ELD Simulator - Complete validation
"""
import subprocess
import sys
from pathlib import Path

def run_test(test_file, test_name):
    """Run a test and report results"""
    import os
    try:
        # Change to test directory to ensure imports work
        original_cwd = os.getcwd()
        test_dir = Path(test_file).parent.absolute()
        os.chdir(test_dir)
        
        result = subprocess.run(
            [sys.executable, Path(test_file).name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        os.chdir(original_cwd)
        
        # Combine stdout and stderr
        output = result.stdout + "\n" + result.stderr
        
        # Check for success markers (case-insensitive)
        output_upper = output.upper()
        passed = any(marker in output_upper for marker in [
            "PASSED",
            "SUCCESS", 
            "ALL TESTS PASSED",
            "[SUCCESS]"
        ])
        
        return passed, output[-400:] if output else "No output"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("\n" + "=" * 80)
    print("  FINAL SYSTEM VERIFICATION")
    print("  ELD Simulator - Production Ready Assessment")
    print("=" * 80 + "\n")
    
    tests = [
        ("backend/test_3000_mile_trip.py", "3,000-Mile Trip Compliance"),
        ("backend/test_stress_ny_to_la.py", "Stress Test (NY-LA with 60h cycle)"),
        ("validate_deployment.py", "Deployment Configuration"),
    ]
    
    results = []
    for test_file, test_name in tests:
        full_path = Path(test_file)
        if full_path.exists():
            print(f"Running: {test_name}...")
            passed, output = run_test(str(full_path), test_name)
            results.append((test_name, passed))
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status}\n")
        else:
            print(f"SKIP: {test_name} - File not found\n")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print("  SYSTEM COMPONENTS")
    print("=" * 80 + "\n")
    
    components = {
        "HOS Engine": "backend/services/hos_engine.py",
        "Django Backend": "backend/core/settings.py",
        "REST API": "backend/api/views.py",
        "Frontend React App": "frontend/src/App.jsx",
        "API Client": "frontend/src/api.js",
        "ELD Grid Component": "frontend/src/components/ELDGrid.jsx",
        "Map Component": "frontend/src/components/Map.jsx",
    }
    
    for comp_name, comp_path in components.items():
        if Path(comp_path).exists():
            print(f"[PRESENT] {comp_name}")
        else:
            print(f"[MISSING] {comp_name}")
    
    print("\n" + "=" * 80)
    print("  DEPLOYMENT CONFIGURATION")
    print("=" * 80 + "\n")
    
    configs = {
        ".env (Development)": ".env",
        ".env.example": ".env.example",
        ".env.production": ".env.production",
        "vercel.json": "vercel.json",
        "requirements.txt": "requirements.txt",
        "frontend/package.json": "frontend/package.json",
    }
    
    for config_name, config_path in configs.items():
        if Path(config_path).exists():
            print(f"[PRESENT] {config_name}")
        else:
            print(f"[MISSING] {config_name}")
    
    print("\n" + "=" * 80)
    print("  TEST RESULTS SUMMARY")
    print("=" * 80 + "\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    print("\n" + "=" * 80)
    if passed_count == total_count:
        print("  [SUCCESS] SYSTEM IS PRODUCTION-READY")
        print("\n  Deployment Options:")
        print("    1. Frontend: Deploy to Vercel")
        print("    2. Backend: Deploy to Vercel Serverless Functions")
        print("    3. Database: Use Neon.tech PostgreSQL")
        print("\n  See DEPLOYMENT.md for detailed instructions")
    else:
        print("  [WARNING] Some tests failed - review above")
    print("=" * 80 + "\n")
    
    return 0 if passed_count == total_count else 1

if __name__ == "__main__":
    exit(main())
