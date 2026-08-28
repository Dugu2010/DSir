#!/usr/bin/env python3
"""
Dependency security check script.
Run this to check for known vulnerabilities in dependencies.
"""
import subprocess
import sys
import json
from pathlib import Path


def run_safety_check():
    """Run safety check on dependencies."""
    try:
        # Run safety check
        result = subprocess.run(
            [sys.executable, "-m", "safety", "check", "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if result.returncode == 0:
            print("������✅ No known security vulnerabilities found in dependencies.")
            return True
        else:
            # Safety returns non-zero when vulnerabilities are found
            try:
                vulnerabilities = json.loads(result.stdout)
                print(f"������❌ Found {len(vulnerabilities)} security vulnerability(ies):")
                for vuln in vulnerabilities:
                    print(f"  - {vuln.get('package_name')} ({vuln.get('installed_version')}): {vuln.get('advisory')}")
                return False
            except json.JSONDecodeError:
                print(f"������❌ Safety check failed with output: {result.stdout}")
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
                return False
    except subprocess.TimeoutExpired:
        print("������⏰ Safety check timed out")
        return False
    except Exception as e:
        print(f"�������💥 Error running safety check: {e}")
        return False


def main():
    """Main function."""
    print("�������🔍 Checking dependencies for security vulnerabilities...")
    success = run_safety_check()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()