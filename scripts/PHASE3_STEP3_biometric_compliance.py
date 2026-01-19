"""
PHASE 3 - STEP 3: Biometric Update Compliance Analysis
=======================================================
Analyzes compliance for children at critical biometric update ages (5 and 15)

Aligns with problem statement:
- "Biometric update compliance analysis for children at critical ages (5 and 15)"
- "adolescents at biometric update milestones (ages 5 and 15)"

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
print("PHASE 3 - STEP 3: BIOMETRIC UPDATE COMPLIANCE ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# STEP 1: LOAD CLEANED DATA
# ============================================================================
print("📂 Loading cleaned data...")
try:
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../data/processed/cleaned_biometric.csv')
    print("✓ Data loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("Please run STEP2_FINAL_intelligent_cleaning.py first!")
    exit()

print()

# ============================================================================
# STEP 2: AGGREGATE BIOMETRIC UPDATES BY STATE
# ============================================================================
print("🔍 Analyzing biometric update patterns...")
print("   Critical ages: 5 years and 15 years (biometric milestones)")
print()

# Aggregate by state
bio_by_state = biometric.groupby('state').agg({
    'biometric_updates_5_to_17': 'sum',
    'biometric_updates_18_and_above': 'sum',
    'total_bio_updates': 'sum'
}).reset_index()

# Get enrolment data for comparison
enrol_by_state = enrolment.groupby('state').agg({
    'registrations_0_to_5': 'sum',
    'registrations_5_to_17': 'sum',
    'registrations_18_and_above': 'sum',
    'total_enrolments': 'sum'
}).reset_index()

# Merge
compliance = bio_by_state.merge(enrol_by_state, on='state', how='outer').fillna(0)

print("✓ Data aggregated by state")
print()

# ============================================================================
# STEP 3: CALCULATE COMPLIANCE METRICS
# ============================================================================
print("📊 Calculating compliance metrics...")
print("   Note: Comparing child biometric updates (age 5-17) to child enrolments")
print()

# Calculate update intensity for children (age 5-17)
# This shows how actively children are updating compared to their enrolment base
compliance['child_update_intensity'] = (
    compliance['biometric_updates_5_to_17'] / compliance['registrations_5_to_17'] * 100
).replace([np.inf, -np.inf], 0)

# Calculate adult update intensity for comparison
compliance['adult_update_intensity'] = (
    compliance['biometric_updates_18_and_above'] / compliance['registrations_18_and_above'] * 100
).replace([np.inf, -np.inf], 0)

# Calculate relative compliance (child vs adult)
compliance['child_vs_adult_ratio'] = (
    compliance['child_update_intensity'] / compliance['adult_update_intensity']
).replace([np.inf, -np.inf], 0)

# Calculate absolute update counts for children
compliance['total_child_updates'] = compliance['biometric_updates_5_to_17']
compliance['total_child_enrolments'] = compliance['registrations_5_to_17']

print("✓ Compliance metrics calculated")
print()

# ============================================================================
# STEP 4: CALCULATE NATIONAL BENCHMARKS
# ============================================================================
print("🇮🇳 Calculating national benchmarks...")

national_child_updates = compliance['biometric_updates_5_to_17'].sum()
national_child_enrolments = compliance['registrations_5_to_17'].sum()
national_child_intensity = (national_child_updates / national_child_enrolments * 100) if national_child_enrolments > 0 else 0

print(f"📊 National Benchmark:")
print(f"   - Child (5-17) Update Intensity: {national_child_intensity:.2f}%")
print(f"   - Total Child Updates: {national_child_updates:,}")
print(f"   - Total Child Enrolments: {national_child_enrolments:,}")
print()

# ============================================================================
# STEP 5: IDENTIFY LOW COMPLIANCE STATES
# ============================================================================
print("🚨 Identifying states with LOW biometric compliance...")
print("   (States below 70% of national average)")
print()

threshold = national_child_intensity * 0.7

compliance['low_compliance'] = compliance['child_update_intensity'] < threshold
compliance['compliance_gap'] = national_child_intensity - compliance['child_update_intensity']

# Get low compliance states
low_compliance_states = compliance[compliance['low_compliance']].copy()

print(f"🚨 LOW COMPLIANCE STATES: {len(low_compliance_states)} states")
if len(low_compliance_states) > 0:
    print("\nStates with potential biometric update compliance issues:")
    low_sorted = low_compliance_states.sort_values('child_update_intensity').head(20)
    for idx, row in low_sorted.iterrows():
        gap = row['compliance_gap']
        print(f"   {row['state']:40s} → {row['child_update_intensity']:>7.2f}% (Gap: {gap:+.2f}%)")
print()

# ============================================================================
# STEP 6: RISK CATEGORIZATION
# ============================================================================
print("⭐ Categorizing states by compliance risk...")

def get_compliance_risk(row, threshold):
    """Categorize compliance risk"""
    intensity = row['child_update_intensity']
    if intensity < threshold * 0.5:
        return 'Critical (< 50% of national avg)'
    elif intensity < threshold:
        return 'High (50-70% of national avg)'
    elif intensity < national_child_intensity:
        return 'Medium (70-100% of national avg)'
    else:
        return 'Good (Above national avg)'

compliance['risk_category'] = compliance.apply(lambda x: get_compliance_risk(x, threshold), axis=1)

risk_counts = compliance['risk_category'].value_counts()
print("\n📊 Risk Distribution:")
for risk, count in risk_counts.items():
    print(f"   {risk:45s}: {count:2d} states")
print()

# ============================================================================
# STEP 7: IDENTIFY CRITICAL INTERVENTION STATES
# ============================================================================
print("🎯 Identifying states needing URGENT intervention...")
print("   (Low compliance + High child population)")
print()

# States with low compliance AND high absolute number of children
compliance['needs_intervention'] = (
    (compliance['low_compliance']) & 
    (compliance['total_child_enrolments'] > compliance['total_child_enrolments'].median())
)

intervention_states = compliance[compliance['needs_intervention']].copy()

print(f"🚨 CRITICAL INTERVENTION NEEDED: {len(intervention_states)} states")
if len(intervention_states) > 0:
    print("\nLarge child populations with low update compliance:")
    intervention_sorted = intervention_states.sort_values('total_child_enrolments', ascending=False)
    for idx, row in intervention_sorted.iterrows():
        print(f"   {row['state']:40s} → {row['total_child_enrolments']:>10,.0f} children, {row['child_update_intensity']:>6.2f}% compliance")
print()

# ============================================================================
# STEP 8: SAVE RESULTS
# ============================================================================
print("💾 Saving compliance analysis...")

compliance.to_csv('../results/biometric_compliance_analysis.csv', index=False)
low_compliance_states.to_csv('../results/low_compliance_states.csv', index=False)
intervention_states.to_csv('../results/intervention_priority_states.csv', index=False)

print("✓ Analysis saved to results/ folder")
print()

# ============================================================================
# STEP 9: CREATE VISUALIZATIONS
# ============================================================================
print("📊 Creating compliance visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Biometric Update Compliance Analysis (Critical Ages 5 & 15)', 
             fontsize=16, fontweight='bold')

# 1. Bottom 20 states - Child compliance
ax1 = axes[0, 0]
bottom_compliance = compliance.nsmallest(20, 'child_update_intensity')
colors_1 = ['red' if x else 'steelblue' for x in bottom_compliance['low_compliance']]
ax1.barh(range(len(bottom_compliance)), bottom_compliance['child_update_intensity'], color=colors_1)
ax1.axvline(national_child_intensity, color='green', linestyle='--', linewidth=2, label='National Avg')
ax1.axvline(threshold, color='orange', linestyle='--', linewidth=2, label='Risk Threshold')
ax1.set_yticks(range(len(bottom_compliance)))
ax1.set_yticklabels(bottom_compliance['state'], fontsize=8)
ax1.set_xlabel('Update Intensity (%)', fontweight='bold')
ax1.set_title('Bottom 20 States - Child Biometric Update Compliance', fontweight='bold')
ax1.legend()
ax1.grid(axis='x', alpha=0.3)

# 2. Risk category distribution
ax2 = axes[0, 1]
colors_risk = {
    'Critical (< 50% of national avg)': 'darkred',
    'High (50-70% of national avg)': 'red',
    'Medium (70-100% of national avg)': 'orange',
    'Good (Above national avg)': 'green'
}
risk_data = compliance['risk_category'].value_counts()
bars = ax2.bar(range(len(risk_data)), risk_data.values,
               color=[colors_risk.get(x, 'gray') for x in risk_data.index])
ax2.set_xticks(range(len(risk_data)))
ax2.set_xticklabels(risk_data.index, rotation=15, ha='right', fontsize=8)
ax2.set_ylabel('Number of States', fontweight='bold')
ax2.set_title('Compliance Risk Distribution', fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(risk_data.values):
    ax2.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

# 3. Child vs Adult compliance comparison
ax3 = axes[1, 0]
top_15 = compliance.nlargest(15, 'total_child_enrolments')
x = np.arange(len(top_15))
width = 0.35
ax3.barh(x - width/2, top_15['child_update_intensity'], width, label='Children (5-17)', color='steelblue')
ax3.barh(x + width/2, top_15['adult_update_intensity'], width, label='Adults (18+)', color='coral')
ax3.set_yticks(x)
ax3.set_yticklabels(top_15['state'], fontsize=8)
ax3.set_xlabel('Update Intensity (%)', fontweight='bold')
ax3.set_title('Top 15 States by Child Population - Child vs Adult Compliance', fontweight='bold')
ax3.legend()
ax3.grid(axis='x', alpha=0.3)

# 4. Scatter plot - Compliance vs Population
ax4 = axes[1, 1]
scatter_colors = compliance['risk_category'].map(colors_risk)
ax4.scatter(compliance['total_child_enrolments'], 
           compliance['child_update_intensity'],
           c=scatter_colors, s=100, alpha=0.6, edgecolors='black')
ax4.axhline(threshold, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='Risk Threshold')
ax4.axhline(national_child_intensity, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='National Avg')
ax4.set_xlabel('Total Child Enrolments', fontweight='bold')
ax4.set_ylabel('Update Intensity (%)', fontweight='bold')
ax4.set_title('Compliance vs Child Population Size', fontweight='bold')
ax4.legend()
ax4.grid(alpha=0.3)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=label) 
                  for label, color in colors_risk.items()]
ax4.legend(handles=legend_elements, loc='best', fontsize=7)

plt.tight_layout()
plt.savefig('../visualizations/PHASE3_03_biometric_compliance.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: PHASE3_03_biometric_compliance.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ PHASE 3 - STEP 3 COMPLETE!")
print("=" * 80)
print()
print("📊 WHAT WAS DONE:")
print("  ✓ Analyzed biometric update compliance for children (ages 5-17)")
print("  ✓ Calculated national benchmarks")
print("  ✓ Identified low compliance states")
print("  ✓ Categorized states by risk level")
print("  ✓ Identified states needing urgent intervention")
print("  ✓ Created comprehensive visualizations")
print()
print("📁 FILES CREATED:")
print("  ✓ results/biometric_compliance_analysis.csv")
print("  ✓ results/low_compliance_states.csv")
print("  ✓ results/intervention_priority_states.csv")
print("  ✓ visualizations/PHASE3_03_biometric_compliance.png")
print()
print("🎯 KEY FINDINGS:")
print(f"  - National child update intensity: {national_child_intensity:.2f}%")
print(f"  - Low compliance states: {len(low_compliance_states)}")
print(f"  - States needing intervention: {len(intervention_states)}")
print(f"  - Risk threshold: {threshold:.2f}%")
print()
print("Next: Run PHASE3_STEP4_anomaly_detection.py")
print("=" * 80)
