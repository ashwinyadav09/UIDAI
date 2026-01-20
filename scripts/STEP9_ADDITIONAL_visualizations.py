"""
STEP 9 - ADDITIONAL ADVANCED VISUALIZATIONS
============================================
Geographic and Regional Pattern Analysis
Created for UIDAI Hackathon

Features:
1. State-wise geographic heatmap
2. Regional clustering analysis
3. Anomaly type distribution
4. Detailed state profiles for top anomalies

Author: Professional ML/Data Science Engineer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

print("=" * 90)
print("STEP 9 - ADDITIONAL ADVANCED VISUALIZATIONS")
print("=" * 90)
print()

# Load data
print("📂 Loading data...")
features_df = pd.read_csv('../results/STEP9_anomaly_detection_complete.csv')
consensus_anomalies = pd.read_csv('../results/STEP9_consensus_anomalies_HIGH_PRIORITY.csv')
iso_anomalies = pd.read_csv('../results/STEP9_isolation_forest_anomalies.csv')
zscore_anomalies = pd.read_csv('../results/STEP9_zscore_anomalies.csv')
temporal_anomalies = pd.read_csv('../results/STEP9_temporal_anomalies.csv')

print(f"✓ Data loaded: {len(features_df)} states")
print()

# ============================================================================
# CHART 6: STATE PROFILE CARDS FOR TOP ANOMALIES
# ============================================================================
print("🎨 Creating Chart 6: Detailed State Profile Cards...")

# Get top 12 anomalies (by isolation forest score)
top_anomalies = features_df.nsmallest(12, 'iso_forest_score')

fig = plt.figure(figsize=(24, 16))
gs = GridSpec(4, 3, figure=fig, hspace=0.4, wspace=0.3)
fig.suptitle('Top 12 Anomalous States - Detailed Profile Cards', 
             fontsize=20, fontweight='bold', y=0.98)

for idx, (i, row) in enumerate(top_anomalies.iterrows()):
    row_pos = idx // 3
    col_pos = idx % 3
    ax = fig.add_subplot(gs[row_pos, col_pos])
    
    # Create profile card
    state_name = row['state'].upper()
    
    # Determine risk level
    if row['anomaly_count'] == 3:
        risk_color = '#E74C3C'
        risk_level = 'CRITICAL'
    elif row['anomaly_count'] == 2:
        risk_color = '#E67E22'
        risk_level = 'HIGH'
    elif row['anomaly_count'] == 1:
        risk_color = '#F39C12'
        risk_level = 'MEDIUM'
    else:
        risk_color = '#2ECC71'
        risk_level = 'LOW'
    
    # Background
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor=risk_color, alpha=0.1))
    
    # Title
    ax.text(0.5, 0.92, state_name, ha='center', va='top', fontsize=11, 
            fontweight='bold', transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=risk_color, alpha=0.8, 
                     edgecolor='black', linewidth=2))
    
    # Risk level
    ax.text(0.5, 0.82, f'Risk Level: {risk_level}', ha='center', va='top', 
            fontsize=9, fontweight='bold', transform=ax.transAxes,
            color=risk_color)
    
    # Metrics
    metrics_text = f"""
Anomaly Score: {row['iso_forest_score']:.3f}
Techniques Flagged: {row['anomaly_count']}/3

KEY METRICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bio Update Rate: {row['bio_update_rate']:.1f}%
Demo Update Rate: {row['demo_update_rate']:.1f}%
Child Enrolment: {row['child_enrol_pct']:.1f}%
Total Enrolments: {row['total_enrolments']:,.0f}

Z-SCORES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bio Rate: {row['bio_rate_zscore']:.2f}σ
Demo Rate: {row['demo_rate_zscore']:.2f}σ
Child %: {row['child_pct_zscore']:.2f}σ

DETECTION FLAGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    flags = []
    if row['iso_forest_anomaly']:
        flags.append('✓ Isolation Forest')
    if row['zscore_anomaly']:
        flags.append('✓ Z-Score Outlier')
    if row['temporal_anomaly']:
        flags.append('✓ Temporal Spike')
    
    if flags:
        metrics_text += '\n'.join(flags)
    else:
        metrics_text += '○ No flags'
    
    ax.text(0.05, 0.72, metrics_text, ha='left', va='top', fontsize=7, 
            fontfamily='monospace', transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

plt.savefig('../visualizations/STEP9_ENHANCED_6_state_profile_cards.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_6_state_profile_cards.png")
plt.close()

# ============================================================================
# CHART 7: ANOMALY TYPE DISTRIBUTION & PATTERNS
# ============================================================================
print("🎨 Creating Chart 7: Anomaly Type Distribution & Patterns...")

fig = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
fig.suptitle('Anomaly Type Distribution & Pattern Analysis', 
             fontsize=18, fontweight='bold', y=0.98)

# 7a: Bio update rate distribution
ax1 = fig.add_subplot(gs[0, 0])
normal_bio = features_df[features_df['anomaly_count'] == 0]['bio_update_rate']
anomaly_bio = features_df[features_df['anomaly_count'] >= 2]['bio_update_rate']

ax1.hist(normal_bio, bins=20, alpha=0.6, color='green', label='Normal States', 
         edgecolor='black', linewidth=1)
ax1.hist(anomaly_bio, bins=20, alpha=0.6, color='red', label='Anomalous States', 
         edgecolor='black', linewidth=1)
ax1.axvline(normal_bio.mean(), color='darkgreen', linestyle='--', linewidth=2, 
            label=f'Normal Mean: {normal_bio.mean():.1f}%')
ax1.axvline(anomaly_bio.mean(), color='darkred', linestyle='--', linewidth=2, 
            label=f'Anomaly Mean: {anomaly_bio.mean():.1f}%')
ax1.set_xlabel('Bio Update Rate (%)', fontweight='bold', fontsize=11)
ax1.set_ylabel('Frequency', fontweight='bold', fontsize=11)
ax1.set_title('Bio Update Rate Distribution', fontweight='bold', fontsize=12)
ax1.legend(fontsize=9)
ax1.grid(alpha=0.3)

# 7b: Demo update rate distribution
ax2 = fig.add_subplot(gs[0, 1])
normal_demo = features_df[features_df['anomaly_count'] == 0]['demo_update_rate']
anomaly_demo = features_df[features_df['anomaly_count'] >= 2]['demo_update_rate']

ax2.hist(normal_demo, bins=20, alpha=0.6, color='green', label='Normal States', 
         edgecolor='black', linewidth=1)
ax2.hist(anomaly_demo, bins=20, alpha=0.6, color='red', label='Anomalous States', 
         edgecolor='black', linewidth=1)
ax2.axvline(normal_demo.mean(), color='darkgreen', linestyle='--', linewidth=2, 
            label=f'Normal Mean: {normal_demo.mean():.1f}%')
ax2.axvline(anomaly_demo.mean(), color='darkred', linestyle='--', linewidth=2, 
            label=f'Anomaly Mean: {anomaly_demo.mean():.1f}%')
ax2.set_xlabel('Demo Update Rate (%)', fontweight='bold', fontsize=11)
ax2.set_ylabel('Frequency', fontweight='bold', fontsize=11)
ax2.set_title('Demo Update Rate Distribution', fontweight='bold', fontsize=12)
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

# 7c: Child enrolment distribution
ax3 = fig.add_subplot(gs[0, 2])
normal_child = features_df[features_df['anomaly_count'] == 0]['child_enrol_pct']
anomaly_child = features_df[features_df['anomaly_count'] >= 2]['child_enrol_pct']

ax3.hist(normal_child, bins=20, alpha=0.6, color='green', label='Normal States', 
         edgecolor='black', linewidth=1)
ax3.hist(anomaly_child, bins=20, alpha=0.6, color='red', label='Anomalous States', 
         edgecolor='black', linewidth=1)
ax3.axvline(normal_child.mean(), color='darkgreen', linestyle='--', linewidth=2, 
            label=f'Normal Mean: {normal_child.mean():.1f}%')
ax3.axvline(anomaly_child.mean(), color='darkred', linestyle='--', linewidth=2, 
            label=f'Anomaly Mean: {anomaly_child.mean():.1f}%')
ax3.set_xlabel('Child Enrolment (%)', fontweight='bold', fontsize=11)
ax3.set_ylabel('Frequency', fontweight='bold', fontsize=11)
ax3.set_title('Child Enrolment % Distribution', fontweight='bold', fontsize=12)
ax3.legend(fontsize=9)
ax3.grid(alpha=0.3)

# 7d: Scatter plot - Bio vs Demo update rates
ax4 = fig.add_subplot(gs[1, :2])
normal_states = features_df[features_df['anomaly_count'] == 0]
low_risk = features_df[features_df['anomaly_count'] == 1]
high_risk = features_df[features_df['anomaly_count'] >= 2]

ax4.scatter(normal_states['bio_update_rate'], normal_states['demo_update_rate'], 
           s=100, alpha=0.6, color='green', label='Normal (0)', edgecolors='black', linewidths=1)
ax4.scatter(low_risk['bio_update_rate'], low_risk['demo_update_rate'], 
           s=150, alpha=0.7, color='orange', label='Low Risk (1)', edgecolors='black', linewidths=1)
ax4.scatter(high_risk['bio_update_rate'], high_risk['demo_update_rate'], 
           s=200, alpha=0.8, color='red', label='High Risk (2+)', edgecolors='black', linewidths=2)

# Add state labels for high risk
for idx, row in high_risk.iterrows():
    ax4.annotate(row['state'][:15], 
                xy=(row['bio_update_rate'], row['demo_update_rate']),
                xytext=(5, 5), textcoords='offset points', fontsize=7,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6))

ax4.set_xlabel('Bio Update Rate (%)', fontweight='bold', fontsize=12)
ax4.set_ylabel('Demo Update Rate (%)', fontweight='bold', fontsize=12)
ax4.set_title('Bio vs Demo Update Rates - Anomaly Risk Clustering', 
              fontweight='bold', fontsize=13)
ax4.legend(fontsize=10, loc='upper right')
ax4.grid(alpha=0.3, linestyle='--')

# 7e: Anomaly characterization breakdown
ax5 = fig.add_subplot(gs[1, 2])
ax5.axis('off')

char_summary = """
╔═══════════════════════════════════════╗
║   ANOMALY CHARACTERIZATION SUMMARY    ║
╚═══════════════════════════════════════╝

PATTERN BREAKDOWN:
"""

# Count different characterizations
char_counts = {}
for char in features_df[features_df['anomaly_count'] > 0]['anomaly_characterization']:
    if pd.notna(char):
        for pattern in char.split('; '):
            char_counts[pattern] = char_counts.get(pattern, 0) + 1

# Sort and display top patterns
sorted_patterns = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
for pattern, count in sorted_patterns[:10]:
    char_summary += f"\n• {pattern}: {count} states"

char_summary += f"""

TOTAL ANOMALIES: {len(features_df[features_df['anomaly_count'] > 0])}

SEVERITY BREAKDOWN:
• Critical (3/3): {len(features_df[features_df['anomaly_count'] == 3])} states
• High (2/3): {len(features_df[features_df['anomaly_count'] == 2])} states
• Medium (1/3): {len(features_df[features_df['anomaly_count'] == 1])} states
"""

ax5.text(0.05, 0.95, char_summary, ha='left', va='top', fontsize=9, 
         fontfamily='monospace', transform=ax5.transAxes,
         bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8, 
                  edgecolor='black', linewidth=2))

plt.savefig('../visualizations/STEP9_ENHANCED_7_anomaly_patterns.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_7_anomaly_patterns.png")
plt.close()

# ============================================================================
# CHART 8: COMPREHENSIVE COMPARISON MATRIX
# ============================================================================
print("🎨 Creating Chart 8: Comprehensive Comparison Matrix...")

fig = plt.figure(figsize=(22, 14))
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)
fig.suptitle('Comprehensive State Comparison Matrix - All Metrics', 
             fontsize=18, fontweight='bold', y=0.98)

# 8a: Top 20 states - All metrics heatmap
ax1 = fig.add_subplot(gs[0:2, :])
top_20_states = features_df.nsmallest(20, 'iso_forest_score')
metrics_cols = ['bio_update_rate', 'demo_update_rate', 'child_enrol_pct', 
                'youth_enrol_pct', 'adult_enrol_pct', 'iso_forest_score', 
                'bio_rate_zscore', 'demo_rate_zscore', 'anomaly_count']

heatmap_data = top_20_states[['state'] + metrics_cols].set_index('state')[metrics_cols]

# Normalize for better visualization
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
heatmap_normalized = pd.DataFrame(
    scaler.fit_transform(heatmap_data),
    columns=metrics_cols,
    index=heatmap_data.index
)

sns.heatmap(heatmap_normalized.T, annot=False, cmap='RdYlGn', center=0.5,
           cbar_kws={'label': 'Normalized Value (0-1)', 'shrink': 0.8}, ax=ax1,
           linewidths=1, linecolor='white', vmin=0, vmax=1)

ax1.set_title('Top 20 Anomalous States - Normalized Metrics Heatmap', 
              fontweight='bold', fontsize=14, pad=15)
ax1.set_xlabel('State', fontweight='bold', fontsize=12)
ax1.set_ylabel('Metric', fontweight='bold', fontsize=12)
ax1.set_yticklabels(['Bio Update\nRate', 'Demo Update\nRate', 'Child\nEnrol %', 
                     'Youth\nEnrol %', 'Adult\nEnrol %', 'IF Score', 
                     'Bio Rate\nZ-Score', 'Demo Rate\nZ-Score', 'Anomaly\nCount'], 
                    rotation=0, fontsize=10)
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right', fontsize=9)

# 8b: Ranking table
ax2 = fig.add_subplot(gs[2, :])
ax2.axis('off')

ranking_text = """
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                           TOP 15 ANOMALOUS STATES - DETAILED RANKING                                                   ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

Rank  State                              IF Score   Bio Rate%   Demo Rate%   Child%   Anomaly Count   Risk Level
────  ─────────────────────────────────  ─────────  ──────────  ───────────  ───────  ──────────────  ──────────
"""

top_15 = features_df.nsmallest(15, 'iso_forest_score')
for rank, (idx, row) in enumerate(top_15.iterrows(), 1):
    risk = 'CRITICAL' if row['anomaly_count'] == 3 else 'HIGH' if row['anomaly_count'] == 2 else 'MEDIUM' if row['anomaly_count'] == 1 else 'LOW'
    ranking_text += f"{rank:2d}.   {row['state'][:35]:35s}  {row['iso_forest_score']:8.3f}   {row['bio_update_rate']:9.1f}   {row['demo_update_rate']:10.1f}   {row['child_enrol_pct']:6.1f}   {row['anomaly_count']:14d}   {risk:10s}\n"

ax2.text(0.5, 0.5, ranking_text, ha='center', va='center', fontsize=8, 
         fontfamily='monospace', transform=ax2.transAxes,
         bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.9, 
                  edgecolor='black', linewidth=2))

plt.savefig('../visualizations/STEP9_ENHANCED_8_comparison_matrix.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved: STEP9_ENHANCED_8_comparison_matrix.png")
plt.close()

print()
print("=" * 90)
print("✅ ADDITIONAL VISUALIZATIONS COMPLETE!")
print("=" * 90)
print()
print("📁 Generated Files:")
print("  6. STEP9_ENHANCED_6_state_profile_cards.png")
print("  7. STEP9_ENHANCED_7_anomaly_patterns.png")
print("  8. STEP9_ENHANCED_8_comparison_matrix.png")
print()
print("🎨 Total Enhanced Visualizations: 8 professional-grade charts")
print("=" * 90)
