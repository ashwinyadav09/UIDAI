"""
STEP 11: XGBoost Model Visualizations
======================================
Professional visualizations for XGBoost model results

Creates:
1. Bottleneck prediction heatmap
2. Feature importance charts
3. Age group targeting matrix
4. Capacity planning dashboard
5. Model performance metrics

Author: Professional ML/Data Science Engineer
"""

import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the PROJECT directory (parent of src)
PROJECT_PATH = os.path.dirname(SCRIPT_DIR)

import pandas as pd


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from matplotlib.gridspec import GridSpec
import warnings


warnings.filterwarnings('ignore')

# Professional styling
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

print("=" * 100)
print("STEP 11: CREATING XGBOOST MODEL VISUALIZATIONS")
print("=" * 100)
print()

# ============================================================================
# LOAD DATA
# ============================================================================
print("📂 Loading model results...")

bottleneck_pred = pd.read_csv(os.path.join(PROJECT_PATH, 'results', 'STEP11_bottleneck_predictions.csv'))
age_targeting = pd.read_csv(os.path.join(PROJECT_PATH, 'results', 'STEP11_age_group_targeting.csv'))
capacity_pred = pd.read_csv(os.path.join(PROJECT_PATH, 'results', 'STEP11_capacity_predictions.csv'))
feature_importance = pd.read_csv(os.path.join(PROJECT_PATH, 'results', 'STEP11_feature_importance.csv'))

print("✓ Data loaded successfully!")
print()

# ============================================================================
# VIZ 1: BOTTLENECK PREDICTION HEATMAP
# ============================================================================
print("📊 Creating Visualization 1: Bottleneck Prediction Heatmap...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Sort by bottleneck probability
bottleneck_sorted = bottleneck_pred.sort_values('bottleneck_probability', ascending=False)

# Plot 1: Bottleneck Probability
colors = ['#DC2F02' if x == 1 else '#0077B6' for x in bottleneck_sorted['is_bottleneck']]
bars1 = ax1.barh(bottleneck_sorted['state'], bottleneck_sorted['bottleneck_probability'], 
                 color=colors, alpha=0.8)

ax1.set_xlabel('Bottleneck Probability', fontsize=14, fontweight='bold')
ax1.set_ylabel('State', fontsize=14, fontweight='bold')
ax1.set_title('XGBoost Bottleneck Prediction\nProbability by State', 
              fontsize=16, fontweight='bold', pad=20)
ax1.axvline(0.5, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Decision Threshold')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (idx, row) in enumerate(bottleneck_sorted.iterrows()):
    value = row['bottleneck_probability']
    ax1.text(value + 0.02, i, f'{value:.2f}', va='center', fontsize=9, fontweight='bold')

# Plot 2: Demand Score vs Bottleneck Prediction
scatter_colors = ['#DC2F02' if x == 1 else '#0077B6' for x in bottleneck_pred['is_bottleneck']]
ax2.scatter(bottleneck_pred['demand_score'], bottleneck_pred['bottleneck_probability'],
            c=scatter_colors, s=200, alpha=0.6, edgecolors='black', linewidth=1.5)

ax2.set_xlabel('Demand Score (%)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Bottleneck Probability', fontsize=14, fontweight='bold')
ax2.set_title('Demand Score vs Bottleneck Prediction', fontsize=16, fontweight='bold', pad=20)
ax2.axhline(0.5, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax2.grid(True, alpha=0.3)

# Add state labels for high-risk states
for idx, row in bottleneck_pred.iterrows():
    if row['is_bottleneck'] == 1 and row['demand_score'] > 100:
        ax2.annotate(row['state'], (row['demand_score'], row['bottleneck_probability']),
                    xytext=(10, 10), textcoords='offset points', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP11_1_bottleneck_prediction.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP11_1_bottleneck_prediction.png")

# ============================================================================
# VIZ 2: AGE GROUP TARGETING MATRIX
# ============================================================================
print("📊 Creating Visualization 2: Age Group Targeting Matrix...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# Create pivot table for heatmap
pivot_compliance = age_targeting.pivot(index='state', columns='age_group', values='compliance_rate')
pivot_priority = age_targeting.pivot(index='state', columns='age_group', values='campaign_priority')

# Plot 1: Compliance Rate Heatmap
sns.heatmap(pivot_compliance, annot=True, fmt='.1f', cmap='RdYlGn', center=50,
            cbar_kws={'label': 'Compliance Rate (%)'}, linewidths=0.5, ax=ax1)
ax1.set_title('Age Group Compliance Rates by State\n(Higher is Better)', 
              fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel('Age Group', fontsize=12, fontweight='bold')
ax1.set_ylabel('State', fontsize=12, fontweight='bold')

# Plot 2: Campaign Priority Heatmap
sns.heatmap(pivot_priority, annot=True, fmt='.0f', cmap='YlOrRd',
            cbar_kws={'label': 'Campaign Priority Score'}, linewidths=0.5, ax=ax2)
ax2.set_title('Targeted Campaign Priority by State-Age Group\n(Higher = More Urgent)', 
              fontsize=16, fontweight='bold', pad=20)
ax2.set_xlabel('Age Group', fontsize=12, fontweight='bold')
ax2.set_ylabel('State', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP11_2_age_group_targeting.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP11_2_age_group_targeting.png")

# ============================================================================
# VIZ 3: CAPACITY PLANNING DASHBOARD
# ============================================================================
print("📊 Creating Visualization 3: Capacity Planning Dashboard...")

fig = plt.figure(figsize=(22, 12))
gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

# Panel 1: Current vs Required Capacity
ax1 = fig.add_subplot(gs[0, 0])
capacity_sorted = capacity_pred.sort_values('capacity_gap', ascending=False).head(10)

x = np.arange(len(capacity_sorted))
width = 0.35

bars1 = ax1.bar(x - width/2, capacity_sorted['last_actual_avg'], width, 
                label='Current Capacity', color='#0077B6', alpha=0.8)
bars2 = ax1.bar(x + width/2, capacity_sorted['predicted_capacity'], width,
                label='Required Capacity', color='#DC2F02', alpha=0.8)

ax1.set_xlabel('State', fontsize=12, fontweight='bold')
ax1.set_ylabel('Weekly Update Capacity', fontsize=12, fontweight='bold')
ax1.set_title('Top 10 States: Current vs Required Capacity', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(capacity_sorted['state'], rotation=45, ha='right')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')

# Panel 2: Capacity Gap Percentage
ax2 = fig.add_subplot(gs[0, 1])
capacity_gap_sorted = capacity_pred.sort_values('capacity_gap_pct', ascending=True)
colors_gap = ['#DC2F02' if x > 0 else '#06A77D' for x in capacity_gap_sorted['capacity_gap_pct']]

bars = ax2.barh(capacity_gap_sorted['state'], capacity_gap_sorted['capacity_gap_pct'],
                color=colors_gap, alpha=0.8)

ax2.set_xlabel('Capacity Gap (%)', fontsize=12, fontweight='bold')
ax2.set_ylabel('State', fontsize=12, fontweight='bold')
ax2.set_title('Capacity Gap Analysis\n(Positive = Expansion Needed)', 
              fontsize=14, fontweight='bold')
ax2.axvline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (idx, row) in enumerate(capacity_gap_sorted.iterrows()):
    value = row['capacity_gap_pct']
    ax2.text(value + 50, i, f'{value:+.0f}%', va='center', fontsize=9, fontweight='bold')

# Panel 3: Scatter - Demand Score vs Capacity Gap
ax3 = fig.add_subplot(gs[1, 0])
scatter_colors = ['#DC2F02' if x > 0 else '#06A77D' for x in capacity_pred['capacity_gap']]
ax3.scatter(capacity_pred['demand_score'], capacity_pred['capacity_gap'],
            c=scatter_colors, s=250, alpha=0.6, edgecolors='black', linewidth=1.5)

ax3.set_xlabel('Demand Score (%)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Capacity Gap (Updates/Week)', fontsize=12, fontweight='bold')
ax3.set_title('Demand Score vs Capacity Gap', fontsize=14, fontweight='bold')
ax3.axhline(0, color='black', linestyle='--', linewidth=1)
ax3.grid(True, alpha=0.3)

# Add labels for extreme cases
for idx, row in capacity_pred.iterrows():
    if abs(row['capacity_gap']) > 50000 or abs(row['demand_score']) > 200:
        ax3.annotate(row['state'], (row['demand_score'], row['capacity_gap']),
                    xytext=(10, 10), textcoords='offset points', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

# Panel 4: Investment Priority Ranking
ax4 = fig.add_subplot(gs[1, 1])
top_investment = capacity_pred.nlargest(10, 'capacity_gap')[['state', 'capacity_gap']]

bars = ax4.barh(top_investment['state'], top_investment['capacity_gap'],
                color='#F18F01', alpha=0.8)

ax4.set_xlabel('Capacity Gap (Updates/Week)', fontsize=12, fontweight='bold')
ax4.set_ylabel('State', fontsize=12, fontweight='bold')
ax4.set_title('Top 10 Infrastructure Investment Priorities', fontsize=14, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (idx, row) in enumerate(top_investment.iterrows()):
    value = row['capacity_gap']
    ax4.text(value + 1000, i, f'{value:,.0f}', va='center', fontsize=9, fontweight='bold')

plt.suptitle('XGBoost Capacity Planning Dashboard\nData-Driven Infrastructure Investment Analysis', 
             fontsize=18, fontweight='bold', y=0.995)
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP11_3_capacity_planning_dashboard.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP11_3_capacity_planning_dashboard.png")

# ============================================================================
# VIZ 4: TOP CAMPAIGN TARGETS
# ============================================================================
print("📊 Creating Visualization 4: Top Campaign Targets...")

fig, ax = plt.subplots(figsize=(16, 10))

# Get top 15 campaign targets
top_campaigns = age_targeting.nlargest(15, 'campaign_priority')

# Create labels
labels = [f"{row['state']} - Age {row['age_group']}" for idx, row in top_campaigns.iterrows()]

# Plot
bars = ax.barh(labels, top_campaigns['campaign_priority'], color='#F77F00', alpha=0.8)

ax.set_xlabel('Campaign Priority Score', fontsize=14, fontweight='bold')
ax.set_ylabel('State - Age Group', fontsize=14, fontweight='bold')
ax.set_title('Top 15 Targeted Campaign Recommendations\nXGBoost Age Group Targeting Model', 
             fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='x')

# Add value labels and compliance rates
for i, (idx, row) in enumerate(top_campaigns.iterrows()):
    value = row['campaign_priority']
    compliance = row['compliance_rate']
    ax.text(value + 50, i, f'{value:.0f} (Compliance: {compliance:.1f}%)', 
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP11_4_campaign_targets.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP11_4_campaign_targets.png")

# ============================================================================
# VIZ 5: COMPREHENSIVE SUMMARY DASHBOARD
# ============================================================================
print("📊 Creating Visualization 5: Comprehensive Summary Dashboard...")

fig = plt.figure(figsize=(24, 14))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: Bottleneck Distribution
ax1 = fig.add_subplot(gs[0, 0])
bottleneck_counts = bottleneck_pred['is_bottleneck'].value_counts()
colors_pie = ['#DC2F02', '#06A77D']
ax1.pie(bottleneck_counts.values, labels=['Bottleneck', 'Non-Bottleneck'], 
        autopct='%1.1f%%', colors=colors_pie, startangle=90)
ax1.set_title('Bottleneck State Distribution', fontsize=14, fontweight='bold')

# Panel 2: Average Compliance by Age Group
ax2 = fig.add_subplot(gs[0, 1])
avg_compliance = age_targeting.groupby('age_group')['compliance_rate'].mean().sort_values()
bars = ax2.bar(avg_compliance.index, avg_compliance.values, color='#2E86AB', alpha=0.8)
ax2.set_xlabel('Age Group', fontsize=11, fontweight='bold')
ax2.set_ylabel('Average Compliance Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Average Compliance by Age Group', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, (age, val) in enumerate(avg_compliance.items()):
    ax2.text(i, val + 1, f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')

# Panel 3: Key Metrics Summary
ax3 = fig.add_subplot(gs[0, 2])
ax3.axis('off')

bottleneck_states = bottleneck_pred[bottleneck_pred['is_bottleneck'] == 1]
high_priority_campaigns = age_targeting[age_targeting['campaign_priority'] > 50]
high_capacity_gap = capacity_pred[capacity_pred['capacity_gap'] > 10000]

summary_text = "📊 KEY METRICS SUMMARY\n\n"
summary_text += f"🔴 Bottleneck States: {len(bottleneck_states)}\n\n"
summary_text += f"🎯 High Priority Campaigns: {len(high_priority_campaigns)}\n\n"
summary_text += f"📈 States Needing Capacity: {len(high_capacity_gap)}\n\n"
summary_text += f"📍 Total States Analyzed: {len(bottleneck_pred)}\n\n"
summary_text += f"👥 Age Groups Analyzed: {age_targeting['age_group'].nunique()}\n\n"

ax3.text(0.1, 0.9, summary_text, fontsize=13, verticalalignment='top', 
         family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax3.set_title('XGBoost Model Summary', fontsize=14, fontweight='bold')

# Panels 4-6: Top 3 Bottleneck States Details
top_3_bottleneck = bottleneck_pred.nlargest(3, 'demand_score')

for i, (idx, state_row) in enumerate(top_3_bottleneck.iterrows()):
    ax = fig.add_subplot(gs[1, i])
    
    state_name = state_row['state']
    
    # Get metrics for this state
    metrics = {
        'Demand Score': state_row['demand_score'],
        'Enrol Growth (3M)': state_row['growth_3m_enrol'],
        'Bio Growth (3M)': state_row['growth_3m_bio'],
        'Bottleneck Prob': state_row['bottleneck_probability'] * 100
    }
    
    bars = ax.barh(list(metrics.keys()), list(metrics.values()), color='#F18F01', alpha=0.8)
    ax.set_xlabel('Value', fontsize=10, fontweight='bold')
    ax.set_title(f'{state_name.title()}\nBottleneck Analysis', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for j, (metric, value) in enumerate(metrics.items()):
        ax.text(value + 10, j, f'{value:.1f}', va='center', fontsize=9, fontweight='bold')

# Panels 7-9: Top 3 Campaign Priority States
top_3_campaigns_states = age_targeting.nlargest(3, 'campaign_priority')

for i, (idx, campaign_row) in enumerate(top_3_campaigns_states.iterrows()):
    ax = fig.add_subplot(gs[2, i])
    
    state_name = campaign_row['state']
    age_group = campaign_row['age_group']
    
    metrics = {
        'Current Compliance': campaign_row['compliance_rate'],
        'Predicted Compliance': campaign_row['predicted_compliance'],
        'Campaign Priority': campaign_row['campaign_priority'],
        'Enrolments': campaign_row['enrolments'] / 1000  # In thousands
    }
    
    bars = ax.barh(list(metrics.keys()), list(metrics.values()), color='#06A77D', alpha=0.8)
    ax.set_xlabel('Value', fontsize=10, fontweight='bold')
    ax.set_title(f'{state_name.title()} - Age {age_group}\nCampaign Target', 
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for j, (metric, value) in enumerate(metrics.items()):
        if 'Enrolments' in metric:
            ax.text(value + 1, j, f'{value:.0f}K', va='center', fontsize=9, fontweight='bold')
        else:
            ax.text(value + 1, j, f'{value:.1f}', va='center', fontsize=9, fontweight='bold')

plt.suptitle('UIDAI XGBoost Predictive Models - Comprehensive Dashboard\nBottleneck Prediction | Campaign Targeting | Capacity Planning', 
             fontsize=20, fontweight='bold', y=0.998)
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP11_5_comprehensive_dashboard.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP11_5_comprehensive_dashboard.png")

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 100)
print("✅ ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
print("=" * 100)
print()
print("📁 FILES CREATED:")
print("   ✓ STEP11_1_bottleneck_prediction.png")
print("   ✓ STEP11_2_age_group_targeting.png")
print("   ✓ STEP11_3_capacity_planning_dashboard.png")
print("   ✓ STEP11_4_campaign_targets.png")
print("   ✓ STEP11_5_comprehensive_dashboard.png")
print()
print("🎯 READY FOR HACKATHON SUBMISSION!")
print("   These visualizations demonstrate:")
print("   • XGBoost-based bottleneck prediction")
print("   • Data-driven campaign targeting by age group")
print("   • Capacity planning with infrastructure priorities")
print("   • Actionable insights for UIDAI decision-making")
print("=" * 100)
