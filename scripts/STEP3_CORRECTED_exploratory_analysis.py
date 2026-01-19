"""
STEP 3 CORRECTED: EXPLORATORY DATA ANALYSIS (EDA)
==================================================
CORRECTION: Update rates removed (misleading when >100%)
Instead showing:
1. Absolute update counts by state
2. Update activity intensity
3. Proper comparisons

Focus Areas:
1. States with highest/lowest enrolment
2. States with highest/lowest update ACTIVITY (not rates)
3. Time trends (monthly patterns)
4. Age group distributions
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
print("EXPLORATORY DATA ANALYSIS (EDA) - CORRECTED")
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

print("\n⚠️  NOTE: Update rates >100% indicate that updates include historical enrolments")
print("         (People enrolled years ago are updating now)")
print("         Therefore, we analyze ABSOLUTE UPDATE ACTIVITY instead of rates")

# ============================================
# EDA 1: STATES WITH HIGHEST/LOWEST ENROLMENT
# ============================================
print(f"\n{'=' * 120}")
print("EDA 1: STATES WITH HIGHEST/LOWEST ENROLMENT")
print(f"{'=' * 120}")

# Calculate state-wise totals (exclude 'unknown')
state_enrol = df_enrol[df_enrol['state'] != 'unknown'].groupby('state')['total_enrolments'].sum().sort_values(ascending=False)

print(f"\n🔝 TOP 10 STATES - HIGHEST ENROLMENT:")
print(f"{'Rank':<6} {'State':<40} {'Total Enrolments':>20}")
print("-" * 70)
for i, (state, count) in enumerate(state_enrol.head(10).items(), 1):
    print(f"{i:<6} {state.title():<40} {count:>20,}")

print(f"\n🔻 BOTTOM 10 STATES - LOWEST ENROLMENT:")
print(f"{'Rank':<6} {'State':<40} {'Total Enrolments':>20}")
print("-" * 70)
for i, (state, count) in enumerate(state_enrol.tail(10).items(), 1):
    print(f"{i:<6} {state.title():<40} {count:>20,}")

# VISUALIZATION 1: Top and Bottom States
fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# Top 15 states
top_15 = state_enrol.head(15)
bars1 = axes[0].barh(range(len(top_15)), top_15.values, color='#2ecc71', edgecolor='black', linewidth=1.5)
axes[0].set_yticks(range(len(top_15)))
axes[0].set_yticklabels([s.title() for s in top_15.index], fontsize=11)
axes[0].set_xlabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[0].set_title('Top 15 States - Highest Aadhaar Enrolments', fontsize=15, fontweight='bold', pad=20)
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3, linestyle='--')

for i, (bar, val) in enumerate(zip(bars1, top_15.values)):
    axes[0].text(val, i, f' {val:,.0f}', va='center', fontsize=10, fontweight='bold')

# Bottom 15 states
bottom_15 = state_enrol.tail(15)
bars2 = axes[1].barh(range(len(bottom_15)), bottom_15.values, color='#e74c3c', edgecolor='black', linewidth=1.5)
axes[1].set_yticks(range(len(bottom_15)))
axes[1].set_yticklabels([s.title() for s in bottom_15.index], fontsize=11)
axes[1].set_xlabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[1].set_title('Bottom 15 States - Lowest Aadhaar Enrolments\n⚠️ Potential Low Coverage Areas', 
                  fontsize=15, fontweight='bold', pad=20)
axes[1].invert_yaxis()
axes[1].grid(axis='x', alpha=0.3, linestyle='--')

for i, (bar, val) in enumerate(zip(bars2, bottom_15.values)):
    axes[1].text(val, i, f' {val:,.0f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '01_state_enrolment_comparison.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 01_state_enrolment_comparison.png")
plt.close()

# ============================================
# EDA 2: STATES WITH HIGHEST/LOWEST UPDATE ACTIVITY
# ============================================
print(f"\n{'=' * 120}")
print("EDA 2: STATES WITH HIGHEST/LOWEST UPDATE ACTIVITY")
print("(Showing absolute counts - NOT rates, as rates >100% indicate historical updates)")
print(f"{'=' * 120}")

# Calculate state-wise update totals
state_bio = df_bio[df_bio['state'] != 'unknown'].groupby('state')['total_bio_updates'].sum().sort_values(ascending=False)
state_demo = df_demo[df_demo['state'] != 'unknown'].groupby('state')['total_demo_updates'].sum().sort_values(ascending=False)

print(f"\n📊 BIOMETRIC UPDATE ACTIVITY:")
print(f"\n🔝 TOP 10 STATES - HIGHEST Biometric Update Activity:")
print(f"{'Rank':<6} {'State':<40} {'Total Updates':>20}")
print("-" * 70)
for i, (state, count) in enumerate(state_bio.head(10).items(), 1):
    print(f"{i:<6} {state.title():<40} {count:>20,}")

print(f"\n🔻 BOTTOM 10 STATES - LOWEST Biometric Update Activity:")
print(f"{'Rank':<6} {'State':<40} {'Total Updates':>20}")
print("-" * 70)
for i, (state, count) in enumerate(state_bio.tail(10).items(), 1):
    print(f"{i:<6} {state.title():<40} {count:>20,}")

print(f"\n📊 DEMOGRAPHIC UPDATE ACTIVITY:")
print(f"\n🔝 TOP 10 STATES - HIGHEST Demographic Update Activity:")
print(f"{'Rank':<6} {'State':<40} {'Total Updates':>20}")
print("-" * 70)
for i, (state, count) in enumerate(state_demo.head(10).items(), 1):
    print(f"{i:<6} {state.title():<40} {count:>20,}")

print(f"\n🔻 BOTTOM 10 STATES - LOWEST Demographic Update Activity:")
print(f"{'Rank':<6} {'State':<40} {'Total Updates':>20}")
print("-" * 70)
for i, (state, count) in enumerate(state_demo.tail(10).items(), 1):
    print(f"{i:<6} {state.title():<40} {count:>20,}")

# VISUALIZATION 2: Update Activity
fig, axes = plt.subplots(2, 2, figsize=(20, 16))

# Biometric - Top 15
top_bio = state_bio.head(15)
bars1 = axes[0, 0].barh(range(len(top_bio)), top_bio.values, color='#3498db', edgecolor='black', linewidth=1.5)
axes[0, 0].set_yticks(range(len(top_bio)))
axes[0, 0].set_yticklabels([s.title() for s in top_bio.index], fontsize=10)
axes[0, 0].set_xlabel('Total Biometric Updates', fontsize=12, fontweight='bold')
axes[0, 0].set_title('Top 15 States - Highest Biometric Update Activity', fontsize=14, fontweight='bold')
axes[0, 0].invert_yaxis()
axes[0, 0].grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars1, top_bio.values)):
    axes[0, 0].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

# Biometric - Bottom 15
bottom_bio = state_bio.tail(15)
bars2 = axes[0, 1].barh(range(len(bottom_bio)), bottom_bio.values, color='#e74c3c', edgecolor='black', linewidth=1.5)
axes[0, 1].set_yticks(range(len(bottom_bio)))
axes[0, 1].set_yticklabels([s.title() for s in bottom_bio.index], fontsize=10)
axes[0, 1].set_xlabel('Total Biometric Updates', fontsize=12, fontweight='bold')
axes[0, 1].set_title('Bottom 15 States - Lowest Biometric Update Activity\n⚠️ Low Update Compliance', 
                     fontsize=14, fontweight='bold')
axes[0, 1].invert_yaxis()
axes[0, 1].grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars2, bottom_bio.values)):
    axes[0, 1].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

# Demographic - Top 15
top_demo = state_demo.head(15)
bars3 = axes[1, 0].barh(range(len(top_demo)), top_demo.values, color='#9b59b6', edgecolor='black', linewidth=1.5)
axes[1, 0].set_yticks(range(len(top_demo)))
axes[1, 0].set_yticklabels([s.title() for s in top_demo.index], fontsize=10)
axes[1, 0].set_xlabel('Total Demographic Updates', fontsize=12, fontweight='bold')
axes[1, 0].set_title('Top 15 States - Highest Demographic Update Activity', fontsize=14, fontweight='bold')
axes[1, 0].invert_yaxis()
axes[1, 0].grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars3, top_demo.values)):
    axes[1, 0].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

# Demographic - Bottom 15
bottom_demo = state_demo.tail(15)
bars4 = axes[1, 1].barh(range(len(bottom_demo)), bottom_demo.values, color='#e67e22', edgecolor='black', linewidth=1.5)
axes[1, 1].set_yticks(range(len(bottom_demo)))
axes[1, 1].set_yticklabels([s.title() for s in bottom_demo.index], fontsize=10)
axes[1, 1].set_xlabel('Total Demographic Updates', fontsize=12, fontweight='bold')
axes[1, 1].set_title('Bottom 15 States - Lowest Demographic Update Activity\n⚠️ Low Update Awareness', 
                     fontsize=14, fontweight='bold')
axes[1, 1].invert_yaxis()
axes[1, 1].grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars4, bottom_demo.values)):
    axes[1, 1].text(val, i, f' {val:,.0f}', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '02_state_update_activity.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 02_state_update_activity.png")
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

# Convert period to timestamp for plotting
monthly_enrol.index = monthly_enrol.index.to_timestamp()
monthly_bio.index = monthly_bio.index.to_timestamp()
monthly_demo.index = monthly_demo.index.to_timestamp()

print(f"\n📅 Date Ranges:")
print(f"   Enrolment: {monthly_enrol.index.min().strftime('%B %Y')} to {monthly_enrol.index.max().strftime('%B %Y')}")
print(f"   Biometric: {monthly_bio.index.min().strftime('%B %Y')} to {monthly_bio.index.max().strftime('%B %Y')}")
print(f"   Demographic: {monthly_demo.index.min().strftime('%B %Y')} to {monthly_demo.index.max().strftime('%B %Y')}")

print(f"\n📊 Monthly Averages:")
print(f"   Enrolments: {monthly_enrol.mean():>15,.0f}")
print(f"   Biometric Updates: {monthly_bio.mean():>15,.0f}")
print(f"   Demographic Updates: {monthly_demo.mean():>15,.0f}")

# VISUALIZATION 3: Monthly Trends
fig, axes = plt.subplots(3, 1, figsize=(18, 14))

# Enrolment trend
axes[0].plot(monthly_enrol.index, monthly_enrol.values, marker='o', linewidth=2.5, 
            markersize=8, color='#2ecc71', label='Monthly Enrolments')
axes[0].fill_between(monthly_enrol.index, monthly_enrol.values, alpha=0.3, color='#2ecc71')
axes[0].set_title('Monthly Aadhaar Enrolment Trends', fontsize=16, fontweight='bold', pad=15)
axes[0].set_ylabel('Total Enrolments', fontsize=13, fontweight='bold')
axes[0].grid(True, alpha=0.4, linestyle='--')
axes[0].legend(fontsize=11, loc='best')
axes[0].ticklabel_format(style='plain', axis='y')

if len(monthly_enrol) > 1:
    z = np.polyfit(range(len(monthly_enrol)), monthly_enrol.values, 1)
    p = np.poly1d(z)
    axes[0].plot(monthly_enrol.index, p(range(len(monthly_enrol))), "--", 
                color='red', linewidth=2, alpha=0.7, label='Trend Line')
    axes[0].legend(fontsize=11)

# Biometric trend
axes[1].plot(monthly_bio.index, monthly_bio.values, marker='s', linewidth=2.5, 
            markersize=8, color='#3498db', label='Monthly Biometric Updates')
axes[1].fill_between(monthly_bio.index, monthly_bio.values, alpha=0.3, color='#3498db')
axes[1].set_title('Monthly Biometric Update Trends', fontsize=16, fontweight='bold', pad=15)
axes[1].set_ylabel('Total Biometric Updates', fontsize=13, fontweight='bold')
axes[1].grid(True, alpha=0.4, linestyle='--')
axes[1].legend(fontsize=11, loc='best')
axes[1].ticklabel_format(style='plain', axis='y')

if len(monthly_bio) > 1:
    z = np.polyfit(range(len(monthly_bio)), monthly_bio.values, 1)
    p = np.poly1d(z)
    axes[1].plot(monthly_bio.index, p(range(len(monthly_bio))), "--", 
                color='red', linewidth=2, alpha=0.7, label='Trend Line')
    axes[1].legend(fontsize=11)

# Demographic trend
axes[2].plot(monthly_demo.index, monthly_demo.values, marker='^', linewidth=2.5, 
            markersize=8, color='#9b59b6', label='Monthly Demographic Updates')
axes[2].fill_between(monthly_demo.index, monthly_demo.values, alpha=0.3, color='#9b59b6')
axes[2].set_title('Monthly Demographic Update Trends', fontsize=16, fontweight='bold', pad=15)
axes[2].set_ylabel('Total Demographic Updates', fontsize=13, fontweight='bold')
axes[2].set_xlabel('Month', fontsize=13, fontweight='bold')
axes[2].grid(True, alpha=0.4, linestyle='--')
axes[2].legend(fontsize=11, loc='best')
axes[2].ticklabel_format(style='plain', axis='y')

if len(monthly_demo) > 1:
    z = np.polyfit(range(len(monthly_demo)), monthly_demo.values, 1)
    p = np.poly1d(z)
    axes[2].plot(monthly_demo.index, p(range(len(monthly_demo))), "--", 
                color='red', linewidth=2, alpha=0.7, label='Trend Line')
    axes[2].legend(fontsize=11)

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

# Overall age distribution
age_dist = {
    'Children (0-5)': df_enrol['age_0_5'].sum(),
    'School Age (5-17)': df_enrol['age_5_17'].sum(),
    'Adults (18+)': df_enrol['age_18_greater'].sum()
}

total_enrol = sum(age_dist.values())

print(f"\n📊 Overall Age Distribution:")
print(f"{'Age Group':<25} {'Count':>15} {'Percentage':>15}")
print("-" * 60)
for group, count in age_dist.items():
    pct = (count / total_enrol) * 100
    print(f"{group:<25} {count:>15,} {pct:>14.2f}%")

# Biometric update age distribution
bio_age_dist = {
    'School Age (5-17)': df_bio['bio_age_5_17'].sum(),
    'Adults (17+)': df_bio['bio_age_17_'].sum()
}

total_bio = sum(bio_age_dist.values())

print(f"\n📊 Biometric Update Age Distribution:")
print(f"{'Age Group':<25} {'Count':>15} {'Percentage':>15}")
print("-" * 60)
for group, count in bio_age_dist.items():
    pct = (count / total_bio) * 100
    print(f"{group:<25} {count:>15,} {pct:>14.2f}%")

# VISUALIZATION 4: Age Distribution
fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Pie chart - Enrolment
colors_enrol = ['#ff9999', '#66b3ff', '#99ff99']
wedges, texts, autotexts = axes[0, 0].pie(age_dist.values(), labels=age_dist.keys(), 
                                           autopct='%1.1f%%', startangle=90, 
                                           colors=colors_enrol, textprops={'fontsize': 12, 'fontweight': 'bold'})
axes[0, 0].set_title('Overall Age Distribution in Enrolments', fontsize=14, fontweight='bold', pad=15)

# Bar chart - Enrolment
bars1 = axes[0, 1].bar(age_dist.keys(), age_dist.values(), color=colors_enrol, 
                       edgecolor='black', linewidth=2)
axes[0, 1].set_title('Enrolments by Age Group', fontsize=14, fontweight='bold', pad=15)
axes[0, 1].set_ylabel('Total Enrolments', fontsize=12, fontweight='bold')
axes[0, 1].ticklabel_format(style='plain', axis='y')
axes[0, 1].grid(axis='y', alpha=0.3)

for bar in bars1:
    height = bar.get_height()
    axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}\n({height/total_enrol*100:.1f}%)',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

# Pie chart - Biometric
colors_bio = ['#ffcc99', '#c2c2f0']
wedges, texts, autotexts = axes[1, 0].pie(bio_age_dist.values(), labels=bio_age_dist.keys(),
                                           autopct='%1.1f%%', startangle=90,
                                           colors=colors_bio, textprops={'fontsize': 12, 'fontweight': 'bold'})
axes[1, 0].set_title('Biometric Update Age Distribution', fontsize=14, fontweight='bold', pad=15)

# Bar chart - Biometric
bars2 = axes[1, 1].bar(bio_age_dist.keys(), bio_age_dist.values(), color=colors_bio,
                       edgecolor='black', linewidth=2)
axes[1, 1].set_title('Biometric Updates by Age Group', fontsize=14, fontweight='bold', pad=15)
axes[1, 1].set_ylabel('Total Biometric Updates', fontsize=12, fontweight='bold')
axes[1, 1].ticklabel_format(style='plain', axis='y')
axes[1, 1].grid(axis='y', alpha=0.3)

for bar in bars2:
    height = bar.get_height()
    axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}\n({height/total_bio*100:.1f}%)',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_FOLDER, '04_age_distributions.png'), dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: 04_age_distributions.png")
plt.close()

# ============================================
# SAVE SUMMARY STATISTICS
# ============================================
print(f"\n{'=' * 120}")
print("GENERATING SUMMARY STATISTICS")
print(f"{'=' * 120}")

summary_stats = {
    'Metric': [
        'Total Enrolments',
        'Total Biometric Updates',
        'Total Demographic Updates',
        'Children (0-5) Enrolments',
        'School Age (5-17) Enrolments',
        'Adults (18+) Enrolments',
        'Biometric Updates (5-17)',
        'Biometric Updates (17+)',
        'Number of Valid States/UTs',
        'Number of Districts',
        'Average Monthly Enrolments',
        'Average Monthly Biometric Updates',
        'Average Monthly Demographic Updates',
    ],
    'Value': [
        df_enrol['total_enrolments'].sum(),
        df_bio['total_bio_updates'].sum(),
        df_demo['total_demo_updates'].sum(),
        df_enrol['age_0_5'].sum(),
        df_enrol['age_5_17'].sum(),
        df_enrol['age_18_greater'].sum(),
        df_bio['bio_age_5_17'].sum(),
        df_bio['bio_age_17_'].sum(),
        len(state_enrol),
        df_enrol[df_enrol['state'] != 'unknown']['district'].nunique(),
        monthly_enrol.mean(),
        monthly_bio.mean(),
        monthly_demo.mean(),
    ]
}

summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv(os.path.join(RESULTS_FOLDER, 'eda_summary_statistics.csv'), index=False)

print(f"\n📊 KEY STATISTICS:")
for metric, value in zip(summary_stats['Metric'], summary_stats['Value']):
    print(f"   {metric:50s} : {value:>15,.0f}")

print(f"\n✓ Saved: eda_summary_statistics.csv")

# ============================================
# FINAL SUMMARY
# ============================================
print(f"\n{'=' * 120}")
print("✅ EXPLORATORY DATA ANALYSIS COMPLETE!")
print(f"{'=' * 120}")

print(f"\n📊 VISUALIZATIONS CREATED:")
print(f"   1. 01_state_enrolment_comparison.png  - Top/Bottom states by enrolment")
print(f"   2. 02_state_update_activity.png       - Top/Bottom states by update activity")
print(f"   3. 03_monthly_trends.png              - Monthly patterns over time")
print(f"   4. 04_age_distributions.png           - Age group breakdowns")

print(f"\n⚠️  IMPORTANT NOTE ON UPDATE ANALYSIS:")
print(f"   Update 'rates' >100% are NORMAL because:")
print(f"   - Updates include people enrolled in previous years")
print(f"   - Our enrolment data is only from March-October 2025")
print(f"   - A person enrolled in 2010 might update in 2025")
print(f"   Therefore, we show ABSOLUTE UPDATE COUNTS, not rates")

print(f"\n📁 OUTPUT LOCATIONS:")
print(f"   Visualizations: {VIZ_FOLDER}")
print(f"   Statistics: {RESULTS_FOLDER}")

print(f"\n🔍 KEY FINDINGS:")
print(f"   ✓ Identified states with lowest enrolment (coverage gaps)")
print(f"   ✓ Identified states with lowest update activity (compliance gaps)")
print(f"   ✓ Analyzed monthly trends (seasonal patterns)")
print(f"   ✓ Analyzed age distributions (demographic patterns)")

print(f"\n{'=' * 120}")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'=' * 120}")
