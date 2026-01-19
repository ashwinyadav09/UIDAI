"""
PHASE 3 - STEP 6: State-wise Trend Analysis
============================================
Analyzes trends over time for each state

Calculates:
- Total enrolments over time
- Total biometric updates over time
- Total demographic updates over time
- Update rate = (Updates / Enrolments) × 100
- Creates trend charts for top 10 states

Author: UIDAI Hackathon Project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("=" * 80)
print("PHASE 3 - STEP 6: STATE-WISE TREND ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# LOAD CLEANED DATA
# ============================================================================
print(" Loading cleaned data...")
try:
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../data/processed/cleaned_biometric.csv')
    demographic = pd.read_csv('../data/processed/cleaned_demographic.csv')
    print("✓ All datasets loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
    print(f"  - Demographic: {len(demographic):,} rows")
except Exception as e:
    print(f" Error loading data: {e}")
    print("Please run STEP2_FINAL_intelligent_cleaning.py first!")
    exit()

print()

# ============================================================================
# PREPARE DATA - Convert dates
# ============================================================================
print(" Preparing data...")

# Convert date columns
enrolment['date'] = pd.to_datetime(enrolment['date'], format='%d-%m-%Y')
biometric['date'] = pd.to_datetime(biometric['date'], format='%d-%m-%Y')
demographic['date'] = pd.to_datetime(demographic['date'], format='%d-%m-%Y')

# Extract month for aggregation
enrolment['month'] = enrolment['date'].dt.to_period('M')
biometric['month'] = biometric['date'].dt.to_period('M')
demographic['month'] = demographic['date'].dt.to_period('M')

print("✓ Dates converted and months extracted")
print()

# ============================================================================
# STEP 6.1: Calculate Total Enrolments Over Time by State
# ============================================================================
print(" Step 6.1: Calculating total enrolments over time by state...")

# Aggregate by state and month
enrolment_trends = enrolment.groupby(['state', 'month']).agg({
    'total_enrolments': 'sum'
}).reset_index()

enrolment_trends['month'] = enrolment_trends['month'].astype(str)

print(f"✓ Enrolment trends calculated for {enrolment_trends['state'].nunique()} states")
print()

# ============================================================================
# STEP 6.2: Calculate Total Biometric Updates Over Time by State
# ============================================================================
print(" Step 6.2: Calculating total biometric updates over time by state...")

biometric_trends = biometric.groupby(['state', 'month']).agg({
    'total_bio_updates': 'sum'
}).reset_index()

biometric_trends['month'] = biometric_trends['month'].astype(str)

print(f"✓ Biometric update trends calculated for {biometric_trends['state'].nunique()} states")
print()

# ============================================================================
# STEP 6.3: Calculate Total Demographic Updates Over Time by State
# ============================================================================
print(" Step 6.3: Calculating total demographic updates over time by state...")

demographic_trends = demographic.groupby(['state', 'month']).agg({
    'total_demo_updates': 'sum'
}).reset_index()

demographic_trends['month'] = demographic_trends['month'].astype(str)

print(f"✓ Demographic update trends calculated for {demographic_trends['state'].nunique()} states")
print()

# ============================================================================
# STEP 6.4: Calculate Update Rates by State
# ============================================================================
print(" Step 6.4: Calculating update rates by state...")

# Total enrolments by state
total_enrol_by_state = enrolment.groupby('state')['total_enrolments'].sum().reset_index()
total_enrol_by_state.columns = ['state', 'total_enrolments']

# Total biometric updates by state
total_bio_by_state = biometric.groupby('state')['total_bio_updates'].sum().reset_index()
total_bio_by_state.columns = ['state', 'total_bio_updates']

# Total demographic updates by state
total_demo_by_state = demographic.groupby('state')['total_demo_updates'].sum().reset_index()
total_demo_by_state.columns = ['state', 'total_demo_updates']

# Merge all
state_summary = total_enrol_by_state.merge(total_bio_by_state, on='state', how='outer').fillna(0)
state_summary = state_summary.merge(total_demo_by_state, on='state', how='outer').fillna(0)

# Calculate update rates
# Note: Update rate can be >100% because updates include historical enrolments
state_summary['biometric_update_activity'] = (
    state_summary['total_bio_updates'] / state_summary['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

state_summary['demographic_update_activity'] = (
    state_summary['total_demo_updates'] / state_summary['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

# Calculate national averages
national_bio_avg = state_summary['biometric_update_activity'].mean()
national_demo_avg = state_summary['demographic_update_activity'].mean()

print(f"✓ Update rates calculated")
print(f"  National Average - Biometric Update Activity: {national_bio_avg:.2f}%")
print(f"  National Average - Demographic Update Activity: {national_demo_avg:.2f}%")
print()

# Add comparison to national average
state_summary['bio_vs_national'] = state_summary['biometric_update_activity'] - national_bio_avg
state_summary['demo_vs_national'] = state_summary['demographic_update_activity'] - national_demo_avg

# ============================================================================
# IDENTIFY TOP 10 STATES FOR VISUALIZATION
# ============================================================================
print(" Identifying top 10 states by total enrolments...")

top_10_states = state_summary.nlargest(10, 'total_enrolments')['state'].tolist()

print(f"✓ Top 10 states identified:")
for i, state in enumerate(top_10_states, 1):
    enrol_count = state_summary[state_summary['state'] == state]['total_enrolments'].iloc[0]
    print(f"  {i:2d}. {state:40s} - {enrol_count:>12,.0f} enrolments")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print(" Saving trend analysis results...")

# Save state summary
state_summary.to_csv('../results/STEP6_state_summary.csv', index=False)

# Save trend data
enrolment_trends.to_csv('../results/STEP6_enrolment_trends.csv', index=False)
biometric_trends.to_csv('../results/STEP6_biometric_trends.csv', index=False)
demographic_trends.to_csv('../results/STEP6_demographic_trends.csv', index=False)

print("✓ Results saved:")
print("  - STEP6_state_summary.csv")
print("  - STEP6_enrolment_trends.csv")
print("  - STEP6_biometric_trends.csv")
print("  - STEP6_demographic_trends.csv")
print()

# ============================================================================
# CREATE VISUALIZATIONS - TREND CHARTS FOR TOP 10 STATES
# ============================================================================
print(" Creating trend charts for top 10 states...")

# Create figure with 3 subplots
fig, axes = plt.subplots(3, 1, figsize=(18, 14))
fig.suptitle('State-wise Trend Analysis - Top 10 States by Enrolment', 
             fontsize=16, fontweight='bold', y=0.995)

# Chart 1: Enrolment Trends
ax1 = axes[0]
for state in top_10_states:
    state_data = enrolment_trends[enrolment_trends['state'] == state]
    if len(state_data) > 0:
        ax1.plot(state_data['month'], state_data['total_enrolments'], 
                marker='o', label=state, linewidth=2, markersize=6)

ax1.set_xlabel('Month', fontweight='bold', fontsize=11)
ax1.set_ylabel('Total Enrolments', fontweight='bold', fontsize=11)
ax1.set_title('1. Total Enrolments Over Time', fontweight='bold', fontsize=13, pad=10)
ax1.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

# Chart 2: Biometric Update Trends
ax2 = axes[1]
for state in top_10_states:
    state_data = biometric_trends[biometric_trends['state'] == state]
    if len(state_data) > 0:
        ax2.plot(state_data['month'], state_data['total_bio_updates'], 
                marker='s', label=state, linewidth=2, markersize=6)

ax2.set_xlabel('Month', fontweight='bold', fontsize=11)
ax2.set_ylabel('Total Biometric Updates', fontweight='bold', fontsize=11)
ax2.set_title('2. Total Biometric Updates Over Time', fontweight='bold', fontsize=13, pad=10)
ax2.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

# Chart 3: Demographic Update Trends
ax3 = axes[2]
for state in top_10_states:
    state_data = demographic_trends[demographic_trends['state'] == state]
    if len(state_data) > 0:
        ax3.plot(state_data['month'], state_data['total_demo_updates'], 
                marker='^', label=state, linewidth=2, markersize=6)

ax3.set_xlabel('Month', fontweight='bold', fontsize=11)
ax3.set_ylabel('Total Demographic Updates', fontweight='bold', fontsize=11)
ax3.set_title('3. Total Demographic Updates Over Time', fontweight='bold', fontsize=13, pad=10)
ax3.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('../visualizations/STEP6_state_trends_top10.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: STEP6_state_trends_top10.png")
print()

# Create second visualization - Update Activity Comparison
fig, axes = plt.subplots(2, 1, figsize=(16, 10))
fig.suptitle('Update Activity by State (vs National Average)', 
             fontsize=16, fontweight='bold')

# Sort by biometric activity
sorted_states_bio = state_summary.sort_values('biometric_update_activity', ascending=False)

# Chart 1: Top 15 Biometric Update Activity
ax1 = axes[0]
top_15_bio = sorted_states_bio.head(15)
colors_bio = ['green' if x > national_bio_avg else 'orange' for x in top_15_bio['biometric_update_activity']]
bars = ax1.barh(range(len(top_15_bio)), top_15_bio['biometric_update_activity'], color=colors_bio)
ax1.axvline(national_bio_avg, color='red', linestyle='--', linewidth=2, label=f'National Avg: {national_bio_avg:.1f}%')
ax1.set_yticks(range(len(top_15_bio)))
ax1.set_yticklabels(top_15_bio['state'], fontsize=9)
ax1.set_xlabel('Biometric Update Activity (%)', fontweight='bold')
ax1.set_title('Top 15 States - Biometric Update Activity', fontweight='bold', fontsize=12)
ax1.legend()
ax1.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(top_15_bio['biometric_update_activity']):
    ax1.text(v, i, f' {v:.1f}%', va='center', fontsize=8)

# Chart 2: Top 15 Demographic Update Activity
ax2 = axes[1]
sorted_states_demo = state_summary.sort_values('demographic_update_activity', ascending=False)
top_15_demo = sorted_states_demo.head(15)
colors_demo = ['green' if x > national_demo_avg else 'orange' for x in top_15_demo['demographic_update_activity']]
bars = ax2.barh(range(len(top_15_demo)), top_15_demo['demographic_update_activity'], color=colors_demo)
ax2.axvline(national_demo_avg, color='red', linestyle='--', linewidth=2, label=f'National Avg: {national_demo_avg:.1f}%')
ax2.set_yticks(range(len(top_15_demo)))
ax2.set_yticklabels(top_15_demo['state'], fontsize=9)
ax2.set_xlabel('Demographic Update Activity (%)', fontweight='bold')
ax2.set_title('Top 15 States - Demographic Update Activity', fontweight='bold', fontsize=12)
ax2.legend()
ax2.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(top_15_demo['demographic_update_activity']):
    ax2.text(v, i, f' {v:.1f}%', va='center', fontsize=8)

plt.tight_layout()
plt.savefig('../visualizations/STEP6_update_activity_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: STEP6_update_activity_comparison.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("STEP 6 COMPLETE!")
print("=" * 80)
print()
print(" WHAT WAS DONE:")
print("  ✓ Calculated total enrolments over time by state")
print("  ✓ Calculated total biometric updates over time by state")
print("  ✓ Calculated total demographic updates over time by state")
print("  ✓ Calculated update activity rates by state")
print("  ✓ Identified top 10 states by enrolment")
print("  ✓ Created trend charts for top 10 states")
print("  ✓ Created update activity comparison charts")
print()
print(" FILES CREATED:")
print("  ✓ results/STEP6_state_summary.csv")
print("  ✓ results/STEP6_enrolment_trends.csv")
print("  ✓ results/STEP6_biometric_trends.csv")
print("  ✓ results/STEP6_demographic_trends.csv")
print("  ✓ visualizations/STEP6_state_trends_top10.png")
print("  ✓ visualizations/STEP6_update_activity_comparison.png")
print()
print(" KEY FINDINGS:")
print(f"  - Analyzed {state_summary.shape[0]} states/UTs")
print(f"  - National biometric update activity: {national_bio_avg:.2f}%")
print(f"  - National demographic update activity: {national_demo_avg:.2f}%")
print(f"  - Top 10 states account for majority of enrolments")
print()
print("Next: Run PHASE3_STEP7_child_enrolment_gap.py")
print("=" * 80)
