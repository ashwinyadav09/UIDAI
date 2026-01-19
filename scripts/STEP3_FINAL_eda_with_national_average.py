"""
STEP 3 FINAL: EXPLORATORY DATA ANALYSIS (EDA)
==============================================
IMPROVED APPROACH: Using National Average as Baseline

Instead of showing rates >100%, we:
1. Calculate INDIA AVERAGE update activity
2. Compare each state to national average
3. Show which states are ABOVE or BELOW average
4. Identify gaps more meaningfully

This provides clearer, more actionable insights!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

# ============================================
# CONFIGURATION
# ============================================
PROJECT_PATH = r"E:\Aadhar UIDAI\PROJECT"
DATA_FOLDER = os.path.join(PROJECT_PATH, "data", "processed")
VIZ_FOLDER = os.path.join(PROJECT_PATH, "visualizations")
RESULTS_FOLDER = os.path.join(PROJECT_PATH, "results")

os.makedirs(VIZ_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

print("=" * 120)
print("EXPLORATORY DATA ANALYSIS (EDA) - FINAL VERSION")
print("Using National Average as Baseline for Meaningful Comparisons")
print("=" * 120)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 120)

# ============================================
# LOAD CLEANED DATA
# ============================================
print("\n📂 Loading cleaned datasets...")

df_enrol = pd.read_csv(os.path.join(DATA_FOLDER, "cleaned_enrolment.csv"))
df_bio = pd.read_csv(os.path.join(DATA_FOLDER, "cleaned_biometric.csv"))
df_demo = pd.read_csv(os.path.join(DATA_FOLDER, "cleaned_demographic.csv"))

# Convert dates
df_enrol['date'] = pd.to_datetime(df_enrol['date'])
df_bio['date'] = pd.to_datetime(df_bio['date'])
df_demo['date'] = pd.to_datetime(df_demo['date'])

print(f"✓ Enrolment: {len(df_enrol):,} rows | {df_enrol['total_enrolments'].sum():,} total enrolments")
print(f"✓ Biometric: {len(df_bio):,} rows | {df_bio['total_bio_updates'].sum():,} total updates")
print(f"✓ Demographic: {len(df_demo):,} rows | {df_demo['total_demo_updates'].sum():,} total updates")

# ============================================
# CALCULATE NATIONAL AVERAGES (BASELINE)
# ============================================
print(f"\n{'=' * 120}")
print("CALCULATING INDIA NATIONAL AVERAGES (BASELINE)")
print(f"{'=' * 120}")

# Filter out 'unknown'
df_enrol_valid = df_enrol[df_enrol['state'] != 'unknown']
df_bio_valid = df_bio[df_bio['state'] != 'unknown']
df_demo_valid = df_demo[df_demo['state'] != 'unknown']

# Calculate totals
total_enrol_india = df_enrol_valid['total_enrolments'].sum()
total_bio_india = df_bio_valid['total_bio_updates'].sum()
total_demo_india = df_demo_valid['total_demo_updates'].sum()

# Calculate per-state averages (India baseline)
num_states = df_enrol_valid['state'].nunique()
avg_enrol_per_state = total_enrol_india / num_states
avg_bio_per_state = total_bio_india / num_states
avg_demo_per_state = total_demo_india / num_states

print(f"\n📊 INDIA TOTALS:")
print(f"   Total Enrolments: {total_enrol_india:>18,}")
print(f"   Total Biometric Updates: {total_bio_india:>18,}")
print(f"   Total Demographic Updates: {total_demo_india:>18,}")

print(f"\n📊 INDIA AVERAGES (Per State Baseline):")
print(f"   Number of States/UTs: {num_states}")
print(f"   Average Enrolments per State: {avg_enrol_per_state:>18,.0f}")
print(f"   Average Biometric Updates per State: {avg_bio_per_state:>18,.0f}")
print(f"   Average Demographic Updates per State: {avg_demo_per_state:>18,.0f}")

# ============================================
# EDA 1: STATES VS NATIONAL AVERAGE - ENROLMENT
# ============================================
print(f"\n{'=' * 120}")
print("EDA 1: STATE ENROLMENT COMPARED TO NATIONAL AVERAGE")
print(f"{'=' * 120}")

state_enrol = df_enrol_valid.groupby('state')['total_enrolments'].sum().sort_values(ascending=False)

# Calculate deviation from average
state_enrol_deviation = ((state_enrol - avg_enrol_per_state) / avg_enrol_per_state * 100).sort_values(ascending=False)

print(f"\n🔝 TOP 10 STATES - HIGHEST ENROLMENT (Above National Average):")
print(f"{'Rank':<6} {'State':<40} {'Enrolments':>15} {'vs Avg':>15}")
print("-" * 80)
for i, (state, count) in enumerate(state_enrol.head(10).items(), 1):
    deviation = state_enrol_deviation[state]
    indicator = "↑" if deviation > 0 else "↓"
    print(f"{i:<6} {state.title():<40} {count:>15,} {indicator} {abs(deviation):>6.1f}%")

print(f"\n🔻 BOTTOM 10 STATES - LOWEST ENROLMENT (Below National Average):")
print(f"{'Rank':<6} {'State':<40} {'Enrolments':>15} {'vs Avg':>15}")
print("-" * 80)
for i, (state, count) in enumerate(state_enrol.tail(10).items(), 1):
    deviation = state_enrol_deviation[state]
    indicator = "↑" if deviation > 0 else "↓"
    print(f"{i:<6} {state.title():<40} {count:>15,} {indicator} {abs(deviation):>6.1f}%")

# VISUALIZATION 1: States vs Average
fig, axes = plt.subplots(1, 2, figsize=(22, 10))

# Top 15 with average line
top_15 = state_enrol.head(15)
colors_top = ['#2ecc71' if val > avg_enrol_per_state else '#e67e22' for val in top_15.values]
bars1 = axes[0].barh(range(len(top_15)), top_15.values, color=colors_top, edgecolor='black', linewidth=1.5)
axes[0].axvline(x=avg_enrol_per_state, color='red', linestyle='--', linewidth=3, label=f'India Avg: {avg_enrol_per_state:,.0f}')
axes[0].set_yticks(range(len(top_15)))
axes[0].set_yticklabels([s.title() for s in top_15.index], fontsize=11)
axes[0].set_xlabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[0].set_title('Top 15 States - Enrolments vs National Average', fontsize=15, fontweight='bold', pad=20)
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3, linestyle='--')
axes[0].legend(fontsize=12, loc='lower right')

for i, (bar, val) in enumerate(zip(bars1, top_15.values)):
    axes[0].text(val, i, f' {val:,.0f}', va='center', fontsize=10, fontweight='bold')

# Bottom 15 with average line
bottom_15 = state_enrol.tail(15)
colors_bottom = ['#2ecc71' if val > avg_enrol_per_state else '#e74c3c' for val in bottom_15.values]
bars2 = axes[1].barh(range(len(bottom_15)), bottom_15.values, color=colors_bottom, edgecolor='black', linewidth=1.5)
axes[1].axvline(x=avg_enrol_per_state, color='red', linestyle='--', linewidth=3, label=f'India Avg: {avg_enrol_per_state:,.0f}')
axes[1].set_yticks(range(len(bottom_15)))
axes[1].set_yticklabels([s.title() for s in bottom_15.index], fontsize=11)
axes[1].set_xlabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[1].set_title('Bottom 15 States - Enrolments vs National Average\n⚠️ Below Average Coverage', 
                  fontsize=15, fontweight='bold', pad=20)
axes[1].invert_yaxis()
axes[1].grid(axis='x', alpha=0.3, linestyle='--')
axes[1].legend(fontsize=12, loc='lower right')

for i, (bar, val) in enumerate(zip(bars2, bottom_15.values)):
    axes[1].text(val, i, f' {val:,.0f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '01_state_enrolment_vs_average.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 01_state_enrolment_vs_average.png")
plt.close()

# ============================================
# EDA 2: STATES VS NATIONAL AVERAGE - UPDATES
# ============================================
print(f"\n{'=' * 120}")
print("EDA 2: STATE UPDATE ACTIVITY COMPARED TO NATIONAL AVERAGE")
print(f"{'=' * 120}")

state_bio = df_bio_valid.groupby('state')['total_bio_updates'].sum().sort_values(ascending=False)
state_demo = df_demo_valid.groupby('state')['total_demo_updates'].sum().sort_values(ascending=False)

# Calculate deviations
state_bio_deviation = ((state_bio - avg_bio_per_state) / avg_bio_per_state * 100).sort_values(ascending=False)
state_demo_deviation = ((state_demo - avg_demo_per_state) / avg_demo_per_state * 100).sort_values(ascending=False)

print(f"\n📊 BIOMETRIC UPDATES vs NATIONAL AVERAGE:")
print(f"\n🔝 TOP 10 STATES - Above National Average:")
print(f"{'Rank':<6} {'State':<40} {'Updates':>15} {'vs Avg':>15}")
print("-" * 80)
for i, (state, count) in enumerate(state_bio.head(10).items(), 1):
    deviation = state_bio_deviation[state]
    indicator = "↑" if deviation > 0 else "↓"
    print(f"{i:<6} {state.title():<40} {count:>15,} {indicator} {abs(deviation):>6.1f}%")

print(f"\n🔻 BOTTOM 10 STATES - Below National Average:")
print(f"{'Rank':<6} {'State':<40} {'Updates':>15} {'vs Avg':>15}")
print("-" * 80)
for i, (state, count) in enumerate(state_bio.tail(10).items(), 1):
    deviation = state_bio_deviation[state]
    indicator = "↑" if deviation > 0 else "↓"
    print(f"{i:<6} {state.title():<40} {count:>15,} {indicator} {abs(deviation):>6.1f}%")

print(f"\n📊 DEMOGRAPHIC UPDATES vs NATIONAL AVERAGE:")
print(f"\n🔝 TOP 10 STATES - Above National Average:")
print(f"{'Rank':<6} {'State':<40} {'Updates':>15} {'vs Avg':>15}")
print("-" * 80)
for i, (state, count) in enumerate(state_demo.head(10).items(), 1):
    deviation = state_demo_deviation[state]
    indicator = "↑" if deviation > 0 else "↓"
    print(f"{i:<6} {state.title():<40} {count:>15,} {indicator} {abs(deviation):>6.1f}%")

print(f"\n🔻 BOTTOM 10 STATES - Below National Average:")
print(f"{'Rank':<6} {'State':<40} {'Updates':>15} {'vs Avg':>15}")
print("-" * 80)
for i, (state, count) in enumerate(state_demo.tail(10).items(), 1):
    deviation = state_demo_deviation[state]
    indicator = "↑" if deviation > 0 else "↓"
    print(f"{i:<6} {state.title():<40} {count:>15,} {indicator} {abs(deviation):>6.1f}%")

# VISUALIZATION 2: Updates vs Average
fig, axes = plt.subplots(2, 2, figsize=(22, 18))

# Biometric - Top 15
top_bio = state_bio.head(15)
colors_bio_top = ['#3498db' if val > avg_bio_per_state else '#e67e22' for val in top_bio.values]
bars1 = axes[0, 0].barh(range(len(top_bio)), top_bio.values, color=colors_bio_top, edgecolor='black', linewidth=1.5)
axes[0, 0].axvline(x=avg_bio_per_state, color='red', linestyle='--', linewidth=3, label=f'India Avg: {avg_bio_per_state:,.0f}')
axes[0, 0].set_yticks(range(len(top_bio)))
axes[0, 0].set_yticklabels([s.title() for s in top_bio.index], fontsize=10)
axes[0, 0].set_xlabel('Biometric Updates', fontsize=12, fontweight='bold')
axes[0, 0].set_title('Top 15 States - Biometric Updates vs National Average', fontsize=14, fontweight='bold')
axes[0, 0].invert_yaxis()
axes[0, 0].grid(axis='x', alpha=0.3)
axes[0, 0].legend(fontsize=11)
for i, val in enumerate(top_bio.values):
    axes[0, 0].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

# Biometric - Bottom 15
bottom_bio = state_bio.tail(15)
colors_bio_bottom = ['#3498db' if val > avg_bio_per_state else '#e74c3c' for val in bottom_bio.values]
bars2 = axes[0, 1].barh(range(len(bottom_bio)), bottom_bio.values, color=colors_bio_bottom, edgecolor='black', linewidth=1.5)
axes[0, 1].axvline(x=avg_bio_per_state, color='red', linestyle='--', linewidth=3, label=f'India Avg: {avg_bio_per_state:,.0f}')
axes[0, 1].set_yticks(range(len(bottom_bio)))
axes[0, 1].set_yticklabels([s.title() for s in bottom_bio.index], fontsize=10)
axes[0, 1].set_xlabel('Biometric Updates', fontsize=12, fontweight='bold')
axes[0, 1].set_title('Bottom 15 States - Biometric Updates vs National Average\n⚠️ Below Average Compliance', 
                     fontsize=14, fontweight='bold')
axes[0, 1].invert_yaxis()
axes[0, 1].grid(axis='x', alpha=0.3)
axes[0, 1].legend(fontsize=11)
for i, val in enumerate(bottom_bio.values):
    axes[0, 1].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

# Demographic - Top 15
top_demo = state_demo.head(15)
colors_demo_top = ['#9b59b6' if val > avg_demo_per_state else '#e67e22' for val in top_demo.values]
bars3 = axes[1, 0].barh(range(len(top_demo)), top_demo.values, color=colors_demo_top, edgecolor='black', linewidth=1.5)
axes[1, 0].axvline(x=avg_demo_per_state, color='red', linestyle='--', linewidth=3, label=f'India Avg: {avg_demo_per_state:,.0f}')
axes[1, 0].set_yticks(range(len(top_demo)))
axes[1, 0].set_yticklabels([s.title() for s in top_demo.index], fontsize=10)
axes[1, 0].set_xlabel('Demographic Updates', fontsize=12, fontweight='bold')
axes[1, 0].set_title('Top 15 States - Demographic Updates vs National Average', fontsize=14, fontweight='bold')
axes[1, 0].invert_yaxis()
axes[1, 0].grid(axis='x', alpha=0.3)
axes[1, 0].legend(fontsize=11)
for i, val in enumerate(top_demo.values):
    axes[1, 0].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

# Demographic - Bottom 15
bottom_demo = state_demo.tail(15)
colors_demo_bottom = ['#9b59b6' if val > avg_demo_per_state else '#e74c3c' for val in bottom_demo.values]
bars4 = axes[1, 1].barh(range(len(bottom_demo)), bottom_demo.values, color=colors_demo_bottom, edgecolor='black', linewidth=1.5)
axes[1, 1].axvline(x=avg_demo_per_state, color='red', linestyle='--', linewidth=3, label=f'India Avg: {avg_demo_per_state:,.0f}')
axes[1, 1].set_yticks(range(len(bottom_demo)))
axes[1, 1].set_yticklabels([s.title() for s in bottom_demo.index], fontsize=10)
axes[1, 1].set_xlabel('Demographic Updates', fontsize=12, fontweight='bold')
axes[1, 1].set_title('Bottom 15 States - Demographic Updates vs National Average\n⚠️ Below Average Activity', 
                     fontsize=14, fontweight='bold')
axes[1, 1].invert_yaxis()
axes[1, 1].grid(axis='x', alpha=0.3)
axes[1, 1].legend(fontsize=11)
for i, val in enumerate(bottom_demo.values):
    axes[1, 1].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '02_state_updates_vs_average.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 02_state_updates_vs_average.png")
plt.close()

# ============================================
# EDA 3: TIME TRENDS (MONTHLY PATTERNS)
# ============================================
print(f"\n{'=' * 120}")
print("EDA 3: TIME TRENDS - MONTHLY PATTERNS")
print(f"{'=' * 120}")

# Monthly aggregation
monthly_enrol = df_enrol.groupby(df_enrol['date'].dt.to_period('M'))['total_enrolments'].sum()
monthly_bio = df_bio.groupby(df_bio['date'].dt.to_period('M'))['total_bio_updates'].sum()
monthly_demo = df_demo.groupby(df_demo['date'].dt.to_period('M'))['total_demo_updates'].sum()

# Convert to timestamp
monthly_enrol.index = monthly_enrol.index.to_timestamp()
monthly_bio.index = monthly_bio.index.to_timestamp()
monthly_demo.index = monthly_demo.index.to_timestamp()

print(f"\n📅 Monthly Activity Summary:")
print(f"   Enrolments - Avg: {monthly_enrol.mean():>12,.0f} | Peak: {monthly_enrol.max():>12,.0f}")
print(f"   Biometric  - Avg: {monthly_bio.mean():>12,.0f} | Peak: {monthly_bio.max():>12,.0f}")
print(f"   Demographic - Avg: {monthly_demo.mean():>12,.0f} | Peak: {monthly_demo.max():>12,.0f}")

# VISUALIZATION 3: Monthly Trends
fig, axes = plt.subplots(3, 1, figsize=(18, 14))

# Enrolment
axes[0].plot(monthly_enrol.index, monthly_enrol.values, marker='o', linewidth=2.5, 
            markersize=8, color='#2ecc71')
axes[0].fill_between(monthly_enrol.index, monthly_enrol.values, alpha=0.3, color='#2ecc71')
axes[0].axhline(y=monthly_enrol.mean(), color='red', linestyle='--', linewidth=2, label=f'Average: {monthly_enrol.mean():,.0f}')
axes[0].set_title('Monthly Aadhaar Enrolment Trends', fontsize=16, fontweight='bold', pad=15)
axes[0].set_ylabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[0].grid(True, alpha=0.4, linestyle='--')
axes[0].legend(fontsize=11)
axes[0].ticklabel_format(style='plain', axis='y')

# Biometric
axes[1].plot(monthly_bio.index, monthly_bio.values, marker='s', linewidth=2.5, 
            markersize=8, color='#3498db')
axes[1].fill_between(monthly_bio.index, monthly_bio.values, alpha=0.3, color='#3498db')
axes[1].axhline(y=monthly_bio.mean(), color='red', linestyle='--', linewidth=2, label=f'Average: {monthly_bio.mean():,.0f}')
axes[1].set_title('Monthly Biometric Update Trends', fontsize=16, fontweight='bold', pad=15)
axes[1].set_ylabel('Total Updates', fontsize=13, fontweight='bold')
axes[1].grid(True, alpha=0.4, linestyle='--')
axes[1].legend(fontsize=11)
axes[1].ticklabel_format(style='plain', axis='y')

# Demographic
axes[2].plot(monthly_demo.index, monthly_demo.values, marker='^', linewidth=2.5, 
            markersize=8, color='#9b59b6')
axes[2].fill_between(monthly_demo.index, monthly_demo.values, alpha=0.3, color='#9b59b6')
axes[2].axhline(y=monthly_demo.mean(), color='red', linestyle='--', linewidth=2, label=f'Average: {monthly_demo.mean():,.0f}')
axes[2].set_title('Monthly Demographic Update Trends', fontsize=16, fontweight='bold', pad=15)
axes[2].set_ylabel('Total Updates', fontsize=13, fontweight='bold')
axes[2].set_xlabel('Month', fontsize=13, fontweight='bold')
axes[2].grid(True, alpha=0.4, linestyle='--')
axes[2].legend(fontsize=11)
axes[2].ticklabel_format(style='plain', axis='y')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '03_monthly_trends.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 03_monthly_trends.png")
plt.close()

# ============================================
# EDA 4: AGE GROUP DISTRIBUTIONS
# ============================================
print(f"\n{'=' * 120}")
print("EDA 4: AGE GROUP DISTRIBUTIONS")
print(f"{'=' * 120}")

age_dist = {
    'Children (0-5)': df_enrol['age_0_5'].sum(),
    'School Age (5-17)': df_enrol['age_5_17'].sum(),
    'Adults (18+)': df_enrol['age_18_greater'].sum()
}

total_enrol = sum(age_dist.values())

print(f"\n📊 Overall Age Distribution:")
for group, count in age_dist.items():
    pct = (count / total_enrol) * 100
    print(f"   {group:20s} : {count:>12,} ({pct:>5.2f}%)")

# VISUALIZATION 4
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Pie chart
colors = ['#ff9999', '#66b3ff', '#99ff99']
wedges, texts, autotexts = axes[0].pie(age_dist.values(), labels=age_dist.keys(), 
                                       autopct='%1.1f%%', startangle=90, colors=colors,
                                       textprops={'fontsize': 13, 'fontweight': 'bold'})
axes[0].set_title('Age Distribution in Enrolments', fontsize=16, fontweight='bold', pad=15)

# Bar chart
bars = axes[1].bar(age_dist.keys(), age_dist.values(), color=colors, edgecolor='black', linewidth=2)
axes[1].set_title('Enrolments by Age Group', fontsize=16, fontweight='bold', pad=15)
axes[1].set_ylabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[1].ticklabel_format(style='plain', axis='y')
axes[1].grid(axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}\n({height/total_enrol*100:.1f}%)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '04_age_distributions.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 04_age_distributions.png")
plt.close()

# ============================================
# SAVE SUMMARY STATISTICS
# ============================================
print(f"\n{'=' * 120}")
print("GENERATING COMPREHENSIVE STATISTICS")
print(f"{'=' * 120}")

# Create state comparison table
comparison_data = []
for state in state_enrol.index:
    comparison_data.append({
        'State': state.title(),
        'Total_Enrolments': state_enrol.get(state, 0),
        'Enrol_vs_Avg_%': state_enrol_deviation.get(state, 0),
        'Total_Bio_Updates': state_bio.get(state, 0),
        'Bio_vs_Avg_%': state_bio_deviation.get(state, 0),
        'Total_Demo_Updates': state_demo.get(state, 0),
        'Demo_vs_Avg_%': state_demo_deviation.get(state, 0)
    })

comparison_df = pd.DataFrame(comparison_data)
comparison_df = comparison_df.sort_values('Total_Enrolments', ascending=False)
comparison_df.to_csv(os.path.join(RESULTS_FOLDER, 'state_comparison_vs_national_average.csv'), index=False)

print(f"\n✓ Saved: state_comparison_vs_national_average.csv")
print(f"\nTop 5 States Summary:")
print(comparison_df.head().to_string(index=False))

# ============================================
# FINAL SUMMARY
# ============================================
print(f"\n{'=' * 120}")
print("✅ EXPLORATORY DATA ANALYSIS COMPLETE!")
print(f"{'=' * 120}")

print(f"\n📊 VISUALIZATIONS CREATED:")
print(f"   1. 01_state_enrolment_vs_average.png  - States vs National Average (Enrolment)")
print(f"   2. 02_state_updates_vs_average.png    - States vs National Average (Updates)")
print(f"   3. 03_monthly_trends.png              - Monthly patterns with averages")
print(f"   4. 04_age_distributions.png           - Age group breakdowns")

print(f"\n🎯 KEY INSIGHTS:")
print(f"   ✓ Identified states significantly below national average")
print(f"   ✓ Showed % deviation from baseline for each state")
print(f"   ✓ Clear visual indicators (above/below average)")
print(f"   ✓ Meaningful comparisons for policy decisions")

print(f"\n📈 APPROACH BENEFITS:")
print(f"   ✓ National average provides clear baseline")
print(f"   ✓ % deviation shows relative performance")
print(f"   ✓ Easy to identify underperforming states")
print(f"   ✓ Actionable insights for interventions")

print(f"\n{'=' * 120}")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'=' * 120}")
