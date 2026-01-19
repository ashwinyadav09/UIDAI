"""
STEP 9 - VISUALIZATION GENERATOR: Separate Detailed Charts
===========================================================
Creates individual, high-quality visualizations for each anomaly detection technique
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("=" * 80)
print("GENERATING SEPARATE ANOMALY DETECTION VISUALIZATIONS")
print("=" * 80)
print()

# Load results
print("📂 Loading anomaly detection results...")
features_df = pd.read_csv('../results/STEP9_anomaly_detection_complete.csv')
temporal_anomalies = pd.read_csv('../results/STEP9_temporal_anomalies.csv')
iso_anomalies = pd.read_csv('../results/STEP9_isolation_forest_anomalies.csv')
zscore_anomalies = pd.read_csv('../results/STEP9_zscore_anomalies.csv')
consensus_anomalies = pd.read_csv('../results/STEP9_consensus_anomalies_HIGH_PRIORITY.csv')

print(f"✓ Data loaded successfully")
print()

# ============================================================================
# CHART 1: ISOLATION FOREST - Detailed Analysis
# ============================================================================
print("🎨 Creating Chart 1: Isolation Forest Detailed Analysis...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Isolation Forest - Multivariate Anomaly Detection', fontsize=16, fontweight='bold')

# Left: All states sorted by score
sorted_df = features_df.sort_values('iso_forest_score')
colors = ['red' if x else 'steelblue' for x in sorted_df['iso_forest_anomaly']]
ax1.barh(range(len(sorted_df)), sorted_df['iso_forest_score'], color=colors, alpha=0.7, edgecolor='black')
ax1.set_yticks(range(len(sorted_df)))
ax1.set_yticklabels(sorted_df['state'], fontsize=8)
ax1.set_xlabel('Isolation Forest Score (lower = more anomalous)', fontweight='bold', fontsize=11)
ax1.set_title('All States - Anomaly Scores', fontweight='bold', fontsize=13)
if len(iso_anomalies) > 0:
    threshold_val = sorted_df[sorted_df['iso_forest_anomaly']]['iso_forest_score'].max()
    ax1.axvline(threshold_val, color='orange', linestyle='--', linewidth=2, label=f'Anomaly Threshold: {threshold_val:.3f}')
    ax1.legend(fontsize=10)
ax1.grid(axis='x', alpha=0.3)

# Right: Feature importance for anomalies
if len(iso_anomalies) > 0:
    feature_cols = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct', 'youth_enrol_pct', 'adult_enrol_pct']
    anomaly_features = iso_anomalies[feature_cols + ['state']].set_index('state')
    
    # Normalize for comparison
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    normalized = pd.DataFrame(
        scaler.fit_transform(anomaly_features),
        columns=feature_cols,
        index=anomaly_features.index
    )
    
    normalized.T.plot(kind='bar', ax=ax2, width=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_title('Anomalous States - Feature Patterns (Normalized)', fontweight='bold', fontsize=13)
    ax2.set_xlabel('Features', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Normalized Value (Z-Score)', fontweight='bold', fontsize=11)
    ax2.legend(title='States', fontsize=9, title_fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
else:
    ax2.text(0.5, 0.5, 'No anomalies detected', ha='center', va='center', fontsize=14, transform=ax2.transAxes)

plt.tight_layout()
plt.savefig('../visualizations/STEP9_1_isolation_forest_detailed.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_1_isolation_forest_detailed.png")
plt.close()

# ============================================================================
# CHART 2: Z-SCORE - Detailed Heatmap
# ============================================================================
print("🎨 Creating Chart 2: Z-Score Statistical Outliers...")

fig, ax = plt.subplots(figsize=(16, 10))
fig.suptitle('Z-Score Method - Statistical Outlier Detection (3-Sigma Threshold)', fontsize=16, fontweight='bold')

zscore_cols = ['bio_rate_zscore', 'demo_rate_zscore', 'child_pct_zscore', 'enrol_zscore']
heatmap_data = features_df.sort_values('bio_rate_zscore', ascending=False)[zscore_cols + ['state']].head(25)
heatmap_matrix = heatmap_data.set_index('state')[zscore_cols].T

sns.heatmap(heatmap_matrix, annot=True, fmt='.2f', cmap='YlOrRd', 
           yticklabels=['Bio Update Rate', 'Demo Update Rate', 'Child Enrolment %', 'Total Enrolments'],
           cbar_kws={'label': 'Z-Score (σ)'}, ax=ax, linewidths=1, linecolor='white',
           vmin=0, vmax=5, cbar=True)

# Add threshold line
ax.axhline(y=0, color='red', linewidth=3, linestyle='--', alpha=0.7, label='3σ Threshold')
ax.axhline(y=1, color='red', linewidth=3, linestyle='--', alpha=0.7)
ax.axhline(y=2, color='red', linewidth=3, linestyle='--', alpha=0.7)
ax.axhline(y=3, color='red', linewidth=3, linestyle='--', alpha=0.7)

ax.set_title('Top 25 States by Bio Update Rate Z-Score', fontweight='bold', fontsize=13, pad=15)
ax.set_xlabel('State', fontweight='bold', fontsize=11)
ax.set_ylabel('Metric', fontweight='bold', fontsize=11)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
plt.setp(ax.get_yticklabels(), rotation=0, fontsize=10)

# Add text annotation
ax.text(0.02, 0.98, 'Red cells (>3σ) = Statistical outliers', 
       transform=ax.transAxes, fontsize=11, verticalalignment='top',
       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('../visualizations/STEP9_2_zscore_heatmap_detailed.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_2_zscore_heatmap_detailed.png")
plt.close()

# ============================================================================
# CHART 3: TEMPORAL ANOMALIES - Line Chart with Annotations
# ============================================================================
print("🎨 Creating Chart 3: Temporal Anomalies - Time Series Analysis...")

# Get top 5 states with most anomalies
top_states = temporal_anomalies['state'].value_counts().head(5).index

fig, axes = plt.subplots(5, 1, figsize=(18, 20))
fig.suptitle('Temporal Anomalies - Month-over-Month Change Analysis (Top 5 States)', 
             fontsize=16, fontweight='bold')

colors_palette = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

for idx, (state, ax) in enumerate(zip(top_states, axes)):
    state_data = temporal_anomalies[temporal_anomalies['state'] == state].copy()
    state_data = state_data.sort_values('year_month')
    
    # Convert period to string for plotting
    x_vals = [str(x) for x in state_data['year_month']]
    y_vals = state_data['mom_change'].values
    
    # Plot line chart
    ax.plot(x_vals, y_vals, marker='o', linewidth=2, markersize=8, 
           color=colors_palette[idx], label=state, alpha=0.7)
    
    # Add threshold lines
    ax.axhline(50, color='red', linestyle='--', linewidth=2, alpha=0.5, label='+50% threshold')
    ax.axhline(-50, color='red', linestyle='--', linewidth=2, alpha=0.5, label='-50% threshold')
    ax.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.3)
    
    # Annotate extreme points
    max_idx = np.argmax(np.abs(y_vals))
    ax.annotate(f'{y_vals[max_idx]:+.1f}%', 
               xy=(x_vals[max_idx], y_vals[max_idx]),
               xytext=(10, 10), textcoords='offset points',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='black'),
               fontsize=10, fontweight='bold')
    
    ax.set_title(f'{state} - {len(state_data)} Anomaly Events', fontweight='bold', fontsize=12)
    ax.set_ylabel('MoM Change (%)', fontweight='bold', fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    
    # Fill areas beyond threshold
    ax.fill_between(range(len(x_vals)), 50, 200, alpha=0.1, color='red')
    ax.fill_between(range(len(x_vals)), -50, -200, alpha=0.1, color='red')

axes[-1].set_xlabel('Month', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('../visualizations/STEP9_3_temporal_anomalies_timeseries.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_3_temporal_anomalies_timeseries.png")
plt.close()

# ============================================================================
# CHART 4: CONSENSUS ANOMALIES - Detailed Comparison
# ============================================================================
print("🎨 Creating Chart 4: Consensus Anomalies - Multi-Technique Comparison...")

fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
fig.suptitle('Consensus Anomalies - High-Confidence Detection (2+ Techniques)', 
             fontsize=16, fontweight='bold')

# Chart 4a: Technique overlap
ax1 = fig.add_subplot(gs[0, 0])
anomaly_dist = features_df['anomaly_count'].value_counts().sort_index()
colors_dist = ['green', 'yellow', 'orange', 'red']
bars = ax1.bar(anomaly_dist.index, anomaly_dist.values, 
              color=[colors_dist[i] if i < len(colors_dist) else 'darkred' for i in anomaly_dist.index],
              edgecolor='black', linewidth=2, width=0.6)
ax1.set_xlabel('Number of Techniques Flagging Anomaly', fontweight='bold', fontsize=11)
ax1.set_ylabel('Number of States', fontweight='bold', fontsize=11)
ax1.set_title('Anomaly Consensus Distribution', fontweight='bold', fontsize=13)
ax1.set_xticks(range(4))
ax1.set_xticklabels(['0\n(Normal)', '1\n(Low)', '2\n(Medium)', '3\n(High)'], fontsize=10)
ax1.grid(axis='y', alpha=0.3)
for i, v in enumerate(anomaly_dist.values):
    ax1.text(anomaly_dist.index[i], v, str(v), ha='center', va='bottom', fontweight='bold', fontsize=14)

# Chart 4b: Technique comparison
ax2 = fig.add_subplot(gs[0, 1])
technique_counts = {
    'Isolation\nForest': len(features_df[features_df['iso_forest_anomaly']]),
    'Z-Score\nOutliers': len(features_df[features_df['zscore_anomaly']]),
    'Temporal\nAnomalies': len(features_df[features_df['temporal_anomaly']]),
    'Consensus\n(2+ methods)': len(consensus_anomalies)
}
colors_tech = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
bars = ax2.bar(range(len(technique_counts)), technique_counts.values(), 
              color=colors_tech, edgecolor='black', linewidth=2, width=0.6)
ax2.set_xticks(range(len(technique_counts)))
ax2.set_xticklabels(technique_counts.keys(), fontsize=10)
ax2.set_ylabel('Number of States', fontweight='bold', fontsize=11)
ax2.set_title('Detection by Technique', fontweight='bold', fontsize=13)
ax2.grid(axis='y', alpha=0.3)
for i, v in enumerate(technique_counts.values()):
    ax2.text(i, v, str(v), ha='center', va='bottom', fontweight='bold', fontsize=14)

# Chart 4c: Consensus states details
ax3 = fig.add_subplot(gs[1, :])
if len(consensus_anomalies) > 0:
    consensus_data = consensus_anomalies[['state', 'anomaly_count', 'iso_forest_anomaly', 
                                          'zscore_anomaly', 'temporal_anomaly']].copy()
    
    # Create technique flags matrix
    technique_matrix = consensus_data[['iso_forest_anomaly', 'zscore_anomaly', 'temporal_anomaly']].T
    technique_matrix.columns = consensus_data['state']
    technique_matrix.index = ['Isolation Forest', 'Z-Score', 'Temporal']
    
    sns.heatmap(technique_matrix.astype(int), annot=True, fmt='d', cmap='RdYlGn_r', 
               cbar_kws={'label': 'Flagged (1=Yes, 0=No)'}, ax=ax3, 
               linewidths=2, linecolor='white', vmin=0, vmax=1)
    
    ax3.set_title('Consensus Anomalies - Technique Detection Matrix', fontweight='bold', fontsize=13)
    ax3.set_xlabel('State', fontweight='bold', fontsize=11)
    ax3.set_ylabel('Detection Technique', fontweight='bold', fontsize=11)
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=11)
    plt.setp(ax3.get_yticklabels(), rotation=0, fontsize=11)
    
    # Add anomaly count annotation
    for idx, (i, state) in enumerate(consensus_data['state'].items()):
        count = consensus_data.loc[i, 'anomaly_count']
        ax3.text(idx + 0.5, -0.5, f'{count}/3', ha='center', va='top', 
                fontweight='bold', fontsize=12, color='darkred')
else:
    ax3.text(0.5, 0.5, 'No consensus anomalies detected', 
            ha='center', va='center', fontsize=14, transform=ax3.transAxes)

plt.tight_layout()
plt.savefig('../visualizations/STEP9_4_consensus_anomalies_detailed.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_4_consensus_anomalies_detailed.png")
plt.close()

# ============================================================================
# CHART 5: SUMMARY DASHBOARD
# ============================================================================
print("🎨 Creating Chart 5: Summary Dashboard...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
fig.suptitle('Anomaly Detection Framework - Executive Summary Dashboard', 
             fontsize=18, fontweight='bold')

# Summary statistics
ax_summary = fig.add_subplot(gs[0, :])
ax_summary.axis('off')

summary_text = f"""
MULTI-TECHNIQUE ANOMALY DETECTION SUMMARY

Total States Analyzed: {len(features_df)}

TECHNIQUE RESULTS:
├─ Isolation Forest (Multivariate):     {len(iso_anomalies)} anomalies ({len(iso_anomalies)/len(features_df)*100:.1f}%)
├─ Z-Score Method (3-Sigma):            {len(zscore_anomalies)} outliers ({len(zscore_anomalies)/len(features_df)*100:.1f}%)
├─ Temporal Analysis (±50% MoM):        {len(features_df[features_df['temporal_anomaly']])} states with spikes/drops
└─ Consensus Detection (2+ methods):    {len(consensus_anomalies)} HIGH-PRIORITY anomalies ({len(consensus_anomalies)/len(features_df)*100:.1f}%)

CONSENSUS ANOMALIES (Requiring Investigation):
"""

if len(consensus_anomalies) > 0:
    for idx, row in consensus_anomalies.iterrows():
        techniques = []
        if row['iso_forest_anomaly']: techniques.append('IF')
        if row['zscore_anomaly']: techniques.append('ZS')
        if row['temporal_anomaly']: techniques.append('TS')
        summary_text += f"\n  • {row['state']:30s} → {row['anomaly_count']}/3 techniques [{', '.join(techniques)}]"

ax_summary.text(0.05, 0.95, summary_text, transform=ax_summary.transAxes,
               fontsize=11, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

# Mini charts
# Top anomalies by score
ax1 = fig.add_subplot(gs[1, 0])
top_iso = features_df.nsmallest(10, 'iso_forest_score')
ax1.barh(range(len(top_iso)), top_iso['iso_forest_score'], color='coral', edgecolor='black')
ax1.set_yticks(range(len(top_iso)))
ax1.set_yticklabels(top_iso['state'], fontsize=8)
ax1.set_xlabel('IF Score', fontsize=9)
ax1.set_title('Top 10 - Isolation Forest', fontweight='bold', fontsize=10)
ax1.grid(axis='x', alpha=0.3)

# Top Z-score outliers
ax2 = fig.add_subplot(gs[1, 1])
top_z = features_df.nlargest(10, 'bio_rate_zscore')
ax2.barh(range(len(top_z)), top_z['bio_rate_zscore'], color='lightcoral', edgecolor='black')
ax2.set_yticks(range(len(top_z)))
ax2.set_yticklabels(top_z['state'], fontsize=8)
ax2.set_xlabel('Z-Score (σ)', fontsize=9)
ax2.set_title('Top 10 - Z-Score Outliers', fontweight='bold', fontsize=10)
ax2.axvline(3, color='red', linestyle='--', linewidth=2)
ax2.grid(axis='x', alpha=0.3)

# Temporal frequency
ax3 = fig.add_subplot(gs[1, 2])
if len(temporal_anomalies) > 0:
    temp_counts = temporal_anomalies['state'].value_counts().head(10)
    ax3.barh(range(len(temp_counts)), temp_counts.values, color='skyblue', edgecolor='black')
    ax3.set_yticks(range(len(temp_counts)))
    ax3.set_yticklabels(temp_counts.index, fontsize=8)
    ax3.set_xlabel('Anomaly Events', fontsize=9)
    ax3.set_title('Top 10 - Temporal Anomalies', fontweight='bold', fontsize=10)
    ax3.grid(axis='x', alpha=0.3)

# Feature distributions for anomalies vs normal
ax4 = fig.add_subplot(gs[2, :])
feature_cols = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct']
x_pos = np.arange(len(feature_cols))
width = 0.35

normal_states = features_df[features_df['anomaly_count'] == 0]
anomaly_states = features_df[features_df['anomaly_count'] >= 2]

normal_means = [normal_states[col].mean() for col in feature_cols]
anomaly_means = [anomaly_states[col].mean() for col in feature_cols]

bars1 = ax4.bar(x_pos - width/2, normal_means, width, label='Normal States', 
               color='green', alpha=0.7, edgecolor='black')
bars2 = ax4.bar(x_pos + width/2, anomaly_means, width, label='Anomalous States (2+ techniques)', 
               color='red', alpha=0.7, edgecolor='black')

ax4.set_xlabel('Features', fontweight='bold', fontsize=11)
ax4.set_ylabel('Mean Value', fontweight='bold', fontsize=11)
ax4.set_title('Feature Comparison: Normal vs Anomalous States', fontweight='bold', fontsize=13)
ax4.set_xticks(x_pos)
ax4.set_xticklabels(['Bio Update Rate', 'Demo Update Rate', 'Child Enrolment %'], fontsize=10)
ax4.legend(fontsize=10)
ax4.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('../visualizations/STEP9_5_summary_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_5_summary_dashboard.png")
plt.close()

print()
print("=" * 80)
print("✅ ALL SEPARATE VISUALIZATIONS CREATED!")
print("=" * 80)
print()
print("📁 Generated Files:")
print("  1. STEP9_1_isolation_forest_detailed.png")
print("  2. STEP9_2_zscore_heatmap_detailed.png")
print("  3. STEP9_3_temporal_anomalies_timeseries.png")
print("  4. STEP9_4_consensus_anomalies_detailed.png")
print("  5. STEP9_5_summary_dashboard.png")
print()
print("🎨 All visualizations saved at 300 DPI for professional presentation!")
print("=" * 80)
