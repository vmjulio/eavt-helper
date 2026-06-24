#!/usr/bin/env python3
"""
Simple test runner for EAVT Helper.
This script runs all tests and provides a summary of results.
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests and display results."""
    print("🧪 Running EAVT Helper Test Suite")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run pytest with verbose output and coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        # Check if pytest-cov is available
        subprocess.run([sys.executable, "-c", "import pytest_cov"], 
                      check=True, capture_output=True)
        cmd.extend(["--cov=eavt_helper", "--cov-report=term-missing"])
    except subprocess.CalledProcessError:
        print("📝 Note: pytest-cov not installed, running without coverage")
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    # Run the tests
    result = subprocess.run(cmd)
    
    print("\n" + "=" * 50)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        
    return result.returncode


def run_specific_tests():
    """Run specific test categories."""
    test_categories = {
        "1": ("Unit Tests - Snapshot", "tests/test_snapshot.py"),
        "2": ("Unit Tests - EAVT", "tests/test_eavt.py"),
        "3": ("Unit Tests - Commands", "tests/test_commands.py"),
        "4": ("Unit Tests - Transformations", "tests/test_transformation_functions.py"),
        "5": ("Unit Tests - Main CLI", "tests/test_main.py"),
        "6": ("All Tests", "tests/")
    }
    
    print("🧪 EAVT Helper Test Runner")
    print("=" * 30)
    print("Select test category to run:")
    print()
    
    for key, (name, _) in test_categories.items():
        print(f"{key}. {name}")
    
    print()
    choice = input("Enter your choice (1-6): ").strip()
    
    if choice in test_categories:
        name, path = test_categories[choice]
        print(f"\n🏃 Running {name}...")
        print("-" * 30)
        
        cmd = [sys.executable, "-m", "pytest", path, "-v", "--tb=short", "--color=yes"]
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"✅ {name} passed!")
        else:
            print(f"❌ {name} failed!")
            
        return result.returncode
    else:
        print("❌ Invalid choice!")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        sys.exit(run_specific_tests())
    else:
        sys.exit(run_tests()) 