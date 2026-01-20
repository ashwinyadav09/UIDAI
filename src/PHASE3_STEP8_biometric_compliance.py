"""
PHASE 3 - STEP 8: Biometric Update Compliance Analysis
=======================================================
Analyzes biometric update compliance for critical ages (5 and 15)

Calculates:
- Age 5 compliance: % of 5-year-olds getting biometric updates
- Age 15 compliance: % of 15-year-olds getting biometric updates  
- Identifies states with low compliance
- Shows who might face service exclusion

Author: UIDAI Hackathon Project
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
import warnings


warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("=" * 80)
print("PHASE 3 - STEP 8: BIOMETRIC UPDATE COMPLIANCE ANALYSIS")
print("=" * 80)
print()
print("Critical Ages for Biometric Updates:")
print("  - Age 5:  First mandatory biometric update milestone")
print("  - Age 15: Second mandatory biometric update milestone")
print()

# ============================================================================
# LOAD CLEANED DATA
# ============================================================================
print(" Loading cleaned data...")
try:
    enrolment = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_enrolment.csv'))
    biometric = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_biometric.csv'))
    print("✓ Data loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
except Exception as e:
    print(f" Error loading data: {e}")
    print("Please run STEP2_FINAL_intelligent_cleaning.py first!")
    exit()

print()

# ============================================================================
# STEP 8.1: Aggregate Data by State
# ============================================================================
print(" Step 8.1: Aggregating enrolment and biometric update data by state...")

# Enrolment by state
enrol_by_state = enrolment.groupby('state').agg({
    'registrations_0_to_5': 'sum',
    'registrations_5_to_17': 'sum',
    'registrations_18_and_above': 'sum',
    'total_enrolments': 'sum'
}).reset_index()

# Biometric updates by state
bio_by_state = biometric.groupby('state').agg({
    'biometric_updates_5_to_17': 'sum',
    'biometric_updates_18_and_above': 'sum',
    'total_bio_updates': 'sum'
}).reset_index()

# Merge datasets
compliance = enrol_by_state.merge(bio_by_state, on='state', how='outer').fillna(0)

print(f"✓ Data aggregated for {len(compliance)} states")
print()

# ============================================================================
# STEP 8.2: Calculate Age 5 Compliance
# ============================================================================
print(" Step 8.2: Calculating Age 5 compliance (biometric update milestone)...")
print()

# Age 5 compliance calculation:
# We compare biometric updates for age 5-17 group against enrolments in 5-17 group
# This shows what % of children in that age bracket are getting biometric updates

compliance['age_5_17_update_rate'] = (
    compliance['biometric_updates_5_to_17'] / compliance['registrations_5_to_17'] * 100
).replace([np.inf, -np.inf], 0)

# Note: Since our data groups are 5-17, we calculate overall compliance for this group
# which includes both age 5 and age 15 milestones

print(" Age 5-17 Update Compliance:")
print(f"   Total children enrolled (5-17): {compliance['registrations_5_to_17'].sum():,.0f}")
print(f"   Total biometric updates (5-17): {compliance['biometric_updates_5_to_17'].sum():,.0f}")
print()

# ============================================================================
# STEP 8.3: Calculate Age 15 Compliance
# ============================================================================
print(" Step 8.3: Calculating Age 15 compliance (second biometric milestone)...")
print()

# Age 15 is within the 5-17 bracket, so we use the same metric
# The age_5_17_update_rate covers both critical ages (5 and 15)

compliance['child_compliance_rate'] = compliance['age_5_17_update_rate']

print(" Child Biometric Compliance (Ages 5-17, including both milestones):")
print(f"   Average update rate: {compliance['child_compliance_rate'].mean():.2f}%")
print()

# For comparison, calculate adult compliance
compliance['adult_update_rate'] = (
    compliance['biometric_updates_18_and_above'] / compliance['registrations_18_and_above'] * 100
).replace([np.inf, -np.inf], 0)

print(" Adult Biometric Compliance (Ages 18+) for comparison:")
print(f"   Average update rate: {compliance['adult_update_rate'].mean():.2f}%")
print()

# ============================================================================
# STEP 8.4: Calculate National Benchmarks
# ============================================================================
print("🇮🇳 Step 8.4: Calculating national benchmarks...")

# National child compliance
national_child_enrol = compliance['registrations_5_to_17'].sum()
national_child_updates = compliance['biometric_updates_5_to_17'].sum()
national_child_compliance = (national_child_updates / national_child_enrol * 100) if national_child_enrol > 0 else 0

# National adult compliance
national_adult_enrol = compliance['registrations_18_and_above'].sum()
national_adult_updates = compliance['biometric_updates_18_and_above'].sum()
national_adult_compliance = (national_adult_updates / national_adult_enrol * 100) if national_adult_enrol > 0 else 0

print(" National Benchmarks:")
print(f"  - Child (5-17) Compliance:  {national_child_compliance:.2f}%")
print(f"  - Adult (18+) Compliance:   {national_adult_compliance:.2f}%")
print(f"  - Child vs Adult Ratio:     {(national_child_compliance/national_adult_compliance if national_adult_compliance > 0 else 0):.2f}x")
print()

# ============================================================================
# STEP 8.5: Identify States with Low Compliance
# ============================================================================
print(" Step 8.5: Identifying states with low biometric compliance...")
print("   Using threshold: 70% of national child compliance")
print()

# Set threshold
threshold_compliance = national_child_compliance * 0.7

print(f"📏 Threshold: {threshold_compliance:.2f}% (70% of national avg)")
print()

# Calculate compliance gap
compliance['compliance_gap'] = national_child_compliance - compliance['child_compliance_rate']

# Flag low compliance states
compliance['low_compliance'] = compliance['child_compliance_rate'] < threshold_compliance

# Get low compliance states
low_compliance_states = compliance[compliance['low_compliance']].copy()

print(f" LOW COMPLIANCE STATES: {len(low_compliance_states)} states")
if len(low_compliance_states) > 0:
    print("\nStates with low biometric update compliance (Ages 5-17):")
    low_sorted = low_compliance_states.sort_values('child_compliance_rate')
    for idx, row in low_sorted.iterrows():
        gap = row['compliance_gap']
        rate = row['child_compliance_rate']
        child_count = row['registrations_5_to_17']
        print(f"  {row['state']:40s} → {rate:>7.2f}% (Gap: {gap:+.2f}%, {child_count:>10,.0f} children)")
else:
    print("  ✓ No states below threshold")
print()

# ============================================================================
# STEP 8.6: Identify Who Might Face Service Exclusion
# ============================================================================
print("  Step 8.6: Identifying children who might face service exclusion...")
print()

# Calculate children NOT getting updates
compliance['children_not_updated'] = compliance['registrations_5_to_17'] - compliance['biometric_updates_5_to_17']
compliance['children_not_updated'] = compliance['children_not_updated'].clip(lower=0)

# Calculate exclusion risk
compliance['exclusion_risk_percentage'] = (
    compliance['children_not_updated'] / compliance['registrations_5_to_17'] * 100
).replace([np.inf, -np.inf], 0)

# Sort by number of children at risk
high_risk_states = compliance.nlargest(15, 'children_not_updated')

print(" TOP 15 STATES - Children at Risk of Service Exclusion:")
print("   (States with highest number of children not getting biometric updates)")
print()
for idx, row in high_risk_states.iterrows():
    children_at_risk = row['children_not_updated']
    risk_pct = row['exclusion_risk_percentage']
    print(f"  {row['state']:40s} → {children_at_risk:>10,.0f} children ({risk_pct:>5.1f}% at risk)")
print()

# Total children at risk nationally
total_at_risk = compliance['children_not_updated'].sum()
total_children = compliance['registrations_5_to_17'].sum()
national_risk_pct = (total_at_risk / total_children * 100) if total_children > 0 else 0

print(f" NATIONAL SUMMARY:")
print(f"  - Total children (5-17): {total_children:,.0f}")
print(f"  - Children not updated: {total_at_risk:,.0f}")
print(f"  - % at risk of exclusion: {national_risk_pct:.2f}%")
print()

# ============================================================================
# STEP 8.7: Priority Categorization
# ============================================================================
print(" Step 8.7: Categorizing states by intervention priority...")

def get_compliance_priority(row, threshold):
    """Categorize compliance priority"""
    rate = row['child_compliance_rate']
    children_count = row['registrations_5_to_17']
    
    # Critical: Low compliance AND large population
    if rate < threshold * 0.5 and children_count > compliance['registrations_5_to_17'].median():
        return 'Critical (Low compliance + Large population)'
    # High: Low compliance
    elif rate < threshold:
        return 'High (Below compliance threshold)'
    # Medium: 70-100% of national average
    elif rate < national_child_compliance:
        return 'Medium (Below national average)'
    # Good: Above national average
    else:
        return 'Good (Above national average)'

compliance['priority'] = compliance.apply(lambda x: get_compliance_priority(x, threshold_compliance), axis=1)

priority_counts = compliance['priority'].value_counts()

print(" Priority Distribution:")
for priority, count in priority_counts.items():
    print(f"  {priority:50s}: {count:2d} states")
print()

# Get critical states
critical_states = compliance[compliance['priority'] == 'Critical (Low compliance + Large population)']

if len(critical_states) > 0:
    print(f" CRITICAL PRIORITY STATES: {len(critical_states)}")
    print("   States requiring URGENT intervention:")
    for idx, row in critical_states.iterrows():
        print(f"  {row['state']:40s} → {row['child_compliance_rate']:>6.2f}%, {row['registrations_5_to_17']:>10,.0f} children")
    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print(" Saving biometric compliance analysis...")

compliance.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP8_biometric_compliance_analysis.csv'), index=False)
low_compliance_states.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP8_low_compliance_states.csv'), index=False)
high_risk_states.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP8_high_exclusion_risk_states.csv'), index=False)
critical_states.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP8_critical_intervention_states.csv'), index=False)

print("✓ Results saved:")
print("  - STEP8_biometric_compliance_analysis.csv")
print("  - STEP8_low_compliance_states.csv")
print("  - STEP8_high_exclusion_risk_states.csv")
print("  - STEP8_critical_intervention_states.csv")
print()

# ============================================================================
# CREATE VISUALIZATIONS
# ============================================================================
print(" Creating compliance visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Biometric Update Compliance Analysis - Ages 5 & 15 (Critical Milestones)', 
             fontsize=16, fontweight='bold')

# Chart 1: Bottom 20 states - Child compliance
ax1 = axes[0, 0]
bottom_20 = compliance.nsmallest(20, 'child_compliance_rate')
colors_1 = ['red' if x else 'steelblue' for x in bottom_20['low_compliance']]
bars1 = ax1.barh(range(len(bottom_20)), bottom_20['child_compliance_rate'], color=colors_1)
ax1.axvline(national_child_compliance, color='green', linestyle='--', linewidth=2, 
           label=f'National Avg: {national_child_compliance:.1f}%')
ax1.axvline(threshold_compliance, color='orange', linestyle='--', linewidth=2, 
           label=f'Risk Threshold: {threshold_compliance:.1f}%')
ax1.set_yticks(range(len(bottom_20)))
ax1.set_yticklabels(bottom_20['state'], fontsize=8)
ax1.set_xlabel('Compliance Rate (%)', fontweight='bold')
ax1.set_title('Bottom 20 States - Child Biometric Update Compliance', fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(bottom_20['child_compliance_rate']):
    ax1.text(v, i, f' {v:.1f}%', va='center', fontsize=7)

# Chart 2: Priority distribution
ax2 = axes[0, 1]
colors_priority = {
    'Critical (Low compliance + Large population)': 'darkred',
    'High (Below compliance threshold)': 'red',
    'Medium (Below national average)': 'orange',
    'Good (Above national average)': 'green'
}
priority_data = compliance['priority'].value_counts()
bars2 = ax2.bar(range(len(priority_data)), priority_data.values,
               color=[colors_priority.get(x, 'gray') for x in priority_data.index])
ax2.set_xticks(range(len(priority_data)))
ax2.set_xticklabels(priority_data.index, rotation=15, ha='right', fontsize=8)
ax2.set_ylabel('Number of States', fontweight='bold')
ax2.set_title('Compliance Priority Distribution', fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(priority_data.values):
    ax2.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

# Chart 3: Child vs Adult compliance
ax3 = axes[1, 0]
top_15_pop = compliance.nlargest(15, 'registrations_5_to_17')
x = np.arange(len(top_15_pop))
width = 0.35
bars3a = ax3.barh(x - width/2, top_15_pop['child_compliance_rate'], width, 
                  label='Children (5-17)', color='steelblue')
bars3b = ax3.barh(x + width/2, top_15_pop['adult_update_rate'], width, 
                  label='Adults (18+)', color='coral')
ax3.set_yticks(x)
ax3.set_yticklabels(top_15_pop['state'], fontsize=8)
ax3.set_xlabel('Compliance Rate (%)', fontweight='bold')
ax3.set_title('Top 15 States by Child Population - Child vs Adult Compliance', fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(axis='x', alpha=0.3)

# Chart 4: Children at risk of exclusion
ax4 = axes[1, 1]
top_15_risk = compliance.nlargest(15, 'children_not_updated')
bars4 = ax4.barh(range(len(top_15_risk)), top_15_risk['children_not_updated'], color='red', alpha=0.7)
ax4.set_yticks(range(len(top_15_risk)))
ax4.set_yticklabels(top_15_risk['state'], fontsize=8)
ax4.set_xlabel('Number of Children Not Updated', fontweight='bold')
ax4.set_title('Top 15 States - Children at Risk of Service Exclusion', fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(top_15_risk['children_not_updated']):
    ax4.text(v, i, f' {v:,.0f}', va='center', fontsize=7)

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP8_biometric_compliance.png'), dpi=300, bbox_inches='tight')
print("✓ Visualization saved: STEP8_biometric_compliance.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print(" STEP 8 COMPLETE!")
print("=" * 80)
print()
print(" WHAT WAS DONE:")
print("  ✓ Calculated Age 5 compliance (5-17 age group)")
print("  ✓ Calculated Age 15 compliance (included in 5-17 group)")
print("  ✓ Identified states with low compliance")
print("  ✓ Calculated children at risk of service exclusion")
print("  ✓ Categorized states by intervention priority")
print("  ✓ Created comprehensive visualizations")
print()
print(" FILES CREATED:")
print("  ✓ results/STEP8_biometric_compliance_analysis.csv")
print("  ✓ results/STEP8_low_compliance_states.csv")
print("  ✓ results/STEP8_high_exclusion_risk_states.csv")
print("  ✓ results/STEP8_critical_intervention_states.csv")
print("  ✓ visualizations/STEP8_biometric_compliance.png")
print()
print(" KEY FINDINGS:")
print(f"  - National child compliance (5-17): {national_child_compliance:.2f}%")
print(f"  - National adult compliance (18+): {national_adult_compliance:.2f}%")
print(f"  - Low compliance states: {len(low_compliance_states)}")
print(f"  - Critical intervention states: {len(critical_states)}")
print(f"  - Total children at risk of exclusion: {total_at_risk:,.0f} ({national_risk_pct:.2f}%)")
print()
print(" STEPS 6, 7, 8 COMPLETE!")
print("   Ready for Step 9: Anomaly Detection (to be done separately)")
print("=" * 80)
