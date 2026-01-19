"""
PHASE 3 - STEP 9: Multi-Technique Anomaly Detection Framework
===============================================================
Professional ML-based anomaly detection using ensemble approach

Implements:
1. Isolation Forest - Multivariate anomaly detection
2. Z-Score Method - Statistical outlier detection (3-sigma)
3. Time-Series Analysis - Temporal pattern anomalies
4. Consensus Detection - High-confidence anomalies

Author: Professional ML/Data Science Engineer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 12)

print("=" * 80)
print("PHASE 3 - STEP 9: MULTI-TECHNIQUE ANOMALY DETECTION FRAMEWORK")
print("=" * 80)
print()
print("🤖 ML Techniques:")
print("  1. Isolation Forest - Multivariate anomaly detection")
print("  2. Z-Score Method - Statistical outlier detection (3-sigma)")
print("  3. Time-Series Analysis - Temporal pattern anomalies")
print("  4. Consensus Detection - High-confidence anomalies")
print()

# ============================================================================
# LOAD ALL CLEANED DATA
# ============================================================================
print("📂 Loading cleaned data...")
try:
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../data/processed/cleaned_biometric.csv')
    demographic = pd.read_csv('../data/processed/cleaned_demographic.csv')
    
    # Convert dates
    enrolment['date'] = pd.to_datetime(enrolment['date'])
    biometric['date'] = pd.to_datetime(biometric['date'])
    demographic['date'] = pd.to_datetime(demographic['date'])
    
    print("✓ Data loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
    print(f"  - Demographic: {len(demographic):,} rows")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

print()

# ============================================================================
# PREPARE FEATURE MATRIX FOR ANOMALY DETECTION
# ============================================================================
print("📊 Step 9.1: Preparing feature matrix for anomaly detection...")

# Aggregate by state for comprehensive features
enrol_features = enrolment.groupby('state').agg({
    'age_0_5': 'sum',
    'age_5_17': 'sum',
    'age_18_greater': 'sum',
    'total_enrolments': 'sum'
}).reset_index()

bio_features = biometric.groupby('state').agg({
    'bio_age_5_17': 'sum',
    'bio_age_17_': 'sum',  # Assuming this is bio_age_17_greater
    'total_bio_updates': 'sum'
}).reset_index()

# Check what columns exist in demographic
demo_cols_to_agg = {'total_demo_updates': 'sum'}
if 'demo_age_5_17' in demographic.columns:
    demo_cols_to_agg['demo_age_5_17'] = 'sum'
if 'demo_age_17_greater' in demographic.columns:
    demo_cols_to_agg['demo_age_17_greater'] = 'sum'

demo_features = demographic.groupby('state').agg(demo_cols_to_agg).reset_index()


# Merge all features
features_df = enrol_features.merge(bio_features, on='state', how='outer')
features_df = features_df.merge(demo_features, on='state', how='outer')
features_df = features_df.fillna(0)

# Calculate derived features
features_df['bio_update_rate'] = (features_df['total_bio_updates'] / features_df['total_enrolments'] * 100).replace([np.inf, -np.inf], 0)
features_df['demo_update_rate'] = (features_df['total_demo_updates'] / features_df['total_enrolments'] * 100).replace([np.inf, -np.inf], 0)
features_df['child_enrol_pct'] = (features_df['age_0_5'] / features_df['total_enrolments'] * 100).replace([np.inf, -np.inf], 0)
features_df['youth_enrol_pct'] = (features_df['age_5_17'] / features_df['total_enrolments'] * 100).replace([np.inf, -np.inf], 0)
features_df['adult_enrol_pct'] = (features_df['age_18_greater'] / features_df['total_enrolments'] * 100).replace([np.inf, -np.inf], 0)

print(f"✓ Feature matrix prepared: {len(features_df)} states, {len(features_df.columns)-1} features")
print()

# ============================================================================
# TECHNIQUE 1: ISOLATION FOREST (Multivariate Anomaly Detection)
# ============================================================================
print("🌲 Step 9.2: Isolation Forest - Multivariate Anomaly Detection...")
print("   Detecting complex patterns across multiple features")
print()

# Select features for Isolation Forest
feature_cols = ['total_enrolments', 'bio_update_rate', 'demo_update_rate', 
                'child_enrol_pct', 'youth_enrol_pct', 'adult_enrol_pct']

X = features_df[feature_cols].values

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Isolation Forest
contamination = 0.05  # Expect 5% anomalies
iso_forest = IsolationForest(
    contamination=contamination,
    random_state=42,
    n_estimators=100,
    max_samples='auto'
)

# Predict anomalies (-1 = anomaly, 1 = normal)
iso_predictions = iso_forest.fit_predict(X_scaled)
iso_scores = iso_forest.score_samples(X_scaled)

# Add to dataframe
features_df['iso_forest_anomaly'] = iso_predictions == -1
features_df['iso_forest_score'] = iso_scores

iso_anomalies = features_df[features_df['iso_forest_anomaly']].copy()

print(f"✓ Isolation Forest Results:")
print(f"  - Anomalies detected: {len(iso_anomalies)} states ({len(iso_anomalies)/len(features_df)*100:.1f}%)")
print(f"  - Contamination parameter: {contamination*100}%")
print()

if len(iso_anomalies) > 0:
    print("  🚨 States flagged as anomalies:")
    for idx, row in iso_anomalies.iterrows():
        print(f"    {row['state']:40s} → Score: {row['iso_forest_score']:.3f}")
print()

# ============================================================================
# TECHNIQUE 2: Z-SCORE METHOD (Statistical Outlier Detection)
# ============================================================================
print("📏 Step 9.3: Z-Score Method - Statistical Outlier Detection...")
print("   Using 3-sigma threshold for individual metrics")
print()

# Calculate Z-scores for key metrics
threshold = 3  # 3-sigma threshold

features_df['bio_rate_zscore'] = np.abs(stats.zscore(features_df['bio_update_rate']))
features_df['demo_rate_zscore'] = np.abs(stats.zscore(features_df['demo_update_rate']))
features_df['child_pct_zscore'] = np.abs(stats.zscore(features_df['child_enrol_pct']))
features_df['enrol_zscore'] = np.abs(stats.zscore(features_df['total_enrolments']))

# Flag outliers (any metric > 3 sigma)
features_df['zscore_anomaly'] = (
    (features_df['bio_rate_zscore'] > threshold) |
    (features_df['demo_rate_zscore'] > threshold) |
    (features_df['child_pct_zscore'] > threshold) |
    (features_df['enrol_zscore'] > threshold)
)

zscore_anomalies = features_df[features_df['zscore_anomaly']].copy()

print(f"✓ Z-Score Results:")
print(f"  - Outliers detected: {len(zscore_anomalies)} states ({len(zscore_anomalies)/len(features_df)*100:.1f}%)")
print(f"  - Threshold: {threshold}-sigma")
print()

if len(zscore_anomalies) > 0:
    print("  🚨 States flagged as outliers:")
    for idx, row in zscore_anomalies.iterrows():
        reasons = []
        if row['bio_rate_zscore'] > threshold:
            reasons.append(f"Bio rate: {row['bio_rate_zscore']:.1f}σ")
        if row['demo_rate_zscore'] > threshold:
            reasons.append(f"Demo rate: {row['demo_rate_zscore']:.1f}σ")
        if row['child_pct_zscore'] > threshold:
            reasons.append(f"Child %: {row['child_pct_zscore']:.1f}σ")
        if row['enrol_zscore'] > threshold:
            reasons.append(f"Enrol: {row['enrol_zscore']:.1f}σ")
        print(f"    {row['state']:40s} → {', '.join(reasons)}")
print()

# ============================================================================
# TECHNIQUE 3: TIME-SERIES ANALYSIS (Temporal Anomalies)
# ============================================================================
print("📈 Step 9.4: Time-Series Analysis - Temporal Pattern Anomalies...")
print("   Detecting sudden spikes/drops (>50% month-over-month change)")
print()

# Analyze month-over-month changes
enrolment['year_month'] = enrolment['date'].dt.to_period('M')
monthly_enrol = enrolment.groupby(['state', 'year_month'])['total_enrolments'].sum().reset_index()
monthly_enrol = monthly_enrol.sort_values(['state', 'year_month'])

# Calculate month-over-month change
monthly_enrol['mom_change'] = monthly_enrol.groupby('state')['total_enrolments'].pct_change() * 100

# Flag sudden changes (>50% increase or decrease)
spike_threshold = 50
monthly_enrol['temporal_anomaly'] = np.abs(monthly_enrol['mom_change']) > spike_threshold

temporal_anomalies = monthly_enrol[monthly_enrol['temporal_anomaly']].copy()

# Aggregate by state
states_with_temporal = temporal_anomalies['state'].unique()
features_df['temporal_anomaly'] = features_df['state'].isin(states_with_temporal)

print(f"✓ Time-Series Results:")
print(f"  - States with temporal anomalies: {len(states_with_temporal)} states")
print(f"  - Total temporal anomalies: {len(temporal_anomalies)} instances")
print(f"  - Threshold: ±{spike_threshold}% month-over-month")
print()

if len(temporal_anomalies) > 0:
    print("  🚨 Top 10 temporal anomalies:")
    top_temporal = temporal_anomalies.nlargest(10, 'mom_change', keep='all')
    for idx, row in top_temporal.head(10).iterrows():
        print(f"    {row['state']:40s} → {row['year_month']}: {row['mom_change']:+.1f}% change")
print()

# ============================================================================
# STEP 9.5: CONSENSUS ANOMALY DETECTION
# ============================================================================
print("🎯 Step 9.5: Consensus Anomaly Detection...")
print("   Identifying high-confidence anomalies flagged by multiple techniques")
print()

# Count how many techniques flagged each state
features_df['anomaly_count'] = (
    features_df['iso_forest_anomaly'].astype(int) +
    features_df['zscore_anomaly'].astype(int) +
    features_df['temporal_anomaly'].astype(int)
)

# Consensus: flagged by 2+ techniques
features_df['consensus_anomaly'] = features_df['anomaly_count'] >= 2

consensus_anomalies = features_df[features_df['consensus_anomaly']].copy()

print(f"✓ Consensus Results:")
print(f"  - High-confidence anomalies: {len(consensus_anomalies)} states")
print(f"  - Criteria: Flagged by 2+ techniques")
print()

if len(consensus_anomalies) > 0:
    print("  🔴 CONSENSUS ANOMALIES (High Priority):")
    for idx, row in consensus_anomalies.iterrows():
        techniques = []
        if row['iso_forest_anomaly']:
            techniques.append("Isolation Forest")
        if row['zscore_anomaly']:
            techniques.append("Z-Score")
        if row['temporal_anomaly']:
            techniques.append("Time-Series")
        print(f"    {row['state']:40s} → {row['anomaly_count']}/3 techniques: {', '.join(techniques)}")
print()

# ============================================================================
# STEP 9.6: ANOMALY CHARACTERIZATION
# ============================================================================
print("🔍 Step 9.6: Characterizing detected anomalies...")

def characterize_anomaly(row):
    """Characterize the type of anomaly"""
    reasons = []
    
    if row['bio_update_rate'] > features_df['bio_update_rate'].quantile(0.95):
        reasons.append("Extremely high bio update rate")
    elif row['bio_update_rate'] < features_df['bio_update_rate'].quantile(0.05):
        reasons.append("Extremely low bio update rate")
    
    if row['demo_update_rate'] > features_df['demo_update_rate'].quantile(0.95):
        reasons.append("Extremely high demo update rate")
    elif row['demo_update_rate'] < features_df['demo_update_rate'].quantile(0.05):
        reasons.append("Extremely low demo update rate")
    
    if row['child_enrol_pct'] > features_df['child_enrol_pct'].quantile(0.95):
        reasons.append("Unusually high child enrolment %")
    elif row['child_enrol_pct'] < features_df['child_enrol_pct'].quantile(0.05):
        reasons.append("Unusually low child enrolment %")
    
    if row['total_enrolments'] > features_df['total_enrolments'].quantile(0.95):
        reasons.append("Very large population")
    elif row['total_enrolments'] < features_df['total_enrolments'].quantile(0.05):
        reasons.append("Very small population")
    
    return "; ".join(reasons) if reasons else "Complex multivariate pattern"

features_df['anomaly_characterization'] = features_df.apply(characterize_anomaly, axis=1)

print("✓ Anomaly characterization complete")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("💾 Saving anomaly detection results...")

features_df.to_csv('../results/STEP9_anomaly_detection_complete.csv', index=False)
iso_anomalies.to_csv('../results/STEP9_isolation_forest_anomalies.csv', index=False)
zscore_anomalies.to_csv('../results/STEP9_zscore_anomalies.csv', index=False)
temporal_anomalies.to_csv('../results/STEP9_temporal_anomalies.csv', index=False)
consensus_anomalies.to_csv('../results/STEP9_consensus_anomalies_HIGH_PRIORITY.csv', index=False)

print("✓ Results saved:")
print("  - STEP9_anomaly_detection_complete.csv")
print("  - STEP9_isolation_forest_anomalies.csv")
print("  - STEP9_zscore_anomalies.csv")
print("  - STEP9_temporal_anomalies.csv")
print("  - STEP9_consensus_anomalies_HIGH_PRIORITY.csv")
print()

# ============================================================================
# CREATE VISUALIZATIONS
# ============================================================================
print("🎨 Creating anomaly detection visualizations...")

fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

fig.suptitle('Multi-Technique Anomaly Detection Framework - Comprehensive Analysis', 
             fontsize=18, fontweight='bold')

# Chart 1: Isolation Forest Scores
ax1 = fig.add_subplot(gs[0, :2])
sorted_df = features_df.sort_values('iso_forest_score')
colors = ['red' if x else 'steelblue' for x in sorted_df['iso_forest_anomaly']]
ax1.barh(range(len(sorted_df)), sorted_df['iso_forest_score'], color=colors, alpha=0.7)
ax1.set_yticks(range(len(sorted_df)))
ax1.set_yticklabels(sorted_df['state'], fontsize=7)
ax1.set_xlabel('Isolation Forest Score (lower = more anomalous)', fontweight='bold')
ax1.set_title('Isolation Forest - Anomaly Scores by State', fontweight='bold', fontsize=12)
ax1.axvline(sorted_df[sorted_df['iso_forest_anomaly']]['iso_forest_score'].max(), 
           color='orange', linestyle='--', linewidth=2, label='Anomaly Threshold')
ax1.legend()
ax1.grid(axis='x', alpha=0.3)

# Chart 2: Technique Comparison
ax2 = fig.add_subplot(gs[0, 2])
technique_counts = {
    'Isolation\nForest': len(iso_anomalies),
    'Z-Score\nOutliers': len(zscore_anomalies),
    'Temporal\nAnomalies': len(states_with_temporal),
    'Consensus\n(2+ methods)': len(consensus_anomalies)
}
colors_tech = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
bars = ax2.bar(range(len(technique_counts)), technique_counts.values(), color=colors_tech)
ax2.set_xticks(range(len(technique_counts)))
ax2.set_xticklabels(technique_counts.keys(), fontsize=9, rotation=0)
ax2.set_ylabel('Number of States', fontweight='bold')
ax2.set_title('Anomaly Detection by Technique', fontweight='bold', fontsize=12)
ax2.grid(axis='y', alpha=0.3)
for i, v in enumerate(technique_counts.values()):
    ax2.text(i, v, str(v), ha='center', va='bottom', fontweight='bold', fontsize=11)

# Chart 3: Z-Score Heatmap
ax3 = fig.add_subplot(gs[1, :])
zscore_cols = ['bio_rate_zscore', 'demo_rate_zscore', 'child_pct_zscore', 'enrol_zscore']
top_20_zscore = features_df.nlargest(20, 'bio_rate_zscore')
heatmap_data = top_20_zscore[zscore_cols].T
sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd', 
           xticklabels=top_20_zscore['state'], yticklabels=['Bio Rate', 'Demo Rate', 'Child %', 'Enrolment'],
           cbar_kws={'label': 'Z-Score (σ)'}, ax=ax3, linewidths=0.5)
ax3.set_title('Z-Score Heatmap - Top 20 States by Bio Update Rate Z-Score', fontweight='bold', fontsize=12)
ax3.set_xlabel('State', fontweight='bold')
plt.setp(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=8)

# Chart 4: Temporal Anomalies Timeline (Improved)
ax4 = fig.add_subplot(gs[2, :2])
if len(temporal_anomalies) > 0:
    # Limit to top 5 states for clarity
    top_states_temporal = temporal_anomalies['state'].value_counts().head(5).index
    
    # Use distinct colors and markers
    colors_palette = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    markers = ['o', 's', '^', 'D', 'v']
    
    for idx, state in enumerate(top_states_temporal):
        state_data = temporal_anomalies[temporal_anomalies['state'] == state]
        ax4.scatter([str(x) for x in state_data['year_month']], 
                   state_data['mom_change'], 
                   label=state, 
                   s=150,  # Larger markers
                   alpha=0.7, 
                   color=colors_palette[idx % len(colors_palette)],
                   marker=markers[idx % len(markers)],
                   edgecolors='black',  # Add edge for better visibility
                   linewidths=1.5)
    
    # Add threshold lines (without labels to avoid legend clutter)
    ax4.axhline(spike_threshold, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax4.axhline(-spike_threshold, color='red', linestyle='--', linewidth=2, alpha=0.7)
    
    # Add threshold annotation instead of legend entry
    ax4.text(0.02, 0.98, f'Threshold: ±{spike_threshold}%', 
            transform=ax4.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax4.set_xlabel('Month', fontweight='bold')
    ax4.set_ylabel('Month-over-Month Change (%)', fontweight='bold')
    ax4.set_title('Temporal Anomalies - Top 5 States with Most Spikes/Drops', fontweight='bold', fontsize=12)
    
    # Place legend below the chart to avoid collision
    ax4.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
              ncol=5, fontsize=9, frameon=True, shadow=True)
    ax4.grid(alpha=0.3)
    plt.setp(ax4.get_xticklabels(), rotation=45, ha='right', fontsize=7)
else:
    ax4.text(0.5, 0.5, 'No temporal anomalies detected', 
            ha='center', va='center', fontsize=12, transform=ax4.transAxes)

# Chart 5: Anomaly Count Distribution
ax5 = fig.add_subplot(gs[2, 2])
anomaly_dist = features_df['anomaly_count'].value_counts().sort_index()
colors_dist = ['green', 'yellow', 'orange', 'red']
bars5 = ax5.bar(anomaly_dist.index, anomaly_dist.values, 
               color=[colors_dist[i] if i < len(colors_dist) else 'darkred' for i in anomaly_dist.index],
               edgecolor='black', linewidth=1.5)
ax5.set_xlabel('Number of Techniques\nFlagging Anomaly', fontweight='bold', fontsize=10)
ax5.set_ylabel('Number of States', fontweight='bold')
ax5.set_title('Anomaly Consensus\nDistribution', fontweight='bold', fontsize=12)
ax5.set_xticks(range(4))
ax5.set_xticklabels(['0\n(Normal)', '1\n(Low)', '2\n(Medium)', '3\n(High)'], fontsize=8)
ax5.grid(axis='y', alpha=0.3)
for i, v in enumerate(anomaly_dist.values):
    ax5.text(anomaly_dist.index[i], v, str(v), ha='center', va='bottom', fontweight='bold', fontsize=12)

plt.savefig('../visualizations/STEP9_anomaly_detection_comprehensive.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: STEP9_anomaly_detection_comprehensive.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ STEP 9 COMPLETE - MULTI-TECHNIQUE ANOMALY DETECTION!")
print("=" * 80)
print()
print("📋 WHAT WAS DONE:")
print("  ✓ Isolation Forest - Multivariate anomaly detection")
print("  ✓ Z-Score Method - Statistical outlier detection (3-sigma)")
print("  ✓ Time-Series Analysis - Temporal pattern anomalies")
print("  ✓ Consensus Detection - High-confidence anomalies")
print("  ✓ Anomaly characterization and prioritization")
print()
print("📁 FILES CREATED:")
print("  ✓ results/STEP9_anomaly_detection_complete.csv")
print("  ✓ results/STEP9_isolation_forest_anomalies.csv")
print("  ✓ results/STEP9_zscore_anomalies.csv")
print("  ✓ results/STEP9_temporal_anomalies.csv")
print("  ✓ results/STEP9_consensus_anomalies_HIGH_PRIORITY.csv")
print("  ✓ visualizations/STEP9_anomaly_detection_comprehensive.png")
print()
print("📊 KEY FINDINGS:")
print(f"  - Isolation Forest anomalies: {len(iso_anomalies)} states")
print(f"  - Z-Score outliers: {len(zscore_anomalies)} states")
print(f"  - Temporal anomalies: {len(states_with_temporal)} states")
print(f"  - Consensus anomalies (HIGH PRIORITY): {len(consensus_anomalies)} states")
print(f"  - Total temporal anomaly instances: {len(temporal_anomalies)}")
print()
print("✅ ALL CORE ANALYSIS STEPS COMPLETE (Steps 6, 7, 8, 9)!")
print("   Professional ML-based analysis ready for hackathon submission!")
print("=" * 80)
