"""
STEP 12: COMPREHENSIVE DASHBOARDS - WORKING VERSION
===================================================
Creates 10 individual professional visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")

print("=" * 100)
print("STEP 12: CREATING COMPREHENSIVE DASHBOARDS")
print("=" * 100)
print()

# Load data
print("📂 Loading data...")
step6_state = pd.read_csv('../results/STEP6_state_summary.csv')
step6_enrol = pd.read_csv('../results/STEP6_enrolment_trends.csv')
step6_bio = pd.read_csv('../results/STEP6_biometric_trends.csv')
step7_child = pd.read_csv('../results/STEP7_child_enrolment_analysis.csv')
step8_comp = pd.read_csv('../results/STEP8_biometric_compliance_analysis.csv')
step9_anom = pd.read_csv('../results/STEP9_anomaly_detection_complete.csv')
step10_cap = pd.read_csv('../results/STEP10_capacity_planning_analysis.csv')
step11_bot = pd.read_csv('../results/STEP11_bottleneck_predictions.csv')
step11_age = pd.read_csv('../results/STEP11_age_group_targeting.csv')
print("✓ Data loaded!\n")

# DASHBOARD 1: State Update Rate Heatmap
print("🎨 Dashboard 1: State Update Rate Heatmap...")
fig, ax = plt.subplots(figsize=(16, 12))
data = step6_state[['state', 'bio_update_rate', 'demo_update_rate']].sort_values('bio_update_rate', ascending=False)
states = data['state'].tolist()
values = data[['bio_update_rate', 'demo_update_rate']].values.T

im = ax.imshow(values, cmap='RdYlGn', aspect='auto')
ax.set_xticks(np.arange(len(states)))
ax.set_yticks([0, 1])
ax.set_xticklabels([s.title() for s in states], rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(['Biometric\nUpdate Rate (%)', 'Demographic\nUpdate Rate (%)'], fontsize=12, fontweight='bold')

for i in range(2):
    for j in range(len(states)):
        ax.text(j, i, f'{values[i, j]:.1f}', ha="center", va="center", fontsize=8, fontweight='bold')

plt.colorbar(im, ax=ax, shrink=0.8, label='Update Rate (%)')
ax.set_title('State-wise Update Rate Heatmap', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_01_state_update_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 2: Enrolment Trends
print("🎨 Dashboard 2: Enrolment Trends...")
fig, ax = plt.subplots(figsize=(18, 10))
top10 = step6_state.nlargest(10, 'total_enrolments')['state'].tolist()
colors = plt.cm.tab10(np.linspace(0, 1, 10))

for idx, state in enumerate(top10):
    data = step6_enrol[step6_enrol['state'] == state].sort_values('year_month')
    if len(data) > 0:
        ax.plot(data['year_month'], data['total_enrolments'], marker='o', linewidth=2.5, 
               label=state.title(), color=colors[idx], alpha=0.8)

ax.set_xlabel('Month', fontsize=14, fontweight='bold')
ax.set_ylabel('Total Enrolments', fontsize=14, fontweight='bold')
ax.set_title('Monthly Enrolment Trends - Top 10 States', fontsize=16, fontweight='bold')
ax.legend(loc='best', fontsize=10, ncol=2)
ax.grid(alpha=0.4)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_02_enrolment_trends.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 3: Biometric Trends
print("🎨 Dashboard 3: Biometric Update Trends...")
fig, ax = plt.subplots(figsize=(18, 10))
top10_bio = step6_state.nlargest(10, 'total_bio_updates')['state'].tolist()

for idx, state in enumerate(top10_bio):
    data = step6_bio[step6_bio['state'] == state].sort_values('year_month')
    if len(data) > 0:
        ax.plot(data['year_month'], data['total_bio_updates'], marker='s', linewidth=2.5,
               label=state.title(), color=colors[idx], alpha=0.8)

ax.set_xlabel('Month', fontsize=14, fontweight='bold')
ax.set_ylabel('Total Biometric Updates', fontsize=14, fontweight='bold')
ax.set_title('Monthly Biometric Update Trends - Top 10 States', fontsize=16, fontweight='bold')
ax.legend(loc='best', fontsize=10, ncol=2)
ax.grid(alpha=0.4)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_03_biometric_trends.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 4: Age Group Distribution
print("🎨 Dashboard 4: Age Group Distribution...")
fig, ax = plt.subplots(figsize=(16, 10))
age_data = step7_child[['state', 'age_0_5_percentage', 'age_5_17_percentage', 'age_18_plus_percentage']].nlargest(15, 'age_0_5_percentage')

x = np.arange(len(age_data))
width = 0.25

ax.bar(x - width, age_data['age_0_5_percentage'], width, label='Children (0-5)', color='#FF6B6B', edgecolor='black', linewidth=1.5)
ax.bar(x, age_data['age_5_17_percentage'], width, label='Youth (5-17)', color='#4ECDC4', edgecolor='black', linewidth=1.5)
ax.bar(x + width, age_data['age_18_plus_percentage'], width, label='Adults (18+)', color='#45B7D1', edgecolor='black', linewidth=1.5)

ax.set_xlabel('State', fontsize=14, fontweight='bold')
ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax.set_title('Age Group Distribution - Top 15 States by Child Enrolment', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([s.title() for s in age_data['state']], rotation=45, ha='right', fontsize=9)
ax.legend(fontsize=12)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_04_age_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 5: Child Enrolment Gap
print("🎨 Dashboard 5: Child Enrolment Gap...")
fig, ax = plt.subplots(figsize=(16, 10))
low_child = step7_child.nsmallest(20, 'age_0_5_percentage')

y_pos = np.arange(len(low_child))
colors_risk = ['#E74C3C' if x < 50 else '#F39C12' if x < 70 else '#2ECC71' for x in low_child['age_0_5_percentage']]

ax.barh(y_pos, low_child['age_0_5_percentage'], color=colors_risk, edgecolor='black', linewidth=1.5)
ax.set_yticks(y_pos)
ax.set_yticklabels([s.title() for s in low_child['state']], fontsize=10)
ax.set_xlabel('Child Enrolment (%)', fontsize=14, fontweight='bold')
ax.set_title('Child Enrolment Gap - Bottom 20 States', fontsize=16, fontweight='bold')
ax.axvline(50, color='red', linestyle='--', linewidth=2, label='Critical (50%)')
ax.axvline(70, color='orange', linestyle='--', linewidth=2, label='Warning (70%)')
ax.legend(fontsize=11)
ax.grid(axis='x', alpha=0.3)

for i, v in enumerate(low_child['age_0_5_percentage']):
    ax.text(v + 1, i, f'{v:.1f}%', va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_05_child_gap.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 6: Biometric Compliance
print("🎨 Dashboard 6: Biometric Compliance...")
fig, ax = plt.subplots(figsize=(18, 10))
comp_data = step6_state[['state', 'bio_update_rate']].sort_values('bio_update_rate', ascending=True)

y_pos = np.arange(len(comp_data))
colors_comp = plt.cm.RdYlGn(comp_data['bio_update_rate'] / comp_data['bio_update_rate'].max())

ax.barh(y_pos, comp_data['bio_update_rate'], color=colors_comp, edgecolor='black', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels([s.title() for s in comp_data['state']], fontsize=8)
ax.set_xlabel('Biometric Update Rate (%)', fontsize=14, fontweight='bold')
ax.set_title('Biometric Compliance Scorecard - All States', fontsize=16, fontweight='bold')
ax.axvline(comp_data['bio_update_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
          label=f'National Avg ({comp_data["bio_update_rate"].mean():.1f}%)')
ax.legend(fontsize=12)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_06_compliance.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 7: Anomaly Detection
print("🎨 Dashboard 7: Anomaly Detection...")
fig, ax = plt.subplots(figsize=(16, 10))
anom_data = step9_anom[['state', 'anomaly_count', 'iso_forest_anomaly', 'zscore_anomaly', 'temporal_anomaly']].sort_values('anomaly_count', ascending=False).head(20)

x = np.arange(len(anom_data))
iso = anom_data['iso_forest_anomaly'].astype(int)
z = anom_data['zscore_anomaly'].astype(int)
temp = anom_data['temporal_anomaly'].astype(int)

ax.bar(x, iso, 0.2, label='Isolation Forest', color='#FF6B6B', edgecolor='black')
ax.bar(x, z, 0.2, bottom=iso, label='Z-Score', color='#4ECDC4', edgecolor='black')
ax.bar(x, temp, 0.2, bottom=iso+z, label='Temporal', color='#45B7D1', edgecolor='black')

ax.set_xlabel('State', fontsize=14, fontweight='bold')
ax.set_ylabel('Anomaly Techniques', fontsize=14, fontweight='bold')
ax.set_title('Anomaly Detection - Top 20 States', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([s.title() for s in anom_data['state']], rotation=45, ha='right', fontsize=9)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(['0', '1', '2', '3 (High)'])
ax.legend(fontsize=12)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_07_anomalies.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 8: Capacity Planning
print("🎨 Dashboard 8: Capacity Planning...")
fig, ax = plt.subplots(figsize=(16, 10))
cap_data = step10_cap.sort_values('enrol_growth_pct', ascending=True)

x = np.arange(len(cap_data))
width = 0.35

ax.barh(x - width/2, cap_data['enrol_growth_pct'], width, label='Enrolment Growth', color='#4A90E2', edgecolor='black', linewidth=1.5)
ax.barh(x + width/2, cap_data['bio_growth_pct'], width, label='Biometric Growth', color='#50C878', edgecolor='black', linewidth=1.5)

ax.set_yticks(x)
ax.set_yticklabels([s.title() for s in cap_data['state']], fontsize=9)
ax.set_xlabel('Growth Rate (%)', fontsize=14, fontweight='bold')
ax.set_title('Capacity Planning - 12-Week Forecast', fontsize=16, fontweight='bold')
ax.axvline(0, color='black', linewidth=1)
ax.axvline(20, color='red', linestyle='--', linewidth=2, label='High Growth (20%)')
ax.axvline(-10, color='orange', linestyle='--', linewidth=2, label='Decline (-10%)')
ax.legend(fontsize=11)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_08_capacity.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 9: Bottleneck Prediction
print("🎨 Dashboard 9: Bottleneck Prediction...")
fig, ax = plt.subplots(figsize=(16, 10))
bot_data = step11_bot.sort_values('bottleneck_probability', ascending=False)

y_pos = np.arange(len(bot_data))
colors_bot = ['#E74C3C' if x > 0.7 else '#F39C12' if x > 0.5 else '#2ECC71' for x in bot_data['bottleneck_probability']]

ax.barh(y_pos, bot_data['bottleneck_probability'] * 100, color=colors_bot, edgecolor='black', linewidth=1.5)
ax.set_yticks(y_pos)
ax.set_yticklabels([s.title() for s in bot_data['state']], fontsize=9)
ax.set_xlabel('Bottleneck Probability (%)', fontsize=14, fontweight='bold')
ax.set_title('ML-Based Bottleneck Prediction', fontsize=16, fontweight='bold')
ax.axvline(50, color='orange', linestyle='--', linewidth=2, label='Medium Risk (50%)')
ax.axvline(70, color='red', linestyle='--', linewidth=2, label='High Risk (70%)')
ax.legend(fontsize=11)
ax.grid(axis='x', alpha=0.3)

for i, v in enumerate(bot_data['bottleneck_probability'] * 100):
    ax.text(v + 1, i, f'{v:.1f}%', va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_09_bottleneck.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

# DASHBOARD 10: Age Targeting
print("🎨 Dashboard 10: Age Group Targeting...")
fig, ax = plt.subplots(figsize=(18, 10))

states = step11_age['state'].unique()
x = np.arange(len(states))
width = 0.25

age_0_5 = []
age_5_17 = []
age_18 = []

for state in states:
    data = step11_age[step11_age['state'] == state]
    age_0_5.append(data[data['age_group'] == 'age_0_5']['priority_score'].values[0] if len(data[data['age_group'] == 'age_0_5']) > 0 else 0)
    age_5_17.append(data[data['age_group'] == 'age_5_17']['priority_score'].values[0] if len(data[data['age_group'] == 'age_5_17']) > 0 else 0)
    age_18.append(data[data['age_group'] == 'age_18_greater']['priority_score'].values[0] if len(data[data['age_group'] == 'age_18_greater']) > 0 else 0)

ax.bar(x - width, age_0_5, width, label='Age 0-5', color='#FF6B6B', edgecolor='black', linewidth=1.5)
ax.bar(x, age_5_17, width, label='Age 5-17', color='#4ECDC4', edgecolor='black', linewidth=1.5)
ax.bar(x + width, age_18, width, label='Age 18+', color='#45B7D1', edgecolor='black', linewidth=1.5)

ax.set_xlabel('State', fontsize=14, fontweight='bold')
ax.set_ylabel('Priority Score', fontsize=14, fontweight='bold')
ax.set_title('Age Group Targeting - ML-Based Campaign Prioritization', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([s.title() for s in states], rotation=45, ha='right', fontsize=9)
ax.legend(fontsize=12)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/DASHBOARD_10_age_targeting.png', dpi=300, bbox_inches='tight')
print("✓ Saved")
plt.close()

print()
print("=" * 100)
print("✅ STEP 12 COMPLETE!")
print("=" * 100)
print()
print("📁 Created 10 professional dashboards (300 DPI):")
print("   1. State Update Rate Heatmap")
print("   2. Enrolment Trends")
print("   3. Biometric Update Trends")
print("   4. Age Group Distribution")
print("   5. Child Enrolment Gap")
print("   6. Biometric Compliance")
print("   7. Anomaly Detection")
print("   8. Capacity Planning")
print("   9. Bottleneck Prediction")
print("   10. Age Group Targeting")
print()
print("✓ All saved in visualizations/ directory")
print("✓ Ready for hackathon PDF!")
print("=" * 100)
