"""
STEP 9 - ENHANCED ADVANCED VISUALIZATIONS
==========================================
Professional-grade anomaly detection visualizations with advanced analytics
Created for UIDAI Hackathon - State-wise Trend Analysis and Prediction

Features:
1. Advanced Isolation Forest visualizations with feature importance
2. Statistical distribution analysis with box plots
3. Geographic heatmaps for regional patterns
4. Correlation analysis between anomaly types
5. Risk scoring and prioritization matrices
6. Interactive-style detailed breakdowns

Author: Professional ML/Data Science Engineer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['figure.dpi'] = 100

print("=" * 90)
print("STEP 9 - ENHANCED ADVANCED ANOMALY DETECTION VISUALIZATIONS")
print("=" * 90)
print()
print("🎨 Creating professional-grade visualizations for hackathon submission...")
print()

# ============================================================================
# LOAD DATA
# ============================================================================
print("📂 Loading anomaly detection results...")
try:
    features_df = pd.read_csv('../results/STEP9_anomaly_detection_complete.csv')
    temporal_anomalies = pd.read_csv('../results/STEP9_temporal_anomalies.csv')
    iso_anomalies = pd.read_csv('../results/STEP9_isolation_forest_anomalies.csv')
    zscore_anomalies = pd.read_csv('../results/STEP9_zscore_anomalies.csv')
    consensus_anomalies = pd.read_csv('../results/STEP9_consensus_anomalies_HIGH_PRIORITY.csv')
    
    print(f"✓ Data loaded successfully!")
    print(f"  - Total states analyzed: {len(features_df)}")
    print(f"  - Isolation Forest anomalies: {len(iso_anomalies)}")
    print(f"  - Z-Score outliers: {len(zscore_anomalies)}")
    print(f"  - Temporal anomalies: {len(temporal_anomalies)} events")
    print(f"  - Consensus anomalies: {len(consensus_anomalies)}")
    print()
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

# ============================================================================
# CHART 1: ADVANCED ISOLATION FOREST ANALYSIS
# ============================================================================
print("🎨 Creating Chart 1: Advanced Isolation Forest Analysis...")

fig = plt.figure(figsize=(20, 12))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
fig.suptitle('Isolation Forest - Advanced Multivariate Anomaly Detection Analysis', 
             fontsize=18, fontweight='bold', y=0.98)

# 1a: Score distribution with KDE
ax1 = fig.add_subplot(gs[0, :2])
sorted_df = features_df.sort_values('iso_forest_score')
colors = ['#FF4444' if x else '#4A90E2' for x in sorted_df['iso_forest_anomaly']]
bars = ax1.barh(range(len(sorted_df)), sorted_df['iso_forest_score'], 
                color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
ax1.set_yticks(range(0, len(sorted_df), max(1, len(sorted_df)//20)))
ax1.set_yticklabels(sorted_df['state'].iloc[::max(1, len(sorted_df)//20)], fontsize=8)
ax1.set_xlabel('Isolation Forest Anomaly Score (lower = more anomalous)', fontweight='bold', fontsize=11)
ax1.set_ylabel('States', fontweight='bold', fontsize=11)
ax1.set_title('All States - Anomaly Score Distribution', fontweight='bold', fontsize=13, pad=10)

if len(iso_anomalies) > 0:
    threshold_val = sorted_df[sorted_df['iso_forest_anomaly']]['iso_forest_score'].max()
    ax1.axvline(threshold_val, color='#FF6B35', linestyle='--', linewidth=3, 
                label=f'Anomaly Threshold: {threshold_val:.3f}', alpha=0.8)
    ax1.legend(fontsize=11, loc='lower right')
ax1.grid(axis='x', alpha=0.4, linestyle='--')

# Add annotation box
textstr = f'Detected: {len(iso_anomalies)} anomalies\nContamination: 5%\nAlgorithm: Isolation Forest'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)

# 1b: Score histogram with distribution
ax2 = fig.add_subplot(gs[0, 2])
ax2.hist(features_df['iso_forest_score'], bins=30, color='#4A90E2', 
         alpha=0.7, edgecolor='black', linewidth=1.5)
ax2.axvline(features_df['iso_forest_score'].mean(), color='red', 
            linestyle='--', linewidth=2, label=f'Mean: {features_df["iso_forest_score"].mean():.3f}')
ax2.axvline(features_df['iso_forest_score'].median(), color='green', 
            linestyle='--', linewidth=2, label=f'Median: {features_df["iso_forest_score"].median():.3f}')
ax2.set_xlabel('Anomaly Score', fontweight='bold', fontsize=10)
ax2.set_ylabel('Frequency', fontweight='bold', fontsize=10)
ax2.set_title('Score Distribution', fontweight='bold', fontsize=12)
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

# 1c: Feature importance for anomalies (Radar-style comparison)
ax3 = fig.add_subplot(gs[1, :])
if len(iso_anomalies) > 0:
    feature_cols = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct', 
                    'youth_enrol_pct', 'adult_enrol_pct']
    
    # Get top 10 anomalies
    top_anomalies = iso_anomalies.nsmallest(10, 'iso_forest_score')
    
    # Create grouped bar chart
    x = np.arange(len(feature_cols))
    width = 0.08
    
    colors_palette = plt.cm.tab10(np.linspace(0, 1, 10))
    
    for idx, (i, row) in enumerate(top_anomalies.iterrows()):
        values = [row[col] for col in feature_cols]
        ax3.bar(x + idx*width, values, width, label=row['state'][:15], 
                color=colors_palette[idx], edgecolor='black', linewidth=0.5)
    
    ax3.set_xlabel('Features', fontweight='bold', fontsize=12)
    ax3.set_ylabel('Value', fontweight='bold', fontsize=12)
    ax3.set_title('Top 10 Anomalous States - Feature Profile Comparison', 
                  fontweight='bold', fontsize=14, pad=10)
    ax3.set_xticks(x + width * 4.5)
    ax3.set_xticklabels(['Bio Update\nRate (%)', 'Demo Update\nRate (%)', 
                         'Child\nEnrolment (%)', 'Youth\nEnrolment (%)', 
                         'Adult\nEnrolment (%)'], fontsize=10)
    ax3.legend(ncol=5, fontsize=9, loc='upper right', framealpha=0.9)
    ax3.grid(axis='y', alpha=0.3)
else:
    ax3.text(0.5, 0.5, 'No anomalies detected', ha='center', va='center', 
             fontsize=14, transform=ax3.transAxes)

# 1d: Box plot comparison - Normal vs Anomalous
ax4 = fig.add_subplot(gs[2, :])
feature_cols_box = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct']
normal_data = features_df[~features_df['iso_forest_anomaly']][feature_cols_box]
anomaly_data = features_df[features_df['iso_forest_anomaly']][feature_cols_box]

positions_normal = np.arange(len(feature_cols_box)) * 2
positions_anomaly = positions_normal + 0.8

bp1 = ax4.boxplot([normal_data[col].dropna() for col in feature_cols_box], 
                   positions=positions_normal, widths=0.6,
                   patch_artist=True, showfliers=True,
                   boxprops=dict(facecolor='#90EE90', edgecolor='black', linewidth=1.5),
                   medianprops=dict(color='darkgreen', linewidth=2),
                   whiskerprops=dict(color='black', linewidth=1.5),
                   capprops=dict(color='black', linewidth=1.5),
                   flierprops=dict(marker='o', markerfacecolor='green', markersize=5, alpha=0.5))

bp2 = ax4.boxplot([anomaly_data[col].dropna() for col in feature_cols_box], 
                   positions=positions_anomaly, widths=0.6,
                   patch_artist=True, showfliers=True,
                   boxprops=dict(facecolor='#FFB6C1', edgecolor='black', linewidth=1.5),
                   medianprops=dict(color='darkred', linewidth=2),
                   whiskerprops=dict(color='black', linewidth=1.5),
                   capprops=dict(color='black', linewidth=1.5),
                   flierprops=dict(marker='o', markerfacecolor='red', markersize=5, alpha=0.5))

ax4.set_xticks(positions_normal + 0.4)
ax4.set_xticklabels(['Bio Update Rate (%)', 'Demo Update Rate (%)', 'Child Enrolment (%)'], 
                     fontsize=11, fontweight='bold')
ax4.set_ylabel('Value', fontweight='bold', fontsize=12)
ax4.set_title('Statistical Distribution Comparison: Normal States vs Anomalous States', 
              fontweight='bold', fontsize=14, pad=10)
ax4.legend([bp1["boxes"][0], bp2["boxes"][0]], ['Normal States', 'Anomalous States'], 
           fontsize=11, loc='upper right')
ax4.grid(axis='y', alpha=0.3)

plt.savefig('../visualizations/STEP9_ENHANCED_1_isolation_forest_advanced.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_1_isolation_forest_advanced.png")
plt.close()

# ============================================================================
# CHART 2: Z-SCORE ADVANCED STATISTICAL ANALYSIS
# ============================================================================
print("🎨 Creating Chart 2: Z-Score Advanced Statistical Analysis...")

fig = plt.figure(figsize=(20, 14))
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)
fig.suptitle('Z-Score Method - Advanced Statistical Outlier Detection (3-Sigma Threshold)', 
             fontsize=18, fontweight='bold', y=0.98)

# 2a: Comprehensive heatmap
ax1 = fig.add_subplot(gs[0:2, :])
zscore_cols = ['bio_rate_zscore', 'demo_rate_zscore', 'child_pct_zscore', 'enrol_zscore']
heatmap_data = features_df.sort_values('bio_rate_zscore', ascending=False).head(30)
heatmap_matrix = heatmap_data[zscore_cols + ['state']].set_index('state')[zscore_cols].T

sns.heatmap(heatmap_matrix, annot=True, fmt='.2f', cmap='YlOrRd', 
           yticklabels=['Bio Update Rate', 'Demo Update Rate', 'Child Enrolment %', 'Total Enrolments'],
           cbar_kws={'label': 'Z-Score (σ)', 'shrink': 0.8}, ax=ax1, 
           linewidths=1.5, linecolor='white', vmin=0, vmax=6,
           annot_kws={'size': 8, 'weight': 'bold'})

ax1.set_title('Top 30 States by Bio Update Rate Z-Score - Multi-Metric Analysis', 
              fontweight='bold', fontsize=14, pad=15)
ax1.set_xlabel('State', fontweight='bold', fontsize=12)
ax1.set_ylabel('Metric', fontweight='bold', fontsize=12)
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right', fontsize=9)
plt.setp(ax1.get_yticklabels(), rotation=0, fontsize=11)

# Add threshold reference
for i in range(4):
    ax1.axhline(y=i+0.5, color='gray', linewidth=0.5, alpha=0.5)

# Add annotation
textstr = 'Red cells (>3σ) = Statistical outliers\nRequire immediate investigation'
props = dict(boxstyle='round', facecolor='yellow', alpha=0.7)
ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=11,
        verticalalignment='top', bbox=props)

# 2b: Z-score distribution by metric
ax2 = fig.add_subplot(gs[2, 0])
zscore_data = features_df[zscore_cols].values.flatten()
ax2.hist(zscore_data, bins=50, color='#FF6B6B', alpha=0.7, edgecolor='black', linewidth=1)
ax2.axvline(3, color='red', linestyle='--', linewidth=3, label='3σ Threshold', alpha=0.8)
ax2.axvline(zscore_data.mean(), color='blue', linestyle='--', linewidth=2, 
            label=f'Mean: {zscore_data.mean():.2f}σ')
ax2.set_xlabel('Z-Score (σ)', fontweight='bold', fontsize=11)
ax2.set_ylabel('Frequency', fontweight='bold', fontsize=11)
ax2.set_title('Overall Z-Score Distribution', fontweight='bold', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(alpha=0.3)

# 2c: Outlier count by metric
ax3 = fig.add_subplot(gs[2, 1])
outlier_counts = {
    'Bio Update\nRate': (features_df['bio_rate_zscore'] > 3).sum(),
    'Demo Update\nRate': (features_df['demo_rate_zscore'] > 3).sum(),
    'Child\nEnrolment %': (features_df['child_pct_zscore'] > 3).sum(),
    'Total\nEnrolments': (features_df['enrol_zscore'] > 3).sum()
}

colors_bar = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
bars = ax3.bar(range(len(outlier_counts)), outlier_counts.values(), 
              color=colors_bar, edgecolor='black', linewidth=2, width=0.6)
ax3.set_xticks(range(len(outlier_counts)))
ax3.set_xticklabels(outlier_counts.keys(), fontsize=10)
ax3.set_ylabel('Number of Outlier States', fontweight='bold', fontsize=11)
ax3.set_title('Outlier Count by Metric (>3σ)', fontweight='bold', fontsize=12)
ax3.grid(axis='y', alpha=0.3)

for i, v in enumerate(outlier_counts.values()):
    ax3.text(i, v, str(v), ha='center', va='bottom', fontweight='bold', fontsize=14)

plt.savefig('../visualizations/STEP9_ENHANCED_2_zscore_advanced.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_2_zscore_advanced.png")
plt.close()

# ============================================================================
# CHART 3: TEMPORAL ANOMALIES - ADVANCED TIME SERIES
# ============================================================================
print("🎨 Creating Chart 3: Temporal Anomalies - Advanced Time Series...")

if len(temporal_anomalies) > 0:
    fig = plt.figure(figsize=(20, 14))
    gs = GridSpec(4, 2, figure=fig, hspace=0.4, wspace=0.25)
    fig.suptitle('Temporal Anomalies - Advanced Time Series Analysis (±50% MoM Threshold)', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Get top 6 states
    top_states = temporal_anomalies['state'].value_counts().head(6).index
    
    colors_palette = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
    
    for idx, state in enumerate(top_states):
        row = idx // 2
        col = idx % 2
        ax = fig.add_subplot(gs[row, col])
        
        state_data = temporal_anomalies[temporal_anomalies['state'] == state].copy()
        state_data = state_data.sort_values('year_month')
        
        x_vals = [str(x) for x in state_data['year_month']]
        y_vals = state_data['mom_change'].values
        
        # Plot with filled area
        ax.plot(x_vals, y_vals, marker='o', linewidth=2.5, markersize=10, 
               color=colors_palette[idx], label=state, alpha=0.8, markeredgecolor='black', markeredgewidth=1)
        ax.fill_between(range(len(x_vals)), y_vals, 0, alpha=0.3, color=colors_palette[idx])
        
        # Threshold lines
        ax.axhline(50, color='red', linestyle='--', linewidth=2, alpha=0.6, label='+50% threshold')
        ax.axhline(-50, color='red', linestyle='--', linewidth=2, alpha=0.6, label='-50% threshold')
        ax.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.4)
        
        # Annotate max/min
        max_idx = np.argmax(np.abs(y_vals))
        ax.annotate(f'{y_vals[max_idx]:+.1f}%', 
                   xy=(max_idx, y_vals[max_idx]),
                   xytext=(10, 15 if y_vals[max_idx] > 0 else -15), 
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8, edgecolor='black'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                                 color='black', lw=2),
                   fontsize=10, fontweight='bold')
        
        ax.set_title(f'{state} - {len(state_data)} Anomaly Events', 
                    fontweight='bold', fontsize=12, pad=10)
        ax.set_ylabel('MoM Change (%)', fontweight='bold', fontsize=10)
        ax.grid(alpha=0.3, linestyle='--')
        ax.legend(loc='upper right', fontsize=8)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        
        # Color zones
        ax.fill_between(range(len(x_vals)), 50, 200, alpha=0.1, color='red')
        ax.fill_between(range(len(x_vals)), -50, -200, alpha=0.1, color='red')
    
    # Summary statistics in remaining space
    ax_summary = fig.add_subplot(gs[3, :])
    ax_summary.axis('off')
    
    summary_stats = f"""
    TEMPORAL ANOMALY SUMMARY STATISTICS
    
    Total Anomaly Events: {len(temporal_anomalies)}
    States Affected: {temporal_anomalies['state'].nunique()}
    Average MoM Change: {temporal_anomalies['mom_change'].abs().mean():.1f}%
    Maximum Spike: {temporal_anomalies['mom_change'].max():.1f}% ({temporal_anomalies.loc[temporal_anomalies['mom_change'].idxmax(), 'state']})
    Maximum Drop: {temporal_anomalies['mom_change'].min():.1f}% ({temporal_anomalies.loc[temporal_anomalies['mom_change'].idxmin(), 'state']})
    
    Top 3 States by Anomaly Frequency:
    """
    
    top_3 = temporal_anomalies['state'].value_counts().head(3)
    for i, (state, count) in enumerate(top_3.items(), 1):
        summary_stats += f"\n    {i}. {state}: {count} events"
    
    ax_summary.text(0.5, 0.5, summary_stats, transform=ax_summary.transAxes,
                   fontsize=12, verticalalignment='center', horizontalalignment='center',
                   fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5, 
                           edgecolor='black', linewidth=2))
    
    plt.savefig('../visualizations/STEP9_ENHANCED_3_temporal_advanced.png', 
                dpi=300, bbox_inches='tight')
    print("✓ Saved: STEP9_ENHANCED_3_temporal_advanced.png")
    plt.close()
else:
    print("⚠ No temporal anomalies to visualize")

# ============================================================================
# CHART 4: CONSENSUS & CORRELATION ANALYSIS
# ============================================================================
print("🎨 Creating Chart 4: Consensus & Correlation Analysis...")

fig = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
fig.suptitle('Consensus Anomalies - Multi-Technique Correlation & Risk Analysis', 
             fontsize=18, fontweight='bold', y=0.98)

# 4a: Venn-style overlap visualization
ax1 = fig.add_subplot(gs[0, 0])
from matplotlib.patches import Circle
iso_count = len(features_df[features_df['iso_forest_anomaly']])
zscore_count = len(features_df[features_df['zscore_anomaly']])
temporal_count = len(features_df[features_df['temporal_anomaly']])
consensus_count = len(consensus_anomalies)

technique_data = {
    'Isolation\nForest': iso_count,
    'Z-Score\nMethod': zscore_count,
    'Temporal\nAnalysis': temporal_count,
    'Consensus\n(2+ methods)': consensus_count
}

colors_tech = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
bars = ax1.bar(range(len(technique_data)), technique_data.values(), 
              color=colors_tech, edgecolor='black', linewidth=2.5, width=0.7, alpha=0.8)
ax1.set_xticks(range(len(technique_data)))
ax1.set_xticklabels(technique_data.keys(), fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of States', fontweight='bold', fontsize=12)
ax1.set_title('Detection by Technique', fontweight='bold', fontsize=13, pad=10)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

for i, v in enumerate(technique_data.values()):
    ax1.text(i, v, str(v), ha='center', va='bottom', fontweight='bold', fontsize=16)

# 4b: Anomaly severity distribution
ax2 = fig.add_subplot(gs[0, 1])
anomaly_dist = features_df['anomaly_count'].value_counts().sort_index()
colors_severity = ['#2ECC71', '#F39C12', '#E67E22', '#E74C3C']
labels_map = {0: 'Normal\n(0 techniques)', 1: 'Low Risk\n(1 technique)', 
              2: 'Medium Risk\n(2 techniques)', 3: 'High Risk\n(3 techniques)'}

# Create labels and colors based on actual data
labels_severity = [labels_map[i] for i in anomaly_dist.index]
colors_used = [colors_severity[i] for i in anomaly_dist.index]
explode_vals = [0.05 * i for i in range(len(anomaly_dist))]

# Create pie chart
wedges, texts, autotexts = ax2.pie(anomaly_dist.values, labels=labels_severity,
                                     colors=colors_used, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 10, 'weight': 'bold'},
                                     explode=explode_vals)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_weight('bold')

ax2.set_title('Risk Distribution Across States', fontweight='bold', fontsize=13, pad=10)

# 4c: Consensus states matrix
ax3 = fig.add_subplot(gs[0, 2])
if len(consensus_anomalies) > 0:
    consensus_data = consensus_anomalies[['state', 'anomaly_count', 'iso_forest_anomaly', 
                                          'zscore_anomaly', 'temporal_anomaly']].copy()
    
    technique_matrix = consensus_data[['iso_forest_anomaly', 'zscore_anomaly', 
                                       'temporal_anomaly']].T
    technique_matrix.columns = consensus_data['state']
    technique_matrix.index = ['Isolation\nForest', 'Z-Score', 'Temporal']
    
    sns.heatmap(technique_matrix.astype(int), annot=True, fmt='d', cmap='RdYlGn_r', 
               cbar_kws={'label': 'Detected', 'ticks': [0, 1]}, ax=ax3, 
               linewidths=2, linecolor='white', vmin=0, vmax=1,
               annot_kws={'size': 12, 'weight': 'bold'})
    
    ax3.set_title('Consensus Detection Matrix', fontweight='bold', fontsize=13, pad=10)
    ax3.set_xlabel('State', fontweight='bold', fontsize=11)
    ax3.set_ylabel('Technique', fontweight='bold', fontsize=11)
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    plt.setp(ax3.get_yticklabels(), rotation=0, fontsize=10)
else:
    ax3.text(0.5, 0.5, 'No consensus anomalies', ha='center', va='center', 
             fontsize=14, transform=ax3.transAxes)

# 4d: Feature correlation for anomalies
ax4 = fig.add_subplot(gs[1, :2])
feature_cols_corr = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct', 
                     'youth_enrol_pct', 'adult_enrol_pct', 'total_enrolments']
corr_matrix = features_df[feature_cols_corr].corr()

sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
           square=True, linewidths=2, linecolor='white', ax=ax4,
           cbar_kws={'label': 'Correlation Coefficient', 'shrink': 0.8},
           vmin=-1, vmax=1, annot_kws={'size': 10, 'weight': 'bold'})

ax4.set_title('Feature Correlation Matrix - All States', fontweight='bold', fontsize=13, pad=10)
ax4.set_xticklabels(['Bio Update\nRate', 'Demo Update\nRate', 'Child\nEnrol %', 
                     'Youth\nEnrol %', 'Adult\nEnrol %', 'Total\nEnrolments'], 
                    fontsize=10, rotation=45, ha='right')
ax4.set_yticklabels(['Bio Update\nRate', 'Demo Update\nRate', 'Child\nEnrol %', 
                     'Youth\nEnrol %', 'Adult\nEnrol %', 'Total\nEnrolments'], 
                    fontsize=10, rotation=0)

# 4e: Risk scoring matrix
ax5 = fig.add_subplot(gs[1, 2])
if len(consensus_anomalies) > 0:
    # Calculate risk scores
    risk_data = consensus_anomalies[['state', 'anomaly_count']].copy()
    risk_data['risk_score'] = risk_data['anomaly_count'] / 3 * 100
    risk_data = risk_data.sort_values('risk_score', ascending=True)
    
    colors_risk = ['#E74C3C' if x == 3 else '#E67E22' for x in risk_data['anomaly_count']]
    
    bars = ax5.barh(range(len(risk_data)), risk_data['risk_score'], 
                   color=colors_risk, edgecolor='black', linewidth=1.5, alpha=0.8)
    ax5.set_yticks(range(len(risk_data)))
    ax5.set_yticklabels(risk_data['state'], fontsize=9)
    ax5.set_xlabel('Risk Score (%)', fontweight='bold', fontsize=11)
    ax5.set_title('Consensus States - Risk Scoring', fontweight='bold', fontsize=13, pad=10)
    ax5.set_xlim(0, 100)
    ax5.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (idx, row) in enumerate(risk_data.iterrows()):
        ax5.text(row['risk_score'] + 2, i, f"{row['risk_score']:.0f}%", 
                va='center', fontweight='bold', fontsize=9)
else:
    ax5.text(0.5, 0.5, 'No consensus anomalies', ha='center', va='center', 
             fontsize=14, transform=ax5.transAxes)

plt.savefig('../visualizations/STEP9_ENHANCED_4_consensus_correlation.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_4_consensus_correlation.png")
plt.close()

# ============================================================================
# CHART 5: COMPREHENSIVE EXECUTIVE DASHBOARD
# ============================================================================
print("🎨 Creating Chart 5: Comprehensive Executive Dashboard...")

fig = plt.figure(figsize=(22, 16))
gs = GridSpec(4, 4, figure=fig, hspace=0.4, wspace=0.35)
fig.suptitle('Anomaly Detection Framework - Comprehensive Executive Dashboard', 
             fontsize=20, fontweight='bold', y=0.99)

# Summary panel
ax_summary = fig.add_subplot(gs[0, :])
ax_summary.axis('off')

summary_text = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                          MULTI-TECHNIQUE ANOMALY DETECTION - EXECUTIVE SUMMARY                               ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📊 ANALYSIS SCOPE:  {len(features_df)} States/UTs Analyzed  |  3 Detection Techniques Applied  |  {len(consensus_anomalies)} High-Priority Anomalies

🔍 TECHNIQUE RESULTS:
   ├─ Isolation Forest (Multivariate ML):      {len(iso_anomalies):2d} anomalies ({len(iso_anomalies)/len(features_df)*100:5.1f}%) - Complex pattern detection
   ├─ Z-Score Method (3-Sigma Statistical):    {len(zscore_anomalies):2d} outliers  ({len(zscore_anomalies)/len(features_df)*100:5.1f}%) - Individual metric extremes
   ├─ Temporal Analysis (±50% MoM Change):     {len(features_df[features_df['temporal_anomaly']]):2d} states    ({len(features_df[features_df['temporal_anomaly']])/len(features_df)*100:5.1f}%) - Service demand volatility
   └─ Consensus Detection (2+ Techniques):     {len(consensus_anomalies):2d} states    ({len(consensus_anomalies)/len(features_df)*100:5.1f}%) - HIGH CONFIDENCE ANOMALIES

🎯 KEY INSIGHTS:
   • {len(consensus_anomalies)} states require immediate investigation (flagged by multiple techniques)
   • {len(temporal_anomalies)} temporal anomaly events detected across {temporal_anomalies['state'].nunique() if len(temporal_anomalies) > 0 else 0} states
   • Average anomaly score: {features_df['iso_forest_score'].mean():.3f} (lower = more anomalous)
"""

if len(consensus_anomalies) > 0:
    summary_text += f"\n🚨 TOP PRIORITY STATES (Consensus Anomalies):\n"
    for idx, row in consensus_anomalies.head(5).iterrows():
        techniques = []
        if row['iso_forest_anomaly']: techniques.append('IF')
        if row['zscore_anomaly']: techniques.append('ZS')
        if row['temporal_anomaly']: techniques.append('TS')
        summary_text += f"   • {row['state']:30s} → {row['anomaly_count']}/3 techniques [{', '.join(techniques)}]\n"

ax_summary.text(0.02, 0.98, summary_text, transform=ax_summary.transAxes,
               fontsize=10, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.9, 
                        edgecolor='#2C3E50', linewidth=2))

# Mini chart 1: Top anomalies by IF score
ax1 = fig.add_subplot(gs[1, :2])
top_iso = features_df.nsmallest(15, 'iso_forest_score')
bars1 = ax1.barh(range(len(top_iso)), top_iso['iso_forest_score'], 
                color='#FF6B6B', edgecolor='black', linewidth=1, alpha=0.8)
ax1.set_yticks(range(len(top_iso)))
ax1.set_yticklabels(top_iso['state'], fontsize=9)
ax1.set_xlabel('Isolation Forest Score', fontsize=10, fontweight='bold')
ax1.set_title('Top 15 States - Lowest IF Scores (Most Anomalous)', 
              fontweight='bold', fontsize=11, pad=8)
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Mini chart 2: Top Z-score outliers
ax2 = fig.add_subplot(gs[1, 2:])
top_z = features_df.nlargest(15, 'bio_rate_zscore')
bars2 = ax2.barh(range(len(top_z)), top_z['bio_rate_zscore'], 
                color='#4ECDC4', edgecolor='black', linewidth=1, alpha=0.8)
ax2.set_yticks(range(len(top_z)))
ax2.set_yticklabels(top_z['state'], fontsize=9)
ax2.set_xlabel('Z-Score (σ)', fontsize=10, fontweight='bold')
ax2.set_title('Top 15 States - Highest Bio Update Rate Z-Scores', 
              fontweight='bold', fontsize=11, pad=8)
ax2.axvline(3, color='red', linestyle='--', linewidth=2, label='3σ Threshold')
ax2.legend(fontsize=9)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Mini chart 3: Temporal frequency
ax3 = fig.add_subplot(gs[2, :2])
if len(temporal_anomalies) > 0:
    temp_counts = temporal_anomalies['state'].value_counts().head(15)
    bars3 = ax3.barh(range(len(temp_counts)), temp_counts.values, 
                    color='#45B7D1', edgecolor='black', linewidth=1, alpha=0.8)
    ax3.set_yticks(range(len(temp_counts)))
    ax3.set_yticklabels(temp_counts.index, fontsize=9)
    ax3.set_xlabel('Number of Anomaly Events', fontsize=10, fontweight='bold')
    ax3.set_title('Top 15 States - Temporal Anomaly Frequency', 
                  fontweight='bold', fontsize=11, pad=8)
    ax3.grid(axis='x', alpha=0.3, linestyle='--')

# Mini chart 4: Feature comparison
ax4 = fig.add_subplot(gs[2, 2:])
feature_cols_comp = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct']
x_pos = np.arange(len(feature_cols_comp))
width = 0.35

normal_states = features_df[features_df['anomaly_count'] == 0]
anomaly_states = features_df[features_df['anomaly_count'] >= 2]

normal_means = [normal_states[col].mean() for col in feature_cols_comp]
anomaly_means = [anomaly_states[col].mean() for col in feature_cols_comp]

bars1 = ax4.bar(x_pos - width/2, normal_means, width, label='Normal States', 
               color='#2ECC71', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax4.bar(x_pos + width/2, anomaly_means, width, label='Anomalous States', 
               color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)

ax4.set_xlabel('Features', fontweight='bold', fontsize=10)
ax4.set_ylabel('Mean Value', fontweight='bold', fontsize=10)
ax4.set_title('Feature Comparison: Normal vs Anomalous States', 
              fontweight='bold', fontsize=11, pad=8)
ax4.set_xticks(x_pos)
ax4.set_xticklabels(['Bio Update\nRate (%)', 'Demo Update\nRate (%)', 'Child\nEnrol (%)'], 
                     fontsize=9)
ax4.legend(fontsize=9)
ax4.grid(axis='y', alpha=0.3, linestyle='--')

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

# Mini chart 5: Anomaly severity pyramid
ax5 = fig.add_subplot(gs[3, 0:2])
severity_data = features_df['anomaly_count'].value_counts().sort_index(ascending=False)
colors_pyramid = ['#E74C3C', '#E67E22', '#F39C12', '#2ECC71']
y_pos = np.arange(len(severity_data))

bars5 = ax5.barh(y_pos, severity_data.values, color=colors_pyramid, 
                edgecolor='black', linewidth=2, alpha=0.8)
ax5.set_yticks(y_pos)
ax5.set_yticklabels([f'Level {i}: {["High Risk", "Medium Risk", "Low Risk", "Normal"][i]}' 
                      for i in range(len(severity_data))], fontsize=10, fontweight='bold')
ax5.set_xlabel('Number of States', fontweight='bold', fontsize=10)
ax5.set_title('Anomaly Severity Pyramid', fontweight='bold', fontsize=11, pad=8)
ax5.grid(axis='x', alpha=0.3, linestyle='--')

for i, v in enumerate(severity_data.values):
    ax5.text(v + max(severity_data.values)*0.02, i, str(v), 
            va='center', fontweight='bold', fontsize=12)

# Mini chart 6: Recommendations panel
ax6 = fig.add_subplot(gs[3, 2:])
ax6.axis('off')

recommendations = """
╔═══════════════════════════════════════════════╗
║        ACTIONABLE RECOMMENDATIONS             ║
╚═══════════════════════════════════════════════╝

🎯 IMMEDIATE ACTIONS:
"""

if len(consensus_anomalies) > 0:
    recommendations += f"""
   1. Investigate {len(consensus_anomalies)} consensus anomaly states
      → Multi-technique detection = high confidence
      
   2. Deploy targeted campaigns in states with:
      → Low bio update rates (exclusion risk)
      → High temporal volatility (capacity issues)
      
   3. Allocate resources based on risk scores:
      → {len(features_df[features_df['anomaly_count'] == 3])} states at HIGH risk (3/3 techniques)
      → {len(features_df[features_df['anomaly_count'] == 2])} states at MEDIUM risk (2/3 techniques)
"""
else:
    recommendations += "\n   ✓ No high-priority anomalies detected\n   ✓ System operating within normal parameters"

recommendations += """

📊 MONITORING PRIORITIES:
   • Track temporal anomalies for capacity planning
   • Monitor Z-score outliers for service quality
   • Review IF anomalies for complex patterns

🔄 NEXT STEPS:
   • Validate findings with ground truth data
   • Implement predictive models (Step 10)
   • Create state-specific intervention plans
"""

ax6.text(0.05, 0.95, recommendations, transform=ax6.transAxes,
        fontsize=9, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#FFF9E6', alpha=0.9, 
                 edgecolor='#D35400', linewidth=2))

plt.savefig('../visualizations/STEP9_ENHANCED_5_executive_dashboard.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_5_executive_dashboard.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 90)
print("✅ ENHANCED ANOMALY DETECTION VISUALIZATIONS COMPLETE!")
print("=" * 90)
print()
print("📁 Generated Files (All at 300 DPI):")
print("  1. STEP9_ENHANCED_1_isolation_forest_advanced.png")
print("  2. STEP9_ENHANCED_2_zscore_advanced.png")
print("  3. STEP9_ENHANCED_3_temporal_advanced.png")
print("  4. STEP9_ENHANCED_4_consensus_correlation.png")
print("  5. STEP9_ENHANCED_5_executive_dashboard.png")
print()
print("🎨 Features:")
print("  ✓ Advanced statistical visualizations with box plots")
print("  ✓ Correlation analysis and feature importance")
print("  ✓ Risk scoring and prioritization matrices")
print("  ✓ Comprehensive executive dashboard with recommendations")
print("  ✓ Professional-grade charts ready for hackathon submission")
print()
print("🏆 Ready for UIDAI Hackathon PDF Report!")
print("=" * 90)
