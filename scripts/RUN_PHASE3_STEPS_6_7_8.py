"""
PHASE 3 - MASTER SCRIPT (Steps 6, 7, 8)
========================================
Runs Steps 6, 7, and 8 in sequence

Step 6: State-wise Trend Analysis
Step 7: Child Enrolment Gap Analysis
Step 8: Biometric Update Compliance Analysis

(Step 9: Anomaly Detection - to be run separately)

Author: UIDAI Hackathon Project
"""

import subprocess
import sys
from datetime import datetime

print("=" * 80)
print("PHASE 3: CORE ANALYSIS (Steps 6, 7, 8)")
print("=" * 80)
print()
print("This script will run:")
print("  Step 6: State-wise Trend Analysis")
print("  Step 7: Child Enrolment Gap Analysis")
print("  Step 8: Biometric Update Compliance Analysis")
print()
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

scripts = [
    ('STEP 6', 'PHASE3_STEP6_state_trend_analysis.py', 'State-wise Trend Analysis'),
    ('STEP 7', 'PHASE3_STEP7_child_enrolment_gap.py', 'Child Enrolment Gap Analysis'),
    ('STEP 8', 'PHASE3_STEP8_biometric_compliance.py', 'Biometric Update Compliance')
]

results = []

for step_num, script_name, description in scripts:
    print(f"\n{'=' * 80}")
    print(f"🚀 Running {step_num}: {description}")
    print(f"   Script: {script_name}")
    print(f"{'=' * 80}\n")
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print output
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Info:", result.stderr)
        
        results.append((step_num, description, '✅ SUCCESS'))
        print(f"\n✅ {step_num} completed successfully!")
        
    except subprocess.CalledProcessError as e:
        results.append((step_num, description, '❌ FAILED'))
        print(f"\n❌ {step_num} failed with error:")
        print(e.stderr)
        print("\nStopping execution. Please fix the error and try again.")
        sys.exit(1)

# Final summary
print("\n\n" + "=" * 80)
print("🎉 PHASE 3 (Steps 6, 7, 8) COMPLETE!")
print("=" * 80)
print()
print("📊 EXECUTION SUMMARY:")
print()

for step, desc, status in results:
    print(f"  {status}  {step}: {desc}")

print()
print("📁 ALL OUTPUT FILES CREATED:")
print()
print("  Step 6 - Trend Analysis:")
print("    ✓ results/STEP6_state_summary.csv")
print("    ✓ results/STEP6_enrolment_trends.csv")
print("    ✓ results/STEP6_biometric_trends.csv")
print("    ✓ results/STEP6_demographic_trends.csv")
print("    ✓ visualizations/STEP6_state_trends_top10.png")
print("    ✓ visualizations/STEP6_update_activity_comparison.png")
print()
print("  Step 7 - Child Enrolment Gaps:")
print("    ✓ results/STEP7_child_enrolment_analysis.csv")
print("    ✓ results/STEP7_at_risk_age_0_5.csv")
print("    ✓ results/STEP7_at_risk_age_5_17.csv")
print("    ✓ results/STEP7_critical_vulnerable_states.csv")
print("    ✓ visualizations/STEP7_child_enrolment_gaps.png")
print()
print("  Step 8 - Biometric Compliance:")
print("    ✓ results/STEP8_biometric_compliance_analysis.csv")
print("    ✓ results/STEP8_low_compliance_states.csv")
print("    ✓ results/STEP8_high_exclusion_risk_states.csv")
print("    ✓ results/STEP8_critical_intervention_states.csv")
print("    ✓ visualizations/STEP8_biometric_compliance.png")
print()
print("=" * 80)
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("🎯 NEXT STEPS:")
print("  1. Review all visualizations in visualizations/ folder")
print("  2. Examine results CSV files in results/ folder")
print("  3. Run Step 9 separately: PHASE3_STEP9_anomaly_detection.py")
print()
print("=" * 80)
