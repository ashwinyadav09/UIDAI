"""
PHASE 3 - STEP 4: AI-Driven Anomaly Detection
==============================================
Detects irregular or anomalous age-specific patterns using machine learning

Aligns with problem statement:
- "AI-driven anomaly detection in age-specific biometric and demographic updates"
- "detect irregular or anomalous age-specific patterns"

Author: UIDAI Hackathon Project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 8)

print("=" * 80)
print("PHASE 3 - STEP 4: AI-DRIVEN ANOMALY DETECTION")
print("=" * 80)
print()
print("Using machine learning algorithms:")
print("  1. Isolation Forest - Detects outliers in multi-dimensional space")
print("  2. Z-Score Method - Identifies statistical outliers")
print("  3. DBSCAN Clustering - Finds density-based anomalies")
print()

# ============================================================================
# STEP 1: LOAD CLEANED DATA
# ============================================================================
print("📂 Loading cleaned data...")
try:
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../data/processed/cleaned_biometric.csv')
    demographic = pd.read_csv('../data/processed/cleaned_demographic.csv')
    print("✓ All datasets loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
    print(f"  - Demographic: {len(demographic):,} rows")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("Please run STEP2_FINAL_intelligent_cleaning.py first!")
    exit()

print()

# ============================================================================
# STEP 2: PREPARE DATA FOR ANOMALY DETECTION
# ============================================================================
print("🔧 Preparing data for anomaly detection...")

# Aggregate data by state
print("  - Aggregating enrolment data...")
enrol_agg = enrolment.groupby('state').agg({
    'registrations_0_to_5': 'sum',
    'registrations_5_to_17': 'sum',
    'registrations_18_and_above': 'sum',
    'total_enrolments': 'sum'
}).reset_index()

print("  - Aggregating biometric update data...")
bio_agg = biometric.groupby('state').agg({
    'biometric_updates_5_to_17': 'sum',
    'biometric_updates_18_and_above': 'sum',
    'total_bio_updates': 'sum'
}).reset_index()

print("  - Aggregating demographic update data...")
demo_agg = demographic.groupby('state').agg({
    'demographic_updates_5_to_17': 'sum',
    'demographic_updates_18_and_above': 'sum',
    'total_demo_updates': 'sum'
}).reset_index()

# Merge all datasets
print("  - Merging datasets...")
anomaly_data = enrol_agg.merge(bio_agg, on='state', how='outer').merge(demo_agg, on='state', how='outer').fillna(0)

print("✓ Data prepared for analysis")
print()

# ============================================================================
# STEP 3: CALCULATE FEATURE RATIOS
# ============================================================================
print("📊 Calculating age-specific feature ratios...")

# Child-to-adult ratios
anomaly_data['child_adult_enrol_ratio'] = (
    (anomaly_data['registrations_0_to_5'] + anomaly_data['registrations_5_to_17']) / 
    anomaly_data['registrations_18_and_above']
).replace([np.inf, -np.inf], 0)

anomaly_data['child_bio_ratio'] = (
    anomaly_data['biometric_updates_5_to_17'] / 
    anomaly_data['biometric_updates_18_and_above']
).replace([np.inf, -np.inf], 0)

anomaly_data['child_demo_ratio'] = (
    anomaly_data['demographic_updates_5_to_17'] / 
    anomaly_data['demographic_updates_18_and_above']
).replace([np.inf, -np.inf], 0)

# Update intensity ratios
anomaly_data['bio_intensity'] = (
    anomaly_data['total_bio_updates'] / anomaly_data['total_enrolments']
).replace([np.inf, -np.inf], 0)

anomaly_data['demo_intensity'] = (
    anomaly_data['total_demo_updates'] / anomaly_data['total_enrolments']
).replace([np.inf, -np.inf], 0)

# Age-specific proportions
anomaly_data['child_0_5_pct'] = (
    anomaly_data['registrations_0_to_5'] / anomaly_data['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

anomaly_data['child_5_17_pct'] = (
    anomaly_data['registrations_5_to_17'] / anomaly_data['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

print("✓ Feature ratios calculated")
print()

# ============================================================================
# STEP 4: METHOD 1 - ISOLATION FOREST
# ============================================================================
print("🤖 METHOD 1: Isolation Forest Anomaly Detection")
print("   (ML algorithm designed specifically for outlier detection)")
print()

# Select features for anomaly detection
features = [
    'child_adult_enrol_ratio',
    'child_bio_ratio',
    'child_demo_ratio',
    'bio_intensity',
    'demo_intensity',
    'child_0_5_pct',
    'child_5_17_pct'
]

# Prepare data
X = anomaly_data[features].fillna(0).replace([np.inf, -np.inf], 0)

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Isolation Forest
print("  - Training Isolation Forest model...")
iso_forest = IsolationForest(
    contamination=0.15,  # Expect ~15% anomalies
    random_state=42,
    n_estimators=100
)
anomaly_data['iso_anomaly'] = iso_forest.fit_predict(X_scaled)
anomaly_data['iso_score'] = iso_forest.score_samples(X_scaled)

# Convert predictions: -1 = anomaly, 1 = normal
anomaly_data['iso_is_anomaly'] = anomaly_data['iso_anomaly'] == -1

iso_anomalies = anomaly_data[anomaly_data['iso_is_anomaly']].copy()
print(f"✓ Isolation Forest detected: {len(iso_anomalies)} anomalous states")
if len(iso_anomalies) > 0:
    print("\n  Anomalous states (ranked by anomaly score):")
    iso_anomalies_sorted = iso_anomalies.sort_values('iso_score').head(10)
    for idx, row in iso_anomalies_sorted.iterrows():
        print(f"    {row['state']:40s} → Score: {row['iso_score']:.3f}")
print()

# ============================================================================
# STEP 5: METHOD 2 - Z-SCORE STATISTICAL METHOD
# ============================================================================
print("📊 METHOD 2: Z-Score Statistical Outlier Detection")
print("   (Identifies values >3 standard deviations from mean)")
print()

def detect_zscore_anomalies(df, columns, threshold=3):
    """Detect anomalies using Z-score method"""
    anomaly_flags = pd.DataFrame()
    
    for col in columns:
        mean = df[col].mean()
        std = df[col].std()
        z_scores = np.abs((df[col] - mean) / std)
        anomaly_flags[f'{col}_anomaly'] = z_scores > threshold
    
    # Mark as anomaly if ANY feature is anomalous
    df['zscore_anomaly_count'] = anomaly_flags.sum(axis=1)
    df['zscore_is_anomaly'] = df['zscore_anomaly_count'] > 0
    
    return df

anomaly_data = detect_zscore_anomalies(anomaly_data, features)

zscore_anomalies = anomaly_data[anomaly_data['zscore_is_anomaly']].copy()
print(f"✓ Z-Score method detected: {len(zscore_anomalies)} anomalous states")
if len(zscore_anomalies) > 0:
    print("\n  Anomalous states (by number of anomalous features):")
    zscore_sorted = zscore_anomalies.sort_values('zscore_anomaly_count', ascending=False).head(10)
    for idx, row in zscore_sorted.iterrows():
        print(f"    {row['state']:40s} → {int(row['zscore_anomaly_count'])} anomalous features")
print()

# ============================================================================
# STEP 6: METHOD 3 - DBSCAN CLUSTERING
# ============================================================================
print("🎯 METHOD 3: DBSCAN Density-Based Clustering")
print("   (Identifies points in low-density regions as anomalies)")
print()

# Apply DBSCAN
dbscan = DBSCAN(eps=1.5, min_samples=3)
anomaly_data['dbscan_cluster'] = dbscan.fit_predict(X_scaled)

# Cluster -1 indicates anomalies (noise points)
anomaly_data['dbscan_is_anomaly'] = anomaly_data['dbscan_cluster'] == -1

dbscan_anomalies = anomaly_data[anomaly_data['dbscan_is_anomaly']].copy()
print(f"✓ DBSCAN detected: {len(dbscan_anomalies)} anomalous states (noise points)")
if len(dbscan_anomalies) > 0:
    print("\n  Anomalous states:")
    for idx, row in dbscan_anomalies.head(10).iterrows():
        print(f"    {row['state']}")
print()

# ============================================================================
# STEP 7: CONSENSUS ANOMALIES
# ============================================================================
print("🎯 CONSENSUS ANALYSIS - Combining all methods...")
print("   (States flagged by 2+ methods are HIGH PRIORITY)")
print()

anomaly_data['anomaly_method_count'] = (
    anomaly_data['iso_is_anomaly'].astype(int) +
    anomaly_data['zscore_is_anomaly'].astype(int) +
    anomaly_data['dbscan_is_anomaly'].astype(int)
)

anomaly_data['consensus_anomaly'] = anomaly_data['anomaly_method_count'] >= 2

consensus_anomalies = anomaly_data[anomaly_data['consensus_anomaly']].copy()
print(f"✅ CONSENSUS ANOMALIES: {len(consensus_anomalies)} states")
if len(consensus_anomalies) > 0:
    print("\n  HIGH PRIORITY anomalous states (flagged by 2+ methods):")
    consensus_sorted = consensus_anomalies.sort_values('anomaly_method_count', ascending=False)
    for idx, row in consensus_sorted.iterrows():
        methods = row['anomaly_method_count']
        print(f"    {row['state']:40s} → Flagged by {methods}/3 methods")
print()

# ============================================================================
# STEP 8: IDENTIFY SPECIFIC ANOMALY TYPES
# ============================================================================
print("🔍 Identifying specific anomaly patterns...")

def identify_anomaly_type(row):
    """Identify what type of anomaly each state exhibits"""
    patterns = []
    
    # Low child enrolment
    if row['child_0_5_pct'] < 5:
        patterns.append("Very low early-child enrolment")
    
    # High child-adult ratio
    if row['child_adult_enrol_ratio'] > 1.5:
        patterns.append("Unusually high child-adult ratio")
    
    # Low biometric compliance
    if row['child_bio_ratio'] < 0.3:
        patterns.append("Low child biometric updates")
    
    # High update intensity
    if row['bio_intensity'] > 50:
        patterns.append("Abnormally high update activity")
    
    # Low update intensity
    if row['bio_intensity'] < 1:
        patterns.append("Abnormally low update activity")
    
    return "; ".join(patterns) if patterns else "Other irregular pattern"

anomaly_data['anomaly_patterns'] = anomaly_data.apply(identify_anomaly_type, axis=1)

print("✓ Anomaly patterns identified")
print()

# ============================================================================
# STEP 9: SAVE RESULTS
# ============================================================================
print("💾 Saving anomaly detection results...")

anomaly_data.to_csv('../results/anomaly_detection_complete.csv', index=False)
iso_anomalies.to_csv('../results/anomalies_isolation_forest.csv', index=False)
zscore_anomalies.to_csv('../results/anomalies_zscore.csv', index=False)
dbscan_anomalies.to_csv('../results/anomalies_dbscan.csv', index=False)
consensus_anomalies.to_csv('../results/consensus_anomalies_HIGH_PRIORITY.csv', index=False)

print("✓ Results saved to results/ folder")
print()

# ============================================================================
# STEP 10: CREATE VISUALIZATIONS
# ============================================================================
print("📊 Creating anomaly detection visualizations...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

fig.suptitle('AI-Driven Anomaly Detection in Aadhaar Updates', 
             fontsize=18, fontweight='bold')

# 1. Method comparison
ax1 = fig.add_subplot(gs[0, :])
method_counts = {
    'Isolation Forest': len(iso_anomalies),
    'Z-Score': len(zscore_anomalies),
    'DBSCAN': len(dbscan_anomalies),
    'Consensus (2+)': len(consensus_anomalies)
}
colors_methods = ['steelblue', 'coral', 'lightgreen', 'darkred']
bars = ax1.bar(method_counts.keys(), method_counts.values(), color=colors_methods)
ax1.set_ylabel('Number of Anomalous States', fontweight='bold')
ax1.set_title('Anomaly Detection Methods Comparison', fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Add values
for bar, value in zip(bars, method_counts.values()):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(value)}', ha='center', va='bottom', fontweight='bold', fontsize=12)

# 2. Isolation Forest scatter
ax2 = fig.add_subplot(gs[1, 0])
colors_iso = ['red' if x else 'blue' for x in anomaly_data['iso_is_anomaly']]
ax2.scatter(anomaly_data['child_0_5_pct'], anomaly_data['bio_intensity'],
           c=colors_iso, alpha=0.6, edgecolors='black', s=80)
ax2.set_xlabel('Child (0-5) Enrolment %', fontweight='bold')
ax2.set_ylabel('Biometric Update Intensity', fontweight='bold')
ax2.set_title('Isolation Forest Detection', fontweight='bold')
ax2.grid(alpha=0.3)

# 3. Z-Score scatter
ax3 = fig.add_subplot(gs[1, 1])
colors_z = ['red' if x else 'blue' for x in anomaly_data['zscore_is_anomaly']]
ax3.scatter(anomaly_data['child_5_17_pct'], anomaly_data['demo_intensity'],
           c=colors_z, alpha=0.6, edgecolors='black', s=80)
ax3.set_xlabel('Child (5-17) Enrolment %', fontweight='bold')
ax3.set_ylabel('Demographic Update Intensity', fontweight='bold')
ax3.set_title('Z-Score Detection', fontweight='bold')
ax3.grid(alpha=0.3)

# 4. DBSCAN clusters
ax4 = fig.add_subplot(gs[1, 2])
unique_clusters = anomaly_data['dbscan_cluster'].unique()
colors_db = plt.cm.rainbow(np.linspace(0, 1, len(unique_clusters)))
for cluster, color in zip(unique_clusters, colors_db):
    if cluster == -1:
        color = 'red'
        label = 'Anomaly'
    else:
        label = f'Cluster {cluster}'
    
    mask = anomaly_data['dbscan_cluster'] == cluster
    ax4.scatter(anomaly_data.loc[mask, 'child_adult_enrol_ratio'],
               anomaly_data.loc[mask, 'child_bio_ratio'],
               c=[color], label=label, alpha=0.6, edgecolors='black', s=80)

ax4.set_xlabel('Child-Adult Enrolment Ratio', fontweight='bold')
ax4.set_ylabel('Child-Adult Bio Update Ratio', fontweight='bold')
ax4.set_title('DBSCAN Clustering', fontweight='bold')
ax4.legend(fontsize=8)
ax4.grid(alpha=0.3)

# 5. Consensus anomaly count
ax5 = fig.add_subplot(gs[2, 0])
count_dist = anomaly_data['anomaly_method_count'].value_counts().sort_index()
colors_consensus = ['green', 'yellow', 'orange', 'red']
ax5.bar(count_dist.index, count_dist.values, color=colors_consensus[:len(count_dist)])
ax5.set_xlabel('Number of Methods Flagging Anomaly', fontweight='bold')
ax5.set_ylabel('Number of States', fontweight='bold')
ax5.set_title('Consensus Anomaly Distribution', fontweight='bold')
ax5.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(count_dist.values):
    ax5.text(count_dist.index[i], v, str(v), ha='center', va='bottom', fontweight='bold')

# 6. Anomaly severity (consensus states)
ax6 = fig.add_subplot(gs[2, 1:])
if len(consensus_anomalies) > 0:
    consensus_plot = consensus_anomalies.nlargest(15, 'anomaly_method_count')
    colors_severity = ['darkred' if x == 3 else 'orange' for x in consensus_plot['anomaly_method_count']]
    ax6.barh(range(len(consensus_plot)), consensus_plot['anomaly_method_count'], color=colors_severity)
    ax6.set_yticks(range(len(consensus_plot)))
    ax6.set_yticklabels(consensus_plot['state'], fontsize=9)
    ax6.set_xlabel('Number of Methods Detecting Anomaly', fontweight='bold')
    ax6.set_title('Top 15 Consensus Anomalies (HIGH PRIORITY)', fontweight='bold')
    ax6.grid(axis='x', alpha=0.3)
    
    # Add values
    for i, v in enumerate(consensus_plot['anomaly_method_count']):
        ax6.text(v, i, f' {int(v)}/3', va='center', fontweight='bold')
else:
    ax6.text(0.5, 0.5, 'No Consensus Anomalies', ha='center', va='center',
            transform=ax6.transAxes, fontsize=14)
    ax6.axis('off')

plt.savefig('../visualizations/PHASE3_04_anomaly_detection.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: PHASE3_04_anomaly_detection.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ PHASE 3 - STEP 4 COMPLETE!")
print("=" * 80)
print()
print("📊 WHAT WAS DONE:")
print("  ✓ Prepared age-specific feature ratios")
print("  ✓ Applied Isolation Forest ML algorithm")
print("  ✓ Applied Z-Score statistical method")
print("  ✓ Applied DBSCAN density clustering")
print("  ✓ Identified consensus anomalies (2+ methods)")
print("  ✓ Categorized specific anomaly patterns")
print("  ✓ Created comprehensive visualizations")
print()
print("📁 FILES CREATED:")
print("  ✓ results/anomaly_detection_complete.csv")
print("  ✓ results/anomalies_isolation_forest.csv")
print("  ✓ results/anomalies_zscore.csv")
print("  ✓ results/anomalies_dbscan.csv")
print("  ✓ results/consensus_anomalies_HIGH_PRIORITY.csv")
print("  ✓ visualizations/PHASE3_04_anomaly_detection.png")
print()
print("🎯 KEY FINDINGS:")
print(f"  - Isolation Forest anomalies: {len(iso_anomalies)}")
print(f"  - Z-Score anomalies: {len(zscore_anomalies)}")
print(f"  - DBSCAN anomalies: {len(dbscan_anomalies)}")
print(f"  - Consensus anomalies (HIGH PRIORITY): {len(consensus_anomalies)}")
print()
print("🎉 PHASE 3 COMPLETE!")
print("All core analyses finished. Ready to create final report!")
print("=" * 80)
