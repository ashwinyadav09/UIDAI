"""
PHASE 3 - STEP 1: State-wise Trend Prediction
==============================================
Forecasts future Aadhaar update demand for effective infrastructure planning

Aligns with problem statement:
- "State-wise trend prediction to forecast future update demand"
- "Predict future update demand for effective infrastructure planning"

Author: UIDAI Hackathon Project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 8)

print("=" * 80)
print("PHASE 3 - STEP 1: STATE-WISE TREND PREDICTION")
print("=" * 80)
print()

# ============================================================================
# STEP 1: LOAD CLEANED DATA
# ============================================================================
print("📂 Loading cleaned data...")
try:
    enrolment = pd.read_csv('../data/processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../data/processed/cleaned_biometric.csv')
    demographic = pd.read_csv('../data/processed/cleaned_demographic.csv')
    print("✓ All datasets loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
    print(f"  - Demographic: {len(demographic):,} rows")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("Please run STEP2_FINAL_intelligent_cleaning.py first!")
    exit()

print()

# ============================================================================
# STEP 2: PREPARE TIME SERIES DATA
# ============================================================================
print("📊 Preparing time series data...")

# Convert dates
for df in [enrolment, biometric, demographic]:
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

# Aggregate by state and date
print("  - Aggregating enrolment data by state and date...")
enrolment_ts = enrolment.groupby(['state', 'date'])['total_enrolments'].sum().reset_index()

print("  - Aggregating biometric update data...")
biometric_ts = biometric.groupby(['state', 'date'])['total_bio_updates'].sum().reset_index()

print("  - Aggregating demographic update data...")
demographic_ts = demographic.groupby(['state', 'date'])['total_demo_updates'].sum().reset_index()

print("✓ Time series data prepared!")
print()

# ============================================================================
# STEP 3: SIMPLE MOVING AVERAGE PREDICTION
# ============================================================================
print("🔮 Generating predictions using Moving Average method...")
print("   (Industry standard for trend forecasting)")
print()

def predict_next_month(ts_data, state_col='state', date_col='date', value_col='value', window=3):
    """
    Predict next month's value using moving average
    
    Parameters:
    - ts_data: Time series dataframe
    - state_col: State column name
    - date_col: Date column name
    - value_col: Value column to predict
    - window: Number of months to average (default=3)
    """
    predictions = []
    
    for state in ts_data[state_col].unique():
        # Get data for this state
        state_data = ts_data[ts_data[state_col] == state].copy()
        state_data = state_data.sort_values(date_col)
        
        # Calculate moving average of last 'window' months
        last_n_values = state_data[value_col].tail(window).values
        
        if len(last_n_values) > 0:
            predicted_value = np.mean(last_n_values)
            
            # Calculate trend (increasing/decreasing)
            if len(last_n_values) >= 2:
                trend = last_n_values[-1] - last_n_values[0]
                trend_pct = (trend / last_n_values[0] * 100) if last_n_values[0] > 0 else 0
            else:
                trend_pct = 0
            
            # Get last date
            last_date = state_data[date_col].max()
            next_month = last_date + timedelta(days=30)
            
            predictions.append({
                'state': state,
                'last_date': last_date,
                'predicted_date': next_month,
                'last_actual': last_n_values[-1],
                'predicted_value': predicted_value,
                'trend_percentage': trend_pct
            })
    
    return pd.DataFrame(predictions)

# Generate predictions
print("🔮 Predicting ENROLMENT for next month...")
enrolment_pred = predict_next_month(enrolment_ts, value_col='total_enrolments')

print("🔮 Predicting BIOMETRIC UPDATES for next month...")
biometric_pred = predict_next_month(biometric_ts, value_col='total_bio_updates')

print("🔮 Predicting DEMOGRAPHIC UPDATES for next month...")
demographic_pred = predict_next_month(demographic_ts, value_col='total_demo_updates')

print("✓ Predictions generated!")
print()

# ============================================================================
# STEP 4: IDENTIFY HIGH-DEMAND STATES
# ============================================================================
print("🚨 Identifying states with HIGH predicted update demand...")
print("   (These states may need additional infrastructure)")
print()

# Calculate national average
bio_avg = biometric_pred['predicted_value'].mean()
demo_avg = demographic_pred['predicted_value'].mean()

print(f"📊 National Average Predictions:")
print(f"   - Biometric Updates: {bio_avg:,.0f}")
print(f"   - Demographic Updates: {demo_avg:,.0f}")
print()

# Identify high-demand states (above 1.5x national average)
high_bio = biometric_pred[biometric_pred['predicted_value'] > bio_avg * 1.5].copy()
high_demo = demographic_pred[demographic_pred['predicted_value'] > demo_avg * 1.5].copy()

print(f"🚨 HIGH-DEMAND STATES (Biometric):")
print(f"   States above 1.5x national average: {len(high_bio)}")
if len(high_bio) > 0:
    print("\nTop 10 states needing infrastructure attention:")
    high_bio_sorted = high_bio.sort_values('predicted_value', ascending=False).head(10)
    for idx, row in high_bio_sorted.iterrows():
        print(f"   {row['state']:40s} → {row['predicted_value']:>10,.0f} updates predicted")
print()

print(f"🚨 HIGH-DEMAND STATES (Demographic):")
print(f"   States above 1.5x national average: {len(high_demo)}")
if len(high_demo) > 0:
    print("\nTop 10 states needing infrastructure attention:")
    high_demo_sorted = high_demo.sort_values('predicted_value', ascending=False).head(10)
    for idx, row in high_demo_sorted.iterrows():
        print(f"   {row['state']:40s} → {row['predicted_value']:>10,.0f} updates predicted")
print()

# ============================================================================
# STEP 5: SAVE PREDICTIONS
# ============================================================================
print("💾 Saving predictions...")

enrolment_pred.to_csv('../results/predictions_enrolment.csv', index=False)
biometric_pred.to_csv('../results/predictions_biometric.csv', index=False)
demographic_pred.to_csv('../results/predictions_demographic.csv', index=False)

# Save high-demand states
high_bio.to_csv('../results/high_demand_states_biometric.csv', index=False)
high_demo.to_csv('../results/high_demand_states_demographic.csv', index=False)

print("✓ Predictions saved to results/ folder")
print()

# ============================================================================
# STEP 6: CREATE VISUALIZATION
# ============================================================================
print("📊 Creating prediction visualizations...")

# Create comparison visualization
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('State-wise Trend Predictions for Next Month', fontsize=16, fontweight='bold')

# 1. Top 15 predicted biometric updates
ax1 = axes[0, 0]
top_bio = biometric_pred.nlargest(15, 'predicted_value')
ax1.barh(range(len(top_bio)), top_bio['predicted_value'], color='steelblue')
ax1.set_yticks(range(len(top_bio)))
ax1.set_yticklabels(top_bio['state'], fontsize=9)
ax1.set_xlabel('Predicted Biometric Updates', fontweight='bold')
ax1.set_title('Top 15 States - Predicted Biometric Update Demand', fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(top_bio['predicted_value']):
    ax1.text(v, i, f' {v:,.0f}', va='center', fontsize=8)

# 2. Top 15 predicted demographic updates
ax2 = axes[0, 1]
top_demo = demographic_pred.nlargest(15, 'predicted_value')
ax2.barh(range(len(top_demo)), top_demo['predicted_value'], color='coral')
ax2.set_yticks(range(len(top_demo)))
ax2.set_yticklabels(top_demo['state'], fontsize=9)
ax2.set_xlabel('Predicted Demographic Updates', fontweight='bold')
ax2.set_title('Top 15 States - Predicted Demographic Update Demand', fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# Add values
for i, v in enumerate(top_demo['predicted_value']):
    ax2.text(v, i, f' {v:,.0f}', va='center', fontsize=8)

# 3. Trend analysis - Biometric
ax3 = axes[1, 0]
trend_bio = biometric_pred.copy()
trend_bio['category'] = trend_bio['trend_percentage'].apply(
    lambda x: 'Increasing' if x > 10 else ('Stable' if x > -10 else 'Decreasing')
)
trend_counts = trend_bio['category'].value_counts()
colors_trend = {'Increasing': 'green', 'Stable': 'orange', 'Decreasing': 'red'}
ax3.bar(trend_counts.index, trend_counts.values, 
        color=[colors_trend[x] for x in trend_counts.index])
ax3.set_ylabel('Number of States', fontweight='bold')
ax3.set_title('Biometric Update Trends Across States', fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(trend_counts.values):
    ax3.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

# 4. Trend analysis - Demographic
ax4 = axes[1, 1]
trend_demo = demographic_pred.copy()
trend_demo['category'] = trend_demo['trend_percentage'].apply(
    lambda x: 'Increasing' if x > 10 else ('Stable' if x > -10 else 'Decreasing')
)
trend_counts_demo = trend_demo['category'].value_counts()
ax4.bar(trend_counts_demo.index, trend_counts_demo.values,
        color=[colors_trend[x] for x in trend_counts_demo.index])
ax4.set_ylabel('Number of States', fontweight='bold')
ax4.set_title('Demographic Update Trends Across States', fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

# Add values
for i, v in enumerate(trend_counts_demo.values):
    ax4.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('../visualizations/PHASE3_01_trend_predictions.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: PHASE3_01_trend_predictions.png")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ PHASE 3 - STEP 1 COMPLETE!")
print("=" * 80)
print()
print("📊 WHAT WAS DONE:")
print("  ✓ Loaded cleaned data")
print("  ✓ Prepared time series by state")
print("  ✓ Generated next-month predictions using moving average")
print("  ✓ Identified high-demand states (>1.5x national average)")
print("  ✓ Analyzed state-wise trends (increasing/stable/decreasing)")
print("  ✓ Created comprehensive visualizations")
print()
print("📁 FILES CREATED:")
print("  ✓ results/predictions_enrolment.csv")
print("  ✓ results/predictions_biometric.csv")
print("  ✓ results/predictions_demographic.csv")
print("  ✓ results/high_demand_states_biometric.csv")
print("  ✓ results/high_demand_states_demographic.csv")
print("  ✓ visualizations/PHASE3_01_trend_predictions.png")
print()
print("🎯 KEY INSIGHTS:")
print(f"  - {len(high_bio)} states have HIGH biometric update demand")
print(f"  - {len(high_demo)} states have HIGH demographic update demand")
print(f"  - {trend_counts.get('Increasing', 0)} states show increasing bio trends")
print(f"  - {trend_counts.get('Decreasing', 0)} states show decreasing bio trends")
print()
print("Next: Run PHASE3_STEP2_child_enrolment_gap.py")
print("=" * 80)
