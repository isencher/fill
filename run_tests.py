#!/usr/bin/env python3
"""
Test runner script for Fill application.

Runs all tests and generates coverage report.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """Run all tests."""
    tests_dir = Path(__file__).parent / "tests"
    
    # Test categories
    test_categories = [
        ("Unit Tests", ["tests/unit/"]),
        ("Integration Tests", ["tests/integration/"]),
        ("E2E Tests", ["tests/e2e/"]),
    ]
    
    results = []
    
    for category_name, paths in test_categories:
        cmd = [
            sys.executable, "-m", "pytest",
            *paths,
            "-v",
            "--tb=short",
            "--strict-markers",
        ]
        success = run_command(cmd, category_name)
        results.append((category_name, success))
    
    # Run new validation tests
    validation_tests = [
        ("Mapping API Validation", ["tests/integration/test_mapping_api_validation.py"]),
        ("SQLite Persistence", ["tests/integration/test_sqlite_persistence.py"]),
        ("Processor", ["tests/unit/test_processor.py"]),
        ("Helpers", ["tests/unit/test_helpers.py"]),
    ]
    
    for test_name, paths in validation_tests:
        if Path(paths[0]).exists():
            cmd = [
                sys.executable, "-m", "pytest",
                *paths,
                "-v",
                "--tb=short",
            ]
            success = run_command(cmd, test_name)
            results.append((test_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
