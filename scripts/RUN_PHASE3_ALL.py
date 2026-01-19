"""
PHASE 3 MASTER SCRIPT - Run All Core Analyses
==============================================
Executes all Phase 3 analyses in sequence

Author: UIDAI Hackathon Project
"""

import subprocess
import sys
from datetime import datetime

print("=" * 80)
print("PHASE 3: CORE ANALYSIS - MASTER EXECUTION")
print("=" * 80)
print()
print("This script will run all 4 core analyses:")
print("  1. State-wise Trend Prediction")
print("  2. Child Enrolment Gap Analysis")
print("  3. Biometric Update Compliance Analysis")
print("  4. AI-Driven Anomaly Detection")
print()
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

scripts = [
    ('STEP 1', 'PHASE3_STEP1_trend_prediction.py', 'State-wise Trend Prediction'),
    ('STEP 2', 'PHASE3_STEP2_child_enrolment_gap.py', 'Child Enrolment Gap Analysis'),
    ('STEP 3', 'PHASE3_STEP3_biometric_compliance.py', 'Biometric Update Compliance'),
    ('STEP 4', 'PHASE3_STEP4_anomaly_detection.py', 'AI-Driven Anomaly Detection')
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
print("🎉 PHASE 3 COMPLETE - ALL ANALYSES FINISHED!")
print("=" * 80)
print()
print("📊 EXECUTION SUMMARY:")
print()

for step, desc, status in results:
    print(f"  {status}  {step}: {desc}")

print()
print("📁 ALL OUTPUT FILES CREATED:")
print()
print("  Predictions:")
print("    ✓ results/predictions_enrolment.csv")
print("    ✓ results/predictions_biometric.csv")
print("    ✓ results/predictions_demographic.csv")
print("    ✓ results/high_demand_states_biometric.csv")
print("    ✓ results/high_demand_states_demographic.csv")
print()
print("  Child Enrolment Gaps:")
print("    ✓ results/child_enrolment_gap_analysis.csv")
print("    ✓ results/at_risk_states_age_0_5.csv")
print("    ✓ results/at_risk_states_age_5_17.csv")
print("    ✓ results/critical_priority_states.csv")
print()
print("  Biometric Compliance:")
print("    ✓ results/biometric_compliance_analysis.csv")
print("    ✓ results/low_compliance_states.csv")
print("    ✓ results/intervention_priority_states.csv")
print()
print("  Anomaly Detection:")
print("    ✓ results/anomaly_detection_complete.csv")
print("    ✓ results/anomalies_isolation_forest.csv")
print("    ✓ results/anomalies_zscore.csv")
print("    ✓ results/anomalies_dbscan.csv")
print("    ✓ results/consensus_anomalies_HIGH_PRIORITY.csv")
print()
print("  Visualizations:")
print("    ✓ visualizations/PHASE3_01_trend_predictions.png")
print("    ✓ visualizations/PHASE3_02_child_enrolment_gaps.png")
print("    ✓ visualizations/PHASE3_03_biometric_compliance.png")
print("    ✓ visualizations/PHASE3_04_anomaly_detection.png")
print()
print("=" * 80)
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("🎯 NEXT STEPS:")
print("  1. Review all visualizations in visualizations/ folder")
print("  2. Examine results CSV files in results/ folder")
print("  3. Prepare for Phase 4: Report Generation")
print()
print("=" * 80)
