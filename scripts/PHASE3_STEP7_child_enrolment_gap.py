"""
PHASE 3 - STEP 7: Child Enrolment Gap Analysis
===============================================
Identifies regions with low child enrolment

Calculates:
- Enrolment rate for age 0-5 by state
- Identifies states with low child enrolment
- Compares with population data (using enrolment as proxy)
- Flags vulnerable regions

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
print("PHASE 3 - STEP 7: CHILD ENROLMENT GAP ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# LOAD CLEANED DATA
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
# STEP 7.1: Calculate Enrolment by Age Group and State
# ============================================================================
print("👶 Step 7.1: Calculating enrolment by age group and state...")

# Aggregate by state
child_enrolment = enrolment.groupby('state').agg({
    'registrations_0_to_5': 'sum',
    'registrations_5_to_17': 'sum',
    'registrations_18_and_above': 'sum',
    'total_enrolments': 'sum'
}).reset_index()

print(f"✓ Data aggregated for {len(child_enrolment)} states")
print()

# ============================================================================
# STEP 7.2: Calculate Enrolment Rate for Age 0-5 by State
# ============================================================================
print("📊 Step 7.2: Calculating enrolment rate for age 0-5 by state...")

# Calculate percentage of total enrolments that are age 0-5
child_enrolment['age_0_5_percentage'] = (
    child_enrolment['registrations_0_to_5'] / child_enrolment['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

# Calculate percentage for age 5-17
child_enrolment['age_5_17_percentage'] = (
    child_enrolment['registrations_5_to_17'] / child_enrolment['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

# Calculate percentage for age 18+
child_enrolment['age_18_plus_percentage'] = (
    child_enrolment['registrations_18_and_above'] / child_enrolment['total_enrolments'] * 100
).replace([np.inf, -np.inf], 0)

print("✓ Enrolment rates calculated")
print()

# ============================================================================
# STEP 7.3: Calculate National Benchmarks
# ============================================================================
print("🇮🇳 Step 7.3: Calculating national benchmarks...")

# Calculate national averages
national_total_enrol = child_enrolment['total_enrolments'].sum()
national_0_5 = child_enrolment['registrations_0_to_5'].sum()
national_5_17 = child_enrolment['registrations_5_to_17'].sum()
national_18_plus = child_enrolment['registrations_18_and_above'].sum()

national_0_5_pct = (national_0_5 / national_total_enrol * 100)
national_5_17_pct = (national_5_17 / national_total_enrol * 100)
national_18_plus_pct = (national_18_plus / national_total_enrol * 100)

print("📊 National Benchmarks:")
print(f"  - Age 0-5:    {national_0_5_pct:.2f}% of total enrolments ({national_0_5:,})")
print(f"  - Age 5-17:   {national_5_17_pct:.2f}% of total enrolments ({national_5_17:,})")
print(f"  - Age 18+:    {national_18_plus_pct:.2f}% of total enrolments ({national_18_plus:,})")
print()

# ============================================================================
# STEP 7.4: Identify States with Low Child Enrolment
# ============================================================================
print("🚨 Step 7.4: Identifying states with low child enrolment...")
print("   Using threshold: 70% of national average")
print()

# Set thresholds (70% of national average)
threshold_0_5 = national_0_5_pct * 0.7
threshold_5_17 = national_5_17_pct * 0.7

print(f"📏 Thresholds:")
print(f"  - Age 0-5 threshold:  {threshold_0_5:.2f}% (70% of national avg)")
print(f"  - Age 5-17 threshold: {threshold_5_17:.2f}% (70% of national avg)")
print()

# Calculate gaps
child_enrolment['gap_0_5'] = national_0_5_pct - child_enrolment['age_0_5_percentage']
child_enrolment['gap_5_17'] = national_5_17_pct - child_enrolment['age_5_17_percentage']

# Flag states below threshold
child_enrolment['at_risk_0_5'] = child_enrolment['age_0_5_percentage'] < threshold_0_5
child_enrolment['at_risk_5_17'] = child_enrolment['age_5_17_percentage'] < threshold_5_17

# Get at-risk states
at_risk_0_5 = child_enrolment[child_enrolment['at_risk_0_5']].copy()
at_risk_5_17 = child_enrolment[child_enrolment['at_risk_5_17']].copy()

print(f"🚨 AT-RISK STATES (Age 0-5): {len(at_risk_0_5)} states")
if len(at_risk_0_5) > 0:
    print("\nStates with low child (0-5) enrolment:")
    at_risk_0_5_sorted = at_risk_0_5.sort_values('age_0_5_percentage')
    for idx, row in at_risk_0_5_sorted.iterrows():
        gap = row['gap_0_5']
        actual = row['age_0_5_percentage']
        print(f"  {row['state']:40s} → {actual:>6.2f}% (Gap: {gap:+.2f}%)")
else:
    print("  ✓ No states below threshold")
print()

print(f"🚨 AT-RISK STATES (Age 5-17): {len(at_risk_5_17)} states")
if len(at_risk_5_17) > 0:
    print("\nStates with low child (5-17) enrolment:")
    at_risk_5_17_sorted = at_risk_5_17.sort_values('age_5_17_percentage')
    for idx, row in at_risk_5_17_sorted.iterrows():
        gap = row['gap_5_17']
        actual = row['age_5_17_percentage']
        print(f"  {row['state']:40s} → {actual:>6.2f}% (Gap: {gap:+.2f}%)")
else:
    print("  ✓ No states below threshold")
print()

# ============================================================================
# STEP 7.5: Flag Vulnerable Regions (Priority Categorization)
# ============================================================================
print("⚠️  Step 7.5: Flagging vulnerable regions...")

def categorize_vulnerability(row):
    """Categorize vulnerability based on enrolment gaps"""
    if row['at_risk_0_5'] and row['at_risk_5_17']:
        return 'Critical (Both age groups)'
    elif row['at_risk_0_5']:
        return 'High (Early childhood risk)'
    elif row['at_risk_5_17']:
        return 'Medium (School-age risk)'
    else:
        return 'Low (Above threshold)'

child_enrolment['vulnerability_level'] = child_enrolment.apply(categorize_vulnerability, axis=1)

# Count by vulnerability level
vulnerability_counts = child_enrolment['vulnerability_level'].value_counts()

print("📊 Vulnerability Distribution:")
for level, count in vulnerability_counts.items():
    print(f"  {level:40s}: {count:2d} states")
print()

# Get critical states
critical_states = child_enrolment[child_enrolment['vulnerability_level'] == 'Critical (Both age groups)']

if len(critical_states) > 0:
    print(f"🚨 CRITICAL PRIORITY STATES: {len(critical_states)}")
    print("   States requiring immediate attention:")
    for idx, row in critical_states.iterrows():
        print(f"  {row['state']:40s} → 0-5: {row['age_0_5_percentage']:.2f}%, 5-17: {row['age_5_17_percentage']:.2f}%")
    print()

# ============================================================================
# STEP 7.6: Compare with Population Data (using enrolment as proxy)
# ============================================================================
print("📊 Step 7.6: Comparing child enrolment distribution across states...")
print("   (Using total enrolment as population proxy)")
print()

# Calculate share of total enrolments
child_enrolment['enrolment_share'] = (
    child_enrolment['total_enrolments'] / child_enrolment['total_enrolments'].sum() * 100
)

# Sort by total enrolments
top_10_population = child_enrolment.nlargest(10, 'total_enrolments')

print("📊 Top 10 States by Total Enrolment:")
for idx, row in top_10_population.iterrows():
    print(f"  {row['state']:40s} → {row['total_enrolments']:>12,.0f} ({row['enrolment_share']:>5.2f}%)")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("💾 Saving child enrolment gap analysis...")

child_enrolment.to_csv('../results/STEP7_child_enrolment_analysis.csv', index=False)
at_risk_0_5.to_csv('../results/STEP7_at_risk_age_0_5.csv', index=False)
at_risk_5_17.to_csv('../results/STEP7_at_risk_age_5_17.csv', index=False)
critical_states.to_csv('../results/STEP7_critical_vulnerable_states.csv', index=False)

print("✓ Results saved:")
print("  - STEP7_child_enrolment_analysis.csv")
print("  - STEP7_at_risk_age_0_5.csv")
print("  - STEP7_at_risk_age_5_17.csv")
print("  - STEP7_critical_vulnerable_states.csv")
print()

# ============================================================================
# CREATE VISUALIZATIONS
# ============================================================================
print("📊 Creating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Child Enrolment Gap Analysis - Identifying Vulnerable Regions', 
             fontsize=16, fontweight='bold')

# Chart 1: Bottom 15 states - Age 0-5
ax1 = axes[0, 0]
bottom_15_0_5 = child_enrolment.nsmallest(15, 'age_0_5_percentage')
colors_1 = ['red' if x else 'steelblue' for x in bottom_15_0_5['at_risk_0_5']]
bars1 = ax1.barh(range(len(bottom_15_0_5)), bottom_15_0_5['age_0_5_percentage'], color=colors_1)
ax1.axvline(national_0_5_pct, color='green', linestyle='--', linewidth=2, label=f'National Avg: {national_0_5_pct:.1f}%')
ax1.axvline(threshold_0_5, color='orange', linestyle='--', linewidth=2, label=f'Risk Threshold: {threshold_0_5:.1f}%')
ax1.set_yticks(range(len(bottom_15_0_5)))
ax1.set_yticklabels(bottom_15_0_5['state'], fontsize=9)
ax1.set_xlabel('Enrolment %', fontweight='bold')
ax1.set_title('Bottom 15 States - Child Enrolment (Age 0-5)', fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(bottom_15_0_5['age_0_5_percentage']):
    ax1.text(v, i, f' {v:.1f}%', va='center', fontsize=8)

# Chart 2: Bottom 15 states - Age 5-17
ax2 = axes[0, 1]
bottom_15_5_17 = child_enrolment.nsmallest(15, 'age_5_17_percentage')
colors_2 = ['red' if x else 'steelblue' for x in bottom_15_5_17['at_risk_5_17']]
bars2 = ax2.barh(range(len(bottom_15_5_17)), bottom_15_5_17['age_5_17_percentage'], color=colors_2)
ax2.axvline(national_5_17_pct, color='green', linestyle='--', linewidth=2, label=f'National Avg: {national_5_17_pct:.1f}%')
ax2.axvline(threshold_5_17, color='orange', linestyle='--', linewidth=2, label=f'Risk Threshold: {threshold_5_17:.1f}%')
ax2.set_yticks(range(len(bottom_15_5_17)))
ax2.set_yticklabels(bottom_15_5_17['state'], fontsize=9)
ax2.set_xlabel('Enrolment %', fontweight='bold')
ax2.set_title('Bottom 15 States - Child Enrolment (Age 5-17)', fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(bottom_15_5_17['age_5_17_percentage']):
    ax2.text(v, i, f' {v:.1f}%', va='center', fontsize=8)

# Chart 3: Vulnerability distribution
ax3 = axes[1, 0]
colors_vuln = {
    'Critical (Both age groups)': 'darkred',
    'High (Early childhood risk)': 'red',
    'Medium (School-age risk)': 'orange',
    'Low (Above threshold)': 'green'
}
vuln_data = child_enrolment['vulnerability_level'].value_counts()
bars3 = ax3.bar(range(len(vuln_data)), vuln_data.values,
               color=[colors_vuln.get(x, 'gray') for x in vuln_data.index])
ax3.set_xticks(range(len(vuln_data)))
ax3.set_xticklabels(vuln_data.index, rotation=15, ha='right', fontsize=9)
ax3.set_ylabel('Number of States', fontweight='bold')
ax3.set_title('State Vulnerability Distribution', fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(vuln_data.values):
    ax3.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

# Chart 4: Scatter - Both age groups
ax4 = axes[1, 1]
scatter_colors = child_enrolment['vulnerability_level'].map(colors_vuln)
ax4.scatter(child_enrolment['age_0_5_percentage'], 
           child_enrolment['age_5_17_percentage'],
           c=scatter_colors, s=100, alpha=0.6, edgecolors='black')
ax4.axvline(threshold_0_5, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='Risk Thresholds')
ax4.axhline(threshold_5_17, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
ax4.set_xlabel('Age 0-5 Enrolment %', fontweight='bold')
ax4.set_ylabel('Age 5-17 Enrolment %', fontweight='bold')
ax4.set_title('Risk Quadrant Analysis', fontweight='bold')
ax4.grid(alpha=0.3)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=label) 
                  for label, color in colors_vuln.items()]
ax4.legend(handles=legend_elements, loc='best', fontsize=8)

plt.tight_layout()
plt.savefig('../visualizations/STEP7_child_enrolment_gaps.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: STEP7_child_enrolment_gaps.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ STEP 7 COMPLETE!")
print("=" * 80)
print()
print("📊 WHAT WAS DONE:")
print("  ✓ Calculated enrolment rate for age 0-5 by state")
print("  ✓ Calculated enrolment rate for age 5-17 by state")
print("  ✓ Identified states with low child enrolment")
print("  ✓ Compared with population distribution")
print("  ✓ Flagged vulnerable regions by priority")
print("  ✓ Created comprehensive visualizations")
print()
print("📁 FILES CREATED:")
print("  ✓ results/STEP7_child_enrolment_analysis.csv")
print("  ✓ results/STEP7_at_risk_age_0_5.csv")
print("  ✓ results/STEP7_at_risk_age_5_17.csv")
print("  ✓ results/STEP7_critical_vulnerable_states.csv")
print("  ✓ visualizations/STEP7_child_enrolment_gaps.png")
print()
print("🎯 KEY FINDINGS:")
print(f"  - National average (Age 0-5): {national_0_5_pct:.2f}%")
print(f"  - National average (Age 5-17): {national_5_17_pct:.2f}%")
print(f"  - At-risk states (Age 0-5): {len(at_risk_0_5)}")
print(f"  - At-risk states (Age 5-17): {len(at_risk_5_17)}")
print(f"  - Critical priority states: {len(critical_states)}")
print()
print("Next: Run PHASE3_STEP8_biometric_compliance.py")
print("=" * 80)
