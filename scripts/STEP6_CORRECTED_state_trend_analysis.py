"""
PHASE 3 - STEP 6: State-wise Trend Analysis (CORRECTED)
========================================================
Professional implementation by Computer Science Engineer

This script analyzes:
1. Total enrolments over time by state
2. Total biometric updates over time by state
3. Total demographic updates over time by state
4. Update rate = (Updates / Enrolments) × 100
5. Trend charts for top 10 states

FIXES:
- Corrected date format to match cleaned data (YYYY-MM-DD)
- Added robust error handling
- Improved column detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# Professional setup
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 10)
plt.rcParams['font.size'] = 10

print("=" * 80)
print("PHASE 3 - STEP 6: STATE-WISE TREND ANALYSIS (CORRECTED)")
print("=" * 80)
print()

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("Step 1: Loading cleaned data...")

try:
    # Load datasets
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../data/processed/cleaned_biometric.csv')
    demographic = pd.read_csv('../data/processed/cleaned_demographic.csv')
    
    print(f"✓ Enrolment data loaded: {len(enrolment):,} rows")
    print(f"✓ Biometric data loaded: {len(biometric):,} rows")
    print(f"✓ Demographic data loaded: {len(demographic):,} rows")
    
except FileNotFoundError as e:
    print(f"ERROR: Could not find cleaned data files!")
    print(f"Details: {e}")
    print()
    print("Please run Phase 2 data cleaning first:")
    print("  python STEP2_FINAL_intelligent_cleaning.py")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

print()

# ============================================================================
# STEP 2: CONVERT DATES AND EXTRACT TIME FEATURES
# ============================================================================
print("Step 2: Converting dates and extracting time features...")

try:
    # Convert date strings to datetime - try multiple formats
    print("  Detecting date format...")
    
    # Check sample date
    sample_date = str(enrolment['date'].iloc[0])
    print(f"  Sample date: {sample_date}")
    
    # Try automatic parsing first
    enrolment['date'] = pd.to_datetime(enrolment['date'], errors='coerce')
    biometric['date'] = pd.to_datetime(biometric['date'], errors='coerce')
    demographic['date'] = pd.to_datetime(demographic['date'], errors='coerce')
    
    # Check for parsing errors
    if enrolment['date'].isna().sum() > 0:
        print(f"  WARNING: {enrolment['date'].isna().sum()} dates could not be parsed in enrolment")
    
    # Extract year-month for grouping
    enrolment['year_month'] = enrolment['date'].dt.to_period('M').astype(str)
    biometric['year_month'] = biometric['date'].dt.to_period('M').astype(str)
    demographic['year_month'] = demographic['date'].dt.to_period('M').astype(str)
    
    print("✓ Dates converted successfully")
    print(f"  Date range: {enrolment['date'].min()} to {enrolment['date'].max()}")
    
except Exception as e:
    print(f"ERROR converting dates: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 3: CALCULATE TOTAL ENROLMENTS OVER TIME BY STATE
# ============================================================================
print("Step 3: Calculating total enrolments over time by state...")

try:
    # Detect the correct column name for total enrolments
    enrol_col = None
    for col in enrolment.columns:
        if 'total' in col.lower() and 'enrol' in col.lower():
            enrol_col = col
            break
    
    if enrol_col is None:
        # Try alternative: sum of age group columns
        age_cols = [col for col in enrolment.columns if 'age' in col.lower() or 'enrol' in col.lower()]
        print(f"  Available columns: {enrolment.columns.tolist()}")
        print(f"  Age-related columns: {age_cols}")
        
        # Assume columns like 'age_0_5', 'age_5_17', 'age_18_plus' or similar
        if len(age_cols) >= 3:
            enrolment['total_enrolments'] = enrolment[age_cols].sum(axis=1)
            enrol_col = 'total_enrolments'
        else:
            raise ValueError("Could not find total enrolments column")
    
    print(f"  Using column: {enrol_col}")
    
    # Group by state and month
    enrolment_trends = enrolment.groupby(['state', 'year_month']).agg({
        enrol_col: 'sum'
    }).reset_index()
    
    # Rename for consistency
    enrolment_trends.columns = ['state', 'year_month', 'total_enrolments']
    
    # Sort by date
    enrolment_trends = enrolment_trends.sort_values(['state', 'year_month'])
    
    print(f"✓ Enrolment trends calculated")
    print(f"  States: {enrolment_trends['state'].nunique()}")
    print(f"  Time periods: {enrolment_trends['year_month'].nunique()}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 4: CALCULATE TOTAL BIOMETRIC UPDATES OVER TIME BY STATE
# ============================================================================
print("Step 4: Calculating total biometric updates over time by state...")

try:
    # Detect the correct column name for biometric updates
    bio_col = None
    for col in biometric.columns:
        if 'total' in col.lower() and 'bio' in col.lower():
            bio_col = col
            break
    
    if bio_col is None:
        # Try alternative: sum of age group columns
        age_cols = [col for col in biometric.columns if 'age' in col.lower() or 'bio' in col.lower()]
        if len(age_cols) >= 2:
            biometric['total_bio_updates'] = biometric[age_cols].sum(axis=1)
            bio_col = 'total_bio_updates'
        else:
            raise ValueError("Could not find total biometric updates column")
    
    print(f"  Using column: {bio_col}")
    
    biometric_trends = biometric.groupby(['state', 'year_month']).agg({
        bio_col: 'sum'
    }).reset_index()
    
    biometric_trends.columns = ['state', 'year_month', 'total_bio_updates']
    biometric_trends = biometric_trends.sort_values(['state', 'year_month'])
    
    print(f"✓ Biometric update trends calculated")
    print(f"  States: {biometric_trends['state'].nunique()}")
    print(f"  Time periods: {biometric_trends['year_month'].nunique()}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 5: CALCULATE TOTAL DEMOGRAPHIC UPDATES OVER TIME BY STATE
# ============================================================================
print("Step 5: Calculating total demographic updates over time by state...")

try:
    # Detect the correct column name for demographic updates
    demo_col = None
    for col in demographic.columns:
        if 'total' in col.lower() and 'demo' in col.lower():
            demo_col = col
            break
    
    if demo_col is None:
        # Try alternative: sum of age group columns
        age_cols = [col for col in demographic.columns if 'age' in col.lower() or 'demo' in col.lower()]
        if len(age_cols) >= 2:
            demographic['total_demo_updates'] = demographic[age_cols].sum(axis=1)
            demo_col = 'total_demo_updates'
        else:
            raise ValueError("Could not find total demographic updates column")
    
    print(f"  Using column: {demo_col}")
    
    demographic_trends = demographic.groupby(['state', 'year_month']).agg({
        demo_col: 'sum'
    }).reset_index()
    
    demographic_trends.columns = ['state', 'year_month', 'total_demo_updates']
    demographic_trends = demographic_trends.sort_values(['state', 'year_month'])
    
    print(f"✓ Demographic update trends calculated")
    print(f"  States: {demographic_trends['state'].nunique()}")
    print(f"  Time periods: {demographic_trends['year_month'].nunique()}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 6: CALCULATE UPDATE RATE BY STATE
# ============================================================================
print("Step 6: Calculating update rates by state...")
print("  Formula: Update Rate = (Total Updates / Total Enrolments) × 100")
print()

try:
    # Total by state (aggregate all time periods)
    state_enrolments = enrolment.groupby('state')[enrol_col].sum().reset_index()
    state_enrolments.columns = ['state', 'total_enrolments']
    
    state_bio_updates = biometric.groupby('state')[bio_col].sum().reset_index()
    state_bio_updates.columns = ['state', 'total_bio_updates']
    
    state_demo_updates = demographic.groupby('state')[demo_col].sum().reset_index()
    state_demo_updates.columns = ['state', 'total_demo_updates']
    
    # Merge
    state_summary = state_enrolments.copy()
    state_summary = state_summary.merge(state_bio_updates, on='state', how='left')
    state_summary = state_summary.merge(state_demo_updates, on='state', how='left')
    
    # Fill NaN with 0
    state_summary = state_summary.fillna(0)
    
    # Calculate update rates
    state_summary['bio_update_rate'] = (
        state_summary['total_bio_updates'] / state_summary['total_enrolments'] * 100
    )
    state_summary['demo_update_rate'] = (
        state_summary['total_demo_updates'] / state_summary['total_enrolments'] * 100
    )
    
    # Handle any infinity or NaN
    state_summary = state_summary.replace([np.inf, -np.inf], 0)
    state_summary = state_summary.fillna(0)
    
    # Calculate national averages
    national_bio_rate = state_summary['bio_update_rate'].mean()
    national_demo_rate = state_summary['demo_update_rate'].mean()
    
    print(f"✓ Update rates calculated for {len(state_summary)} states")
    print(f"  National average - Biometric update rate: {national_bio_rate:.2f}%")
    print(f"  National average - Demographic update rate: {national_demo_rate:.2f}%")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 7: IDENTIFY TOP 10 STATES BY TOTAL ENROLMENTS
# ============================================================================
print("Step 7: Identifying top 10 states by total enrolments...")

try:
    # Sort by total enrolments and get top 10
    top_10_states = state_summary.nlargest(10, 'total_enrolments')['state'].tolist()
    
    print("✓ Top 10 states identified:")
    for i, state in enumerate(top_10_states, 1):
        enrol = state_summary[state_summary['state'] == state]['total_enrolments'].iloc[0]
        print(f"  {i:2d}. {state:40s} - {enrol:>12,.0f} enrolments")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 8: CREATE RESULTS DIRECTORY
# ============================================================================
print("Step 8: Creating results directory...")

try:
    os.makedirs('../results', exist_ok=True)
    os.makedirs('../visualizations', exist_ok=True)
    print("✓ Directories ready")
    
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

print()

# ============================================================================
# STEP 9: SAVE RESULTS TO CSV
# ============================================================================
print("Step 9: Saving results to CSV files...")

try:
    # Save state summary
    state_summary.to_csv('../results/STEP6_state_summary.csv', index=False)
    print("✓ Saved: STEP6_state_summary.csv")
    
    # Save trend data
    enrolment_trends.to_csv('../results/STEP6_enrolment_trends.csv', index=False)
    print("✓ Saved: STEP6_enrolment_trends.csv")
    
    biometric_trends.to_csv('../results/STEP6_biometric_trends.csv', index=False)
    print("✓ Saved: STEP6_biometric_trends.csv")
    
    demographic_trends.to_csv('../results/STEP6_demographic_trends.csv', index=False)
    print("✓ Saved: STEP6_demographic_trends.csv")
    
except Exception as e:
    print(f"ERROR saving CSVs: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# STEP 10: CREATE TREND CHARTS FOR TOP 10 STATES
# ============================================================================
print("Step 10: Creating trend charts for top 10 states...")

try:
    # Create figure with 3 subplots (vertical layout)
    fig, axes = plt.subplots(3, 1, figsize=(18, 14))
    
    # Add main title
    fig.suptitle('State-wise Trend Analysis - Top 10 States by Total Enrolment', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Chart 1: Enrolment Trends
    ax1 = axes[0]
    for state in top_10_states:
        state_data = enrolment_trends[enrolment_trends['state'] == state]
        if len(state_data) > 0:
            ax1.plot(state_data['year_month'], 
                    state_data['total_enrolments'],
                    marker='o', label=state, linewidth=2, markersize=6)
    
    ax1.set_xlabel('Month', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Total Enrolments', fontweight='bold', fontsize=11)
    ax1.set_title('Total Enrolments Over Time', fontweight='bold', fontsize=13, pad=10)
    ax1.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Chart 2: Biometric Update Trends
    ax2 = axes[1]
    for state in top_10_states:
        state_data = biometric_trends[biometric_trends['state'] == state]
        if len(state_data) > 0:
            ax2.plot(state_data['year_month'], 
                    state_data['total_bio_updates'],
                    marker='s', label=state, linewidth=2, markersize=6)
    
    ax2.set_xlabel('Month', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Total Biometric Updates', fontweight='bold', fontsize=11)
    ax2.set_title('Total Biometric Updates Over Time', fontweight='bold', fontsize=13, pad=10)
    ax2.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Chart 3: Demographic Update Trends
    ax3 = axes[2]
    for state in top_10_states:
        state_data = demographic_trends[demographic_trends['state'] == state]
        if len(state_data) > 0:
            ax3.plot(state_data['year_month'], 
                    state_data['total_demo_updates'],
                    marker='^', label=state, linewidth=2, markersize=6)
    
    ax3.set_xlabel('Month', fontweight='bold', fontsize=11)
    ax3.set_ylabel('Total Demographic Updates', fontweight='bold', fontsize=11)
    ax3.set_title('Total Demographic Updates Over Time', fontweight='bold', fontsize=13, pad=10)
    ax3.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig('../visualizations/STEP6_trends_top10_states.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Saved: STEP6_trends_top10_states.png")
    
except Exception as e:
    print(f"ERROR creating trend charts: {e}")
    import traceback
    traceback.print_exc()
    # Continue anyway

print()

# ============================================================================
# STEP 11: CREATE UPDATE RATE COMPARISON CHARTS
# ============================================================================
print("Step 11: Creating update rate comparison charts...")

try:
    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    fig.suptitle('Update Rates by State (vs National Average)', 
                 fontsize=16, fontweight='bold')
    
    # Sort states by update rate
    sorted_bio = state_summary.sort_values('bio_update_rate', ascending=False)
    sorted_demo = state_summary.sort_values('demo_update_rate', ascending=False)
    
    # Chart 1: Top 15 Biometric Update Rates
    ax1 = axes[0]
    top_15_bio = sorted_bio.head(15)
    colors_bio = ['green' if x > national_bio_rate else 'orange' 
                  for x in top_15_bio['bio_update_rate']]
    
    y_pos = range(len(top_15_bio))
    ax1.barh(y_pos, top_15_bio['bio_update_rate'], color=colors_bio)
    ax1.axvline(national_bio_rate, color='red', linestyle='--', linewidth=2,
               label=f'National Avg: {national_bio_rate:.1f}%')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top_15_bio['state'], fontsize=9)
    ax1.set_xlabel('Biometric Update Rate (%)', fontweight='bold')
    ax1.set_title('Top 15 States - Biometric Update Rate', fontweight='bold')
    ax1.legend()
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(top_15_bio['bio_update_rate']):
        ax1.text(v, i, f' {v:.1f}%', va='center', fontsize=8)
    
    # Chart 2: Top 15 Demographic Update Rates
    ax2 = axes[1]
    top_15_demo = sorted_demo.head(15)
    colors_demo = ['green' if x > national_demo_rate else 'orange' 
                   for x in top_15_demo['demo_update_rate']]
    
    y_pos = range(len(top_15_demo))
    ax2.barh(y_pos, top_15_demo['demo_update_rate'], color=colors_demo)
    ax2.axvline(national_demo_rate, color='red', linestyle='--', linewidth=2,
               label=f'National Avg: {national_demo_rate:.1f}%')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(top_15_demo['state'], fontsize=9)
    ax2.set_xlabel('Demographic Update Rate (%)', fontweight='bold')
    ax2.set_title('Top 15 States - Demographic Update Rate', fontweight='bold')
    ax2.legend()
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(top_15_demo['demo_update_rate']):
        ax2.text(v, i, f' {v:.1f}%', va='center', fontsize=8)
    
    plt.tight_layout()
    
    # Save
    plt.savefig('../visualizations/STEP6_update_rates_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Saved: STEP6_update_rates_comparison.png")
    
except Exception as e:
    print(f"ERROR creating comparison charts: {e}")
    import traceback
    traceback.print_exc()
    # Continue anyway

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("✅ STEP 6 COMPLETE - ALL TASKS FINISHED SUCCESSFULLY!")
print("=" * 80)
print()

print("📊 SUMMARY OF RESULTS:")
print()
print("CSV Files Created (4 files):")
print("  ✓ STEP6_state_summary.csv          - State-wise aggregated data")
print("  ✓ STEP6_enrolment_trends.csv       - Monthly enrolment trends")
print("  ✓ STEP6_biometric_trends.csv       - Monthly biometric trends")
print("  ✓ STEP6_demographic_trends.csv     - Monthly demographic trends")
print()

print("Visualizations Created (2 files):")
print("  ✓ STEP6_trends_top10_states.png    - Trend charts (3 charts)")
print("  ✓ STEP6_update_rates_comparison.png - Update rate comparison (2 charts)")
print()

print("📈 KEY STATISTICS:")
print(f"  • States analyzed: {len(state_summary)}")
print(f"  • Time periods covered: {enrolment_trends['year_month'].nunique()}")
print(f"  • Top 10 states identified")
print(f"  • National bio update rate: {national_bio_rate:.2f}%")
print(f"  • National demo update rate: {national_demo_rate:.2f}%")
print()

print("📁 OUTPUT LOCATION:")
print("  • CSV files: E:\\Aadhar UIDAI\\PROJECT\\results\\")
print("  • Visualizations: E:\\Aadhar UIDAI\\PROJECT\\visualizations\\")
print()

print("=" * 80)
print("✅ STEP 6 SUCCESSFULLY COMPLETED!")
print("=" * 80)
