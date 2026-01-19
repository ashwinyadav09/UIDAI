"""
PHASE 3 - STEP 2: Child Enrolment Gap Analysis
===============================================
Identifies regions with potential early-life exclusion risks

Aligns with problem statement:
- "Child enrolment gap analysis to identify regions with potential early-life exclusion risks"
- "Critical populations—particularly children... may remain under-updated"

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
plt.rcParams['figure.figsize'] = (15, 8)

print("=" * 80)
print("PHASE 3 - STEP 2: CHILD ENROLMENT GAP ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# STEP 1: LOAD CLEANED DATA
# ============================================================================
print("📂 Loading cleaned enrolment data...")
try:
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    print("✓ Enrolment data loaded successfully!")
    print(f"  - Total rows: {len(enrolment):,}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("Please run STEP2_FINAL_intelligent_cleaning.py first!")
    exit()

print()

# ============================================================================
# STEP 2: CALCULATE CHILD ENROLMENT BY STATE
# ============================================================================
print("👶 Analyzing child enrolment patterns...")
print("   Age groups: 0-5 years (critical early-life period)")
print()

# Aggregate by state
child_enrolment = enrolment.groupby('state').agg({
    'registrations_0_to_5': 'sum',
    'registrations_5_to_17': 'sum',
    'registrations_18_and_above': 'sum',
    'total_enrolments': 'sum'
}).reset_index()

# Calculate proportions
child_enrolment['child_0_5_percentage'] = (
    child_enrolment['registrations_0_to_5'] / child_enrolment['total_enrolments'] * 100
)

child_enrolment['child_5_17_percentage'] = (
    child_enrolment['registrations_5_to_17'] / child_enrolment['total_enrolments'] * 100
)

child_enrolment['adult_percentage'] = (
    child_enrolment['registrations_18_and_above'] / child_enrolment['total_enrolments'] * 100
)

print("✓ Child enrolment calculated by state")
print()

# ============================================================================
# STEP 3: CALCULATE NATIONAL BENCHMARK
# ============================================================================
print("📊 Calculating national benchmarks...")

national_total = child_enrolment['total_enrolments'].sum()
national_0_5 = child_enrolment['registrations_0_to_5'].sum()
national_5_17 = child_enrolment['registrations_5_to_17'].sum()

national_0_5_pct = (national_0_5 / national_total * 100)
national_5_17_pct = (national_5_17 / national_total * 100)

print(f"🇮🇳 National Benchmarks:")
print(f"   - Age 0-5:    {national_0_5_pct:.2f}% of total enrolments")
print(f"   - Age 5-17:   {national_5_17_pct:.2f}% of total enrolments")
print()

# ============================================================================
# STEP 4: IDENTIFY STATES WITH LOW CHILD ENROLMENT
# ============================================================================
print("🚨 Identifying states with LOW child enrolment...")
print("   (States below 70% of national average)")
print()

threshold_0_5 = national_0_5_pct * 0.7
threshold_5_17 = national_5_17_pct * 0.7

child_enrolment['gap_0_5'] = national_0_5_pct - child_enrolment['child_0_5_percentage']
child_enrolment['gap_5_17'] = national_5_17_pct - child_enrolment['child_5_17_percentage']

# Flag states with gaps
child_enrolment['risk_0_5'] = child_enrolment['child_0_5_percentage'] < threshold_0_5
child_enrolment['risk_5_17'] = child_enrolment['child_5_17_percentage'] < threshold_5_17

# Get at-risk states
at_risk_0_5 = child_enrolment[child_enrolment['risk_0_5']].copy()
at_risk_5_17 = child_enrolment[child_enrolment['risk_5_17']].copy()

print(f"🚨 AT-RISK STATES (Age 0-5): {len(at_risk_0_5)} states")
if len(at_risk_0_5) > 0:
    print("\nStates with potential early-life exclusion risk:")
    at_risk_0_5_sorted = at_risk_0_5.sort_values('child_0_5_percentage').head(15)
    for idx, row in at_risk_0_5_sorted.iterrows():
        gap = row['gap_0_5']
        print(f"   {row['state']:40s} → {row['child_0_5_percentage']:>6.2f}% (Gap: {gap:+.2f}%)")
print()

print(f"🚨 AT-RISK STATES (Age 5-17): {len(at_risk_5_17)} states")
if len(at_risk_5_17) > 0:
    print("\nStates with potential school-age exclusion risk:")
    at_risk_5_17_sorted = at_risk_5_17.sort_values('child_5_17_percentage').head(15)
    for idx, row in at_risk_5_17_sorted.iterrows():
        gap = row['gap_5_17']
        print(f"   {row['state']:40s} → {row['child_5_17_percentage']:>6.2f}% (Gap: {gap:+.2f}%)")
print()

# ============================================================================
# STEP 5: PRIORITY CATEGORIZATION
# ============================================================================
print("⭐ Categorizing states by priority...")

def get_priority(row):
    """Categorize state priority based on child enrolment gaps"""
    if row['risk_0_5'] and row['risk_5_17']:
        return 'Critical (Both age groups at risk)'
    elif row['risk_0_5']:
        return 'High (Early-life risk)'
    elif row['risk_5_17']:
        return 'Medium (School-age risk)'
    else:
        return 'Low (Above threshold)'

child_enrolment['priority'] = child_enrolment.apply(get_priority, axis=1)

priority_counts = child_enrolment['priority'].value_counts()
print("\n📊 Priority Distribution:")
for priority, count in priority_counts.items():
    print(f"   {priority:45s}: {count:2d} states")
print()

# ============================================================================
# STEP 6: SAVE RESULTS
# ============================================================================
print("💾 Saving child enrolment gap analysis...")

child_enrolment.to_csv('../results/child_enrolment_gap_analysis.csv', index=False)
at_risk_0_5.to_csv('../results/at_risk_states_age_0_5.csv', index=False)
at_risk_5_17.to_csv('../results/at_risk_states_age_5_17.csv', index=False)

# Save critical states
critical_states = child_enrolment[child_enrolment['priority'] == 'Critical (Both age groups at risk)']
critical_states.to_csv('../results/critical_priority_states.csv', index=False)

print("✓ Analysis saved to results/ folder")
print()

# ============================================================================
# STEP 7: CREATE VISUALIZATIONS
# ============================================================================
print("📊 Creating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Child Enrolment Gap Analysis - Identifying Exclusion Risks', 
             fontsize=16, fontweight='bold')

# 1. Bottom 15 states - Age 0-5
ax1 = axes[0, 0]
bottom_0_5 = child_enrolment.nsmallest(15, 'child_0_5_percentage')
colors_1 = ['red' if x else 'steelblue' for x in bottom_0_5['risk_0_5']]
ax1.barh(range(len(bottom_0_5)), bottom_0_5['child_0_5_percentage'], color=colors_1)
ax1.axvline(national_0_5_pct, color='green', linestyle='--', linewidth=2, label='National Avg')
ax1.axvline(threshold_0_5, color='orange', linestyle='--', linewidth=2, label='Risk Threshold')
ax1.set_yticks(range(len(bottom_0_5)))
ax1.set_yticklabels(bottom_0_5['state'], fontsize=9)
ax1.set_xlabel('Enrolment %', fontweight='bold')
ax1.set_title('Bottom 15 States - Child Enrolment (Age 0-5)', fontweight='bold')
ax1.legend()
ax1.grid(axis='x', alpha=0.3)

# 2. Bottom 15 states - Age 5-17
ax2 = axes[0, 1]
bottom_5_17 = child_enrolment.nsmallest(15, 'child_5_17_percentage')
colors_2 = ['red' if x else 'steelblue' for x in bottom_5_17['risk_5_17']]
ax2.barh(range(len(bottom_5_17)), bottom_5_17['child_5_17_percentage'], color=colors_2)
ax2.axvline(national_5_17_pct, color='green', linestyle='--', linewidth=2, label='National Avg')
ax2.axvline(threshold_5_17, color='orange', linestyle='--', linewidth=2, label='Risk Threshold')
ax2.set_yticks(range(len(bottom_5_17)))
ax2.set_yticklabels(bottom_5_17['state'], fontsize=9)
ax2.set_xlabel('Enrolment %', fontweight='bold')
ax2.set_title('Bottom 15 States - Child Enrolment (Age 5-17)', fontweight='bold')
ax2.legend()
ax2.grid(axis='x', alpha=0.3)

# 3. Priority distribution
ax3 = axes[1, 0]
colors_priority = {
    'Critical (Both age groups at risk)': 'darkred',
    'High (Early-life risk)': 'red',
    'Medium (School-age risk)': 'orange',
    'Low (Above threshold)': 'green'
}
priority_data = child_enrolment['priority'].value_counts()
bars = ax3.bar(range(len(priority_data)), priority_data.values,
               color=[colors_priority[x] for x in priority_data.index])
ax3.set_xticks(range(len(priority_data)))
ax3.set_xticklabels(priority_data.index, rotation=15, ha='right', fontsize=9)
ax3.set_ylabel('Number of States', fontweight='bold')
ax3.set_title('State Priority Distribution', fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(priority_data.values):
    ax3.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

# 4. Scatter plot - Both age groups
ax4 = axes[1, 1]
scatter_colors = child_enrolment['priority'].map(colors_priority)
ax4.scatter(child_enrolment['child_0_5_percentage'], 
           child_enrolment['child_5_17_percentage'],
           c=scatter_colors, s=100, alpha=0.6, edgecolors='black')
ax4.axvline(threshold_0_5, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
ax4.axhline(threshold_5_17, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
ax4.set_xlabel('Age 0-5 Enrolment %', fontweight='bold')
ax4.set_ylabel('Age 5-17 Enrolment %', fontweight='bold')
ax4.set_title('Risk Quadrant Analysis', fontweight='bold')
ax4.grid(alpha=0.3)

# Add legend for scatter
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=label) 
                  for label, color in colors_priority.items()]
ax4.legend(handles=legend_elements, loc='best', fontsize=8)

plt.tight_layout()
plt.savefig('../visualizations/PHASE3_02_child_enrolment_gaps.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: PHASE3_02_child_enrolment_gaps.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ PHASE 3 - STEP 2 COMPLETE!")
print("=" * 80)
print()
print("📊 WHAT WAS DONE:")
print("  ✓ Analyzed child enrolment by state")
print("  ✓ Calculated national benchmarks")
print("  ✓ Identified at-risk states (below 70% of national average)")
print("  ✓ Categorized states by priority level")
print("  ✓ Created comprehensive visualizations")
print()
print("📁 FILES CREATED:")
print("  ✓ results/child_enrolment_gap_analysis.csv")
print("  ✓ results/at_risk_states_age_0_5.csv")
print("  ✓ results/at_risk_states_age_5_17.csv")
print("  ✓ results/critical_priority_states.csv")
print("  ✓ visualizations/PHASE3_02_child_enrolment_gaps.png")
print()
print("🎯 KEY FINDINGS:")
print(f"  - National average (Age 0-5): {national_0_5_pct:.2f}%")
print(f"  - National average (Age 5-17): {national_5_17_pct:.2f}%")
print(f"  - At-risk states (Age 0-5): {len(at_risk_0_5)}")
print(f"  - At-risk states (Age 5-17): {len(at_risk_5_17)}")
print(f"  - Critical priority states: {len(critical_states)}")
print()
print("Next: Run PHASE3_STEP3_biometric_compliance.py")
print("=" * 80)
