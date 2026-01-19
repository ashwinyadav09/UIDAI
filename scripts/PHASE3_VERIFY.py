"""
PHASE 3 - PRE-EXECUTION VERIFICATION
=====================================
Checks if everything is ready before running Phase 3

Author: UIDAI Hackathon Project
"""

import os
import sys

print("=" * 80)
print("PHASE 3 - PRE-EXECUTION VERIFICATION")
print("=" * 80)
print()
print("Checking if everything is ready to run Phase 3...")
print()

all_good = True

# ============================================================================
# CHECK 1: Python version
# ============================================================================
print("✓ Checking Python version...")
if sys.version_info >= (3, 7):
    print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor} - Good!")
else:
    print(f"  ❌ Python {sys.version_info.major}.{sys.version_info.minor} - Need 3.7+")
    all_good = False
print()

# ============================================================================
# CHECK 2: Required libraries
# ============================================================================
print("✓ Checking required libraries...")

libraries = {
    'pandas': 'Data manipulation',
    'numpy': 'Numerical operations',
    'matplotlib': 'Visualizations',
    'seaborn': 'Statistical visualizations',
    'sklearn': 'Machine learning (scikit-learn)'
}

missing_libs = []

for lib, desc in libraries.items():
    try:
        __import__(lib)
        print(f"  ✅ {lib:15s} - {desc}")
    except ImportError:
        print(f"  ❌ {lib:15s} - MISSING! ({desc})")
        missing_libs.append(lib)
        all_good = False

print()

if missing_libs:
    print("📦 To install missing libraries, run:")
    if 'sklearn' in missing_libs:
        missing_libs.remove('sklearn')
        missing_libs.append('scikit-learn')
    print(f"   pip install {' '.join(missing_libs)}")
    print()

# ============================================================================
# CHECK 3: Phase 2 completion (cleaned data exists)
# ============================================================================
print("✓ Checking Phase 2 completion (cleaned data)...")

required_files = [
    '../data/processed/cleaned_enrolment.csv',
    '../data/processed/cleaned_biometric.csv',
    '../data/processed/cleaned_demographic.csv'
]

missing_files = []

for file_path in required_files:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"  ✅ {os.path.basename(file_path):30s} ({size:,} bytes)")
    else:
        print(f"  ❌ {os.path.basename(file_path):30s} - MISSING!")
        missing_files.append(file_path)
        all_good = False

print()

if missing_files:
    print("⚠️  Phase 2 not complete! Please run:")
    print("   python STEP2_FINAL_intelligent_cleaning.py")
    print()

# ============================================================================
# CHECK 4: Output directories exist
# ============================================================================
print("✓ Checking output directories...")

directories = [
    '../results',
    '../visualizations'
]

for dir_path in directories:
    if os.path.exists(dir_path):
        print(f"  ✅ {dir_path}")
    else:
        print(f"  ⚠️  {dir_path} - Will be created automatically")

print()

# ============================================================================
# CHECK 5: Phase 3 scripts exist
# ============================================================================
print("✓ Checking Phase 3 scripts...")

phase3_scripts = [
    'PHASE3_STEP1_trend_prediction.py',
    'PHASE3_STEP2_child_enrolment_gap.py',
    'PHASE3_STEP3_biometric_compliance.py',
    'PHASE3_STEP4_anomaly_detection.py',
    'RUN_PHASE3_ALL.py'
]

for script in phase3_scripts:
    if os.path.exists(script):
        print(f"  ✅ {script}")
    else:
        print(f"  ❌ {script} - MISSING!")
        all_good = False

print()

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("=" * 80)
if all_good:
    print("✅ ALL CHECKS PASSED!")
    print("=" * 80)
    print()
    print("🎉 You're ready to run Phase 3!")
    print()
    print("To start, run:")
    print("   python RUN_PHASE3_ALL.py")
    print()
    print("This will:")
    print("  - Run all 4 core analyses")
    print("  - Generate 16 CSV result files")
    print("  - Create 4 professional visualizations")
    print("  - Take approximately 20-30 minutes")
    print()
    print("Good luck! 🚀")
else:
    print("❌ SOME CHECKS FAILED!")
    print("=" * 80)
    print()
    print("Please fix the issues above before running Phase 3.")
    print()
    if missing_libs:
        print("1. Install missing libraries:")
        libs_to_install = missing_libs.copy()
        if 'sklearn' in libs_to_install:
            libs_to_install.remove('sklearn')
            libs_to_install.append('scikit-learn')
        print(f"   pip install {' '.join(libs_to_install)}")
        print()
    
    if missing_files:
        print("2. Run Phase 2 data cleaning:")
        print("   python STEP2_FINAL_intelligent_cleaning.py")
        print()
    
    print("Then run this verification script again:")
    print("   python PHASE3_VERIFY.py")

print("=" * 80)
