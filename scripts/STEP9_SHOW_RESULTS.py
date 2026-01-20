"""
STEP 9 - FINAL RESULTS SUMMARY
===============================
Display key findings from anomaly detection analysis
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("STEP 9 - ANOMALY DETECTION FRAMEWORK - FINAL RESULTS")
print("=" * 100)
print()

# Load all results
features_df = pd.read_csv('../results/STEP9_anomaly_detection_complete.csv')
iso_anomalies = pd.read_csv('../results/STEP9_isolation_forest_anomalies.csv')
zscore_anomalies = pd.read_csv('../results/STEP9_zscore_anomalies.csv')
temporal_anomalies = pd.read_csv('../results/STEP9_temporal_anomalies.csv')
consensus_anomalies = pd.read_csv('../results/STEP9_consensus_anomalies_HIGH_PRIORITY.csv')

print("📊 ANALYSIS SUMMARY")
print("=" * 100)
print(f"Total States/UTs Analyzed: {len(features_df)}")
print(f"Analysis Period: All available data")
print(f"Techniques Applied: 3 (Isolation Forest, Z-Score, Temporal Analysis)")
print()

print("🔍 DETECTION RESULTS")
print("=" * 100)
print(f"Isolation Forest Anomalies:    {len(iso_anomalies):3d} states ({len(iso_anomalies)/len(features_df)*100:5.1f}%)")
print(f"Z-Score Outliers (3-sigma):    {len(zscore_anomalies):3d} states ({len(zscore_anomalies)/len(features_df)*100:5.1f}%)")
print(f"Temporal Anomalies:            {len(features_df[features_df['temporal_anomaly']]):3d} states ({len(features_df[features_df['temporal_anomaly']])/len(features_df)*100:5.1f}%)")
print(f"Temporal Anomaly Events:       {len(temporal_anomalies):3d} total events")
print(f"Consensus Anomalies (2+ tech): {len(consensus_anomalies):3d} states ({len(consensus_anomalies)/len(features_df)*100:5.1f}%) ⚠️ HIGH PRIORITY")
print()

print("🎯 RISK DISTRIBUTION")
print("=" * 100)
risk_dist = features_df['anomaly_count'].value_counts().sort_index()
for level, count in risk_dist.items():
    risk_name = {0: 'NORMAL', 1: 'LOW RISK', 2: 'MEDIUM RISK', 3: 'CRITICAL RISK'}[level]
    percentage = count / len(features_df) * 100
    bar = '█' * int(percentage / 2)
    print(f"{level}/3 techniques - {risk_name:15s}: {count:3d} states ({percentage:5.1f}%) {bar}")
print()

if len(consensus_anomalies) > 0:
    print("🚨 CONSENSUS ANOMALIES (HIGH PRIORITY - Flagged by 2+ Techniques)")
    print("=" * 100)
    print(f"{'State':<40s} {'Anomaly Count':<15s} {'Techniques':<50s}")
    print("-" * 100)
    
    for idx, row in consensus_anomalies.iterrows():
        techniques = []
        if row['iso_forest_anomaly']:
            techniques.append('Isolation Forest')
        if row['zscore_anomaly']:
            techniques.append('Z-Score')
        if row['temporal_anomaly']:
            techniques.append('Temporal')
        
        tech_str = ', '.join(techniques)
        print(f"{row['state']:<40s} {row['anomaly_count']}/3{'':<12s} {tech_str:<50s}")
    print()

print("📈 TOP 10 STATES BY ISOLATION FOREST SCORE (Most Anomalous)")
print("=" * 100)
print(f"{'Rank':<6s} {'State':<40s} {'IF Score':<12s} {'Bio Rate%':<12s} {'Demo Rate%':<12s} {'Risk':<10s}")
print("-" * 100)

top_10_iso = features_df.nsmallest(10, 'iso_forest_score')
for rank, (idx, row) in enumerate(top_10_iso.iterrows(), 1):
    risk = {0: 'NORMAL', 1: 'LOW', 2: 'MEDIUM', 3: 'CRITICAL'}[row['anomaly_count']]
    print(f"{rank:<6d} {row['state']:<40s} {row['iso_forest_score']:<12.4f} {row['bio_update_rate']:<12.1f} {row['demo_update_rate']:<12.1f} {risk:<10s}")
print()

print("📊 TOP 10 STATES BY Z-SCORE (Bio Update Rate)")
print("=" * 100)
print(f"{'Rank':<6s} {'State':<40s} {'Z-Score (σ)':<15s} {'Bio Rate%':<12s} {'Status':<15s}")
print("-" * 100)

top_10_z = features_df.nlargest(10, 'bio_rate_zscore')
for rank, (idx, row) in enumerate(top_10_z.iterrows(), 1):
    status = 'OUTLIER (>3σ)' if row['bio_rate_zscore'] > 3 else 'Normal'
    print(f"{rank:<6d} {row['state']:<40s} {row['bio_rate_zscore']:<15.2f} {row['bio_update_rate']:<12.1f} {status:<15s}")
print()

if len(temporal_anomalies) > 0:
    print("⏱️  TOP 10 STATES BY TEMPORAL ANOMALY FREQUENCY")
    print("=" * 100)
    print(f"{'Rank':<6s} {'State':<40s} {'Anomaly Events':<20s} {'Max Change%':<15s}")
    print("-" * 100)
    
    temp_summary = temporal_anomalies.groupby('state').agg({
        'mom_change': ['count', lambda x: x.abs().max()]
    }).reset_index()
    temp_summary.columns = ['state', 'count', 'max_change']
    temp_summary = temp_summary.sort_values('count', ascending=False).head(10)
    
    for rank, (idx, row) in enumerate(temp_summary.iterrows(), 1):
        print(f"{rank:<6d} {row['state']:<40s} {int(row['count']):<20d} {row['max_change']:<15.1f}")
    print()

print("📁 OUTPUT FILES CREATED")
print("=" * 100)
print("\nCSV Results (in results/ directory):")
print("  1. STEP9_anomaly_detection_complete.csv - All states with all metrics")
print("  2. STEP9_isolation_forest_anomalies.csv - Isolation Forest anomalies")
print("  3. STEP9_zscore_anomalies.csv - Z-Score outliers")
print("  4. STEP9_temporal_anomalies.csv - Temporal anomaly events")
print("  5. STEP9_consensus_anomalies_HIGH_PRIORITY.csv - Consensus anomalies")
print()
print("Visualizations (in visualizations/ directory):")
print("  Original (5 files):")
print("    - STEP9_1_isolation_forest_detailed.png")
print("    - STEP9_2_zscore_heatmap_detailed.png")
print("    - STEP9_3_temporal_anomalies_timeseries.png")
print("    - STEP9_4_consensus_anomalies_detailed.png")
print("    - STEP9_5_summary_dashboard.png")
print()
print("  Enhanced (8 files):")
print("    - STEP9_ENHANCED_1_isolation_forest_advanced.png")
print("    - STEP9_ENHANCED_2_zscore_advanced.png")
print("    - STEP9_ENHANCED_3_temporal_advanced.png")
print("    - STEP9_ENHANCED_4_consensus_correlation.png")
print("    - STEP9_ENHANCED_5_executive_dashboard.png ⭐ RECOMMENDED FOR PDF")
print("    - STEP9_ENHANCED_6_state_profile_cards.png")
print("    - STEP9_ENHANCED_7_anomaly_patterns.png")
print("    - STEP9_ENHANCED_8_comparison_matrix.png")
print()

print("💡 KEY INSIGHTS FOR HACKATHON REPORT")
print("=" * 100)
print()
print("1. MULTI-TECHNIQUE VALIDATION:")
print(f"   - {len(consensus_anomalies)} states flagged by 2+ techniques (high confidence)")
print(f"   - Reduces false positives through consensus approach")
print()
print("2. SOCIAL VULNERABILITY INDICATORS:")
print(f"   - States with low bio update rates risk service exclusion")
print(f"   - Temporal volatility indicates capacity planning needs")
print()
print("3. ACTIONABLE RECOMMENDATIONS:")
print("   - Investigate consensus anomaly states immediately")
print("   - Deploy targeted campaigns in low-update regions")
print("   - Allocate resources based on temporal patterns")
print()

print("✅ STEP 9 COMPLETE - ANOMALY DETECTION FRAMEWORK READY FOR HACKATHON!")
print("=" * 100)
print()
print("📖 For detailed methodology and findings, see: STEP9_COMPLETE_SUMMARY.md")
print("🎨 All visualizations are at 300 DPI, ready for PDF inclusion")
print()
print("Next: Proceed to Step 10 - Time Series Forecasting & Prediction Models")
print("=" * 100)
