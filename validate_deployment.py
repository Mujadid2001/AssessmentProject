#!/usr/bin/env python
"""
Final Deployment Validation Script
Verifies all components are production-ready
"""
import os
import json
from pathlib import Path

def check_files_exist():
    """Verify critical files exist"""
    required_files = [
        "requirements.txt",
        "backend/core/settings.py",
        "backend/core/wsgi_handler.py",
        "frontend/package.json",
        "frontend/vite.config.js",
        "frontend/src/api.js",
        "vercel.json",
        ".env.production",
        ".env.example",
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    return len(missing) == 0, missing

def check_environment_variables():
    """Check all required env vars are documented"""
    required_vars = {
        "backend": ["DEBUG", "SECRET_KEY", "ALLOWED_HOSTS", "DATABASE_URL", "CORS_ALLOWED_ORIGINS"],
        "frontend": ["REACT_APP_API_URL"],
    }
    
    issues = []
    
    # Check .env.example
    if Path(".env.example").exists():
        with open(".env.example") as f:
            example = f.read()
            for var in required_vars["backend"]:
                if var not in example:
                    issues.append(f"Missing {var} in .env.example")
    
    # Check .env.production
    if Path(".env.production").exists():
        with open(".env.production") as f:
            prod = f.read()
            for var in required_vars["backend"]:
                if var not in prod:
                    issues.append(f"Missing {var} in .env.production")
    
    return len(issues) == 0, issues

def check_vercel_config():
    """Validate vercel.json configuration"""
    issues = []
    
    if not Path("vercel.json").exists():
        return False, ["vercel.json not found"]
    
    try:
        with open("vercel.json") as f:
            config = json.load(f)
        
        # Check builds
        if "builds" not in config:
            issues.append("No 'builds' section in vercel.json")
        
        # Check routes
        if "routes" not in config:
            issues.append("No 'routes' section in vercel.json")
        
        # Check env variables
        if "env" not in config:
            issues.append("No 'env' section in vercel.json")
        else:
            required_env = ["DEBUG", "SECRET_KEY", "ALLOWED_HOSTS", "DATABASE_URL"]
            for var in required_env:
                if var not in config["env"]:
                    issues.append(f"Missing {var} in vercel.json env")
    
    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON in vercel.json: {e}")
    
    return len(issues) == 0, issues

def check_frontend_config():
    """Validate frontend configuration"""
    issues = []
    
    # Check vite.config.js
    if Path("frontend/vite.config.js").exists():
        with open("frontend/vite.config.js") as f:
            vite_config = f.read()
            if "outDir" not in vite_config:
                issues.append("vite.config.js missing outDir configuration")
    
    # Check api.js uses environment variable
    if Path("frontend/src/api.js").exists():
        with open("frontend/src/api.js") as f:
            api_code = f.read()
            if "import.meta.env.VITE_API_URL" not in api_code:
                issues.append("frontend/src/api.js not using VITE_API_URL environment variable")
    
    return len(issues) == 0, issues

def check_backend_config():
    """Validate backend configuration"""
    issues = []
    
    # Check settings.py
    if Path("backend/core/settings.py").exists():
        with open("backend/core/settings.py") as f:
            settings_code = f.read()
            
            if "get_database_config()" not in settings_code:
                issues.append("settings.py not using dynamic database configuration")
            
            if "get_secret_key()" not in settings_code:
                issues.append("settings.py not using get_secret_key function")
    
    return len(issues) == 0, issues

def main():
    print("\n" + "=" * 80)
    print("  DEPLOYMENT VALIDATION")
    print("=" * 80 + "\n")
    
    checks = [
        ("Critical Files", check_files_exist()),
        ("Environment Variables", check_environment_variables()),
        ("Vercel Configuration", check_vercel_config()),
        ("Frontend Configuration", check_frontend_config()),
        ("Backend Configuration", check_backend_config()),
    ]
    
    all_passed = True
    for check_name, (passed, issues) in checks:
        if passed:
            print(f"[PASS] {check_name}")
        else:
            print(f"[FAIL] {check_name}")
            all_passed = False
            for issue in issues:
                print(f"       - {issue}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("  [SUCCESS] All deployment checks passed!")
        print("  Ready to deploy to Vercel + Neon.tech")
    else:
        print("  [FAILURE] Some checks failed - see above")
        print("  Fix issues before deploying")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
