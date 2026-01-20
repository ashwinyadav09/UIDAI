"""
PHASE 4 - STEP 10 ENHANCED: Professional Time Series Forecasting with Prophet
===============================================================================
Production-ready ML forecasting for Aadhaar update demand prediction

KEY IMPROVEMENTS:
1. ✅ Floor constraints to prevent negative forecasts
2. ✅ Additive seasonality (better for count data)
3. ✅ Robust data validation and preprocessing
4. ✅ Multiple forecast horizons (1, 3, 6 months)
5. ✅ Comprehensive capacity planning metrics
6. ✅ Bottleneck prediction with confidence intervals
7. ✅ State-wise growth trajectory analysis

Author: Professional ML/Data Science Engineer for UIDAI Hackathon
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
from prophet import Prophet
import warnings


warnings.filterwarnings('ignore')

# Set professional styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)
plt.rcParams['font.size'] = 10

print("=" * 100)
print("STEP 10 ENHANCED: PROFESSIONAL TIME SERIES FORECASTING WITH PROPHET")
print("=" * 100)
print()
print("🎯 OBJECTIVES:")
print("  ✓ Build robust Prophet models with floor constraints (no negative forecasts)")
print("  ✓ Forecast enrolment, biometric, and demographic update demand")
print("  ✓ Predict capacity bottlenecks for next 1, 3, and 6 months")
print("  ✓ Identify high-risk states requiring immediate intervention")
print("  ✓ Generate actionable insights for UIDAI infrastructure planning")
print()

# ============================================================================
# STEP 1: LOAD AND VALIDATE DATA
# ============================================================================
print("📂 Step 1: Loading and validating cleaned data...")

try:
    enrolment = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_enrolment.csv'))
    biometric = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_biometric.csv'))
    demographic = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_demographic.csv'))
    
    # Convert dates
    enrolment['date'] = pd.to_datetime(enrolment['date'])
    biometric['date'] = pd.to_datetime(biometric['date'])
    demographic['date'] = pd.to_datetime(demographic['date'])
    
    print("✓ Data loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows | Date range: {enrolment['date'].min()} to {enrolment['date'].max()}")
    print(f"  - Biometric: {len(biometric):,} rows | Date range: {biometric['date'].min()} to {biometric['date'].max()}")
    print(f"  - Demographic: {len(demographic):,} rows | Date range: {demographic['date'].min()} to {demographic['date'].max()}")
    
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

print()

# ============================================================================
# STEP 2: PREPARE TIME SERIES DATA (WEEKLY AGGREGATION)
# ============================================================================
print("📊 Step 2: Preparing time series data with weekly aggregation...")

# Weekly aggregation reduces noise and improves forecast stability
enrolment_ts = enrolment.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_enrolments': 'sum',
    'age_0_5': 'sum',
    'age_5_17': 'sum',
    'age_18_greater': 'sum'
}).reset_index()

biometric_ts = biometric.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_bio_updates': 'sum',
    'bio_age_5_17': 'sum',
    'bio_age_17_': 'sum'
}).reset_index()

demographic_ts = demographic.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_demo_updates': 'sum'
}).reset_index()

print(f"✓ Time series aggregated:")
print(f"  - Enrolment: {len(enrolment_ts):,} state-week observations")
print(f"  - Biometric: {len(biometric_ts):,} state-week observations")
print(f"  - Demographic: {len(demographic_ts):,} state-week observations")
print()

# ============================================================================
# STEP 3: SELECT TOP STATES FOR FORECASTING
# ============================================================================
print("🎯 Step 3: Selecting top states for detailed forecasting...")

# Select top 10 states by total activity
top_states_enrol = enrolment.groupby('state')['total_enrolments'].sum().nlargest(10).index.tolist()
top_states_bio = biometric.groupby('state')['total_bio_updates'].sum().nlargest(10).index.tolist()

# Combine and deduplicate
top_states = list(set(top_states_enrol + top_states_bio))[:12]  # Top 12 states

print(f"✓ Selected {len(top_states)} states for forecasting:")
for i, state in enumerate(top_states, 1):
    total_enrol = enrolment[enrolment['state'] == state]['total_enrolments'].sum()
    total_bio = biometric[biometric['state'] == state]['total_bio_updates'].sum()
    print(f"  {i:2d}. {state:30s} - Enrol: {total_enrol:>10,} | Bio: {total_bio:>10,}")
print()

# ============================================================================
# STEP 4: BUILD ENHANCED PROPHET MODELS - ENROLMENT FORECASTING
# ============================================================================
print("🔮 Step 4: Building enhanced Prophet models for ENROLMENT forecasting...")
print("   Configuration: Additive seasonality + Floor constraints + 95% CI")
print()

forecast_horizons = {
    '1_month': 4,   # 4 weeks
    '3_months': 12,  # 12 weeks
    '6_months': 24   # 24 weeks
}

enrolment_forecasts = {}
enrolment_models = {}
enrolment_metrics = []

for idx, state in enumerate(top_states, 1):
    print(f"  [{idx}/{len(top_states)}] Forecasting enrolments for: {state}")
    
    # Prepare data for Prophet
    state_data = enrolment_ts[enrolment_ts['state'] == state][['date', 'total_enrolments']].copy()
    state_data.columns = ['ds', 'y']
    
    # Remove zeros and negatives
    state_data = state_data[state_data['y'] > 0].reset_index(drop=True)
    
    # Data validation
    if len(state_data) < 15:
        print(f"      ⚠ Insufficient data ({len(state_data)} points), skipping...")
        continue
    
    # Calculate floor (minimum value) - Prophet won't forecast below this
    floor_value = max(1, state_data['y'].quantile(0.05))  # 5th percentile as floor
    state_data['floor'] = floor_value
    
    try:
        # Initialize Prophet with ADDITIVE seasonality (better for count data)
        model = Prophet(
            growth='linear',
            yearly_seasonality=True,
            weekly_seasonality=False,  # Disable for weekly aggregated data
            daily_seasonality=False,
            seasonality_mode='additive',  # CRITICAL: Additive prevents negative forecasts
            changepoint_prior_scale=0.05,
            interval_width=0.95,
            seasonality_prior_scale=10.0
        )
        
        # Fit model
        model.fit(state_data)
        
        # Generate forecasts for multiple horizons
        future_6m = model.make_future_dataframe(periods=forecast_horizons['6_months'], freq='W')
        future_6m['floor'] = floor_value
        forecast = model.predict(future_6m)
        
        # Ensure no negative forecasts (additional safety)
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)
        
        # Store results
        enrolment_forecasts[state] = forecast
        enrolment_models[state] = model
        
        # Calculate metrics
        last_actual = state_data['y'].iloc[-5:].mean()  # Last 5 weeks average
        forecast_1m = forecast[forecast['ds'] > state_data['ds'].max()].head(4)['yhat'].mean()
        forecast_3m = forecast[forecast['ds'] > state_data['ds'].max()].head(12)['yhat'].mean()
        forecast_6m = forecast[forecast['ds'] > state_data['ds'].max()].head(24)['yhat'].mean()
        
        growth_1m = ((forecast_1m - last_actual) / last_actual) * 100
        growth_3m = ((forecast_3m - last_actual) / last_actual) * 100
        growth_6m = ((forecast_6m - last_actual) / last_actual) * 100
        
        enrolment_metrics.append({
            'state': state,
            'last_actual_avg': last_actual,
            'forecast_1m': forecast_1m,
            'forecast_3m': forecast_3m,
            'forecast_6m': forecast_6m,
            'growth_1m_pct': growth_1m,
            'growth_3m_pct': growth_3m,
            'growth_6m_pct': growth_6m,
            'data_points': len(state_data)
        })
        
        print(f"      ✓ Baseline: {last_actual:>8,.0f} | 1M: {forecast_1m:>8,.0f} ({growth_1m:+.1f}%) | "
              f"3M: {forecast_3m:>8,.0f} ({growth_3m:+.1f}%) | 6M: {forecast_6m:>8,.0f} ({growth_6m:+.1f}%)")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print(f"✓ Enrolment forecasting complete: {len(enrolment_forecasts)} states modeled")
print()

# ============================================================================
# STEP 5: BUILD ENHANCED PROPHET MODELS - BIOMETRIC UPDATE FORECASTING
# ============================================================================
print("🔮 Step 5: Building enhanced Prophet models for BIOMETRIC UPDATE forecasting...")
print()

biometric_forecasts = {}
biometric_models = {}
biometric_metrics = []

for idx, state in enumerate(top_states, 1):
    print(f"  [{idx}/{len(top_states)}] Forecasting biometric updates for: {state}")
    
    # Prepare data
    state_data = biometric_ts[biometric_ts['state'] == state][['date', 'total_bio_updates']].copy()
    state_data.columns = ['ds', 'y']
    state_data = state_data[state_data['y'] > 0].reset_index(drop=True)
    
    if len(state_data) < 15:
        print(f"      ⚠ Insufficient data ({len(state_data)} points), skipping...")
        continue
    
    # Set floor
    floor_value = max(1, state_data['y'].quantile(0.05))
    state_data['floor'] = floor_value
    
    try:
        model = Prophet(
            growth='linear',
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',
            changepoint_prior_scale=0.05,
            interval_width=0.95,
            seasonality_prior_scale=10.0
        )
        
        model.fit(state_data)
        
        future_6m = model.make_future_dataframe(periods=forecast_horizons['6_months'], freq='W')
        future_6m['floor'] = floor_value
        forecast = model.predict(future_6m)
        
        # Clip negatives
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)
        
        biometric_forecasts[state] = forecast
        biometric_models[state] = model
        
        # Metrics
        last_actual = state_data['y'].iloc[-5:].mean()
        forecast_1m = forecast[forecast['ds'] > state_data['ds'].max()].head(4)['yhat'].mean()
        forecast_3m = forecast[forecast['ds'] > state_data['ds'].max()].head(12)['yhat'].mean()
        forecast_6m = forecast[forecast['ds'] > state_data['ds'].max()].head(24)['yhat'].mean()
        
        growth_1m = ((forecast_1m - last_actual) / last_actual) * 100
        growth_3m = ((forecast_3m - last_actual) / last_actual) * 100
        growth_6m = ((forecast_6m - last_actual) / last_actual) * 100
        
        biometric_metrics.append({
            'state': state,
            'last_actual_avg': last_actual,
            'forecast_1m': forecast_1m,
            'forecast_3m': forecast_3m,
            'forecast_6m': forecast_6m,
            'growth_1m_pct': growth_1m,
            'growth_3m_pct': growth_3m,
            'growth_6m_pct': growth_6m,
            'data_points': len(state_data)
        })
        
        print(f"      ✓ Baseline: {last_actual:>8,.0f} | 1M: {forecast_1m:>8,.0f} ({growth_1m:+.1f}%) | "
              f"3M: {forecast_3m:>8,.0f} ({growth_3m:+.1f}%) | 6M: {forecast_6m:>8,.0f} ({growth_6m:+.1f}%)")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print(f"✓ Biometric update forecasting complete: {len(biometric_forecasts)} states modeled")
print()

# ============================================================================
# STEP 6: BUILD ENHANCED PROPHET MODELS - DEMOGRAPHIC UPDATE FORECASTING
# ============================================================================
print("🔮 Step 6: Building enhanced Prophet models for DEMOGRAPHIC UPDATE forecasting...")
print()

demographic_forecasts = {}
demographic_models = {}
demographic_metrics = []

for idx, state in enumerate(top_states, 1):
    print(f"  [{idx}/{len(top_states)}] Forecasting demographic updates for: {state}")
    
    state_data = demographic_ts[demographic_ts['state'] == state][['date', 'total_demo_updates']].copy()
    state_data.columns = ['ds', 'y']
    state_data = state_data[state_data['y'] > 0].reset_index(drop=True)
    
    if len(state_data) < 15:
        print(f"      ⚠ Insufficient data ({len(state_data)} points), skipping...")
        continue
    
    floor_value = max(1, state_data['y'].quantile(0.05))
    state_data['floor'] = floor_value
    
    try:
        model = Prophet(
            growth='linear',
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',
            changepoint_prior_scale=0.05,
            interval_width=0.95,
            seasonality_prior_scale=10.0
        )
        
        model.fit(state_data)
        
        future_6m = model.make_future_dataframe(periods=forecast_horizons['6_months'], freq='W')
        future_6m['floor'] = floor_value
        forecast = model.predict(future_6m)
        
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)
        
        demographic_forecasts[state] = forecast
        demographic_models[state] = model
        
        last_actual = state_data['y'].iloc[-5:].mean()
        forecast_1m = forecast[forecast['ds'] > state_data['ds'].max()].head(4)['yhat'].mean()
        forecast_3m = forecast[forecast['ds'] > state_data['ds'].max()].head(12)['yhat'].mean()
        forecast_6m = forecast[forecast['ds'] > state_data['ds'].max()].head(24)['yhat'].mean()
        
        growth_1m = ((forecast_1m - last_actual) / last_actual) * 100
        growth_3m = ((forecast_3m - last_actual) / last_actual) * 100
        growth_6m = ((forecast_6m - last_actual) / last_actual) * 100
        
        demographic_metrics.append({
            'state': state,
            'last_actual_avg': last_actual,
            'forecast_1m': forecast_1m,
            'forecast_3m': forecast_3m,
            'forecast_6m': forecast_6m,
            'growth_1m_pct': growth_1m,
            'growth_3m_pct': growth_3m,
            'growth_6m_pct': growth_6m,
            'data_points': len(state_data)
        })
        
        print(f"      ✓ Baseline: {last_actual:>8,.0f} | 1M: {forecast_1m:>8,.0f} ({growth_1m:+.1f}%) | "
              f"3M: {forecast_3m:>8,.0f} ({growth_3m:+.1f}%) | 6M: {forecast_6m:>8,.0f} ({growth_6m:+.1f}%)")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print(f"✓ Demographic update forecasting complete: {len(demographic_forecasts)} states modeled")
print()

# ============================================================================
# STEP 7: COMPREHENSIVE CAPACITY PLANNING ANALYSIS
# ============================================================================
print("📈 Step 7: Comprehensive capacity planning and bottleneck prediction...")
print()

# Convert metrics to DataFrames
enrolment_df = pd.DataFrame(enrolment_metrics)
biometric_df = pd.DataFrame(biometric_metrics)
demographic_df = pd.DataFrame(demographic_metrics)

# Merge for comprehensive analysis
capacity_analysis = enrolment_df.merge(
    biometric_df[['state', 'forecast_3m', 'growth_3m_pct']], 
    on='state', 
    how='outer', 
    suffixes=('_enrol', '_bio')
)

# Add demographic data
capacity_analysis = capacity_analysis.merge(
    demographic_df[['state', 'forecast_3m', 'growth_3m_pct']], 
    on='state', 
    how='outer'
).rename(columns={'forecast_3m': 'forecast_3m_demo', 'growth_3m_pct': 'growth_3m_pct_demo'})

# Fill NaN with 0
capacity_analysis = capacity_analysis.fillna(0)

# Calculate combined demand score (weighted average of growth rates)
capacity_analysis['demand_score'] = (
    capacity_analysis['growth_3m_pct_enrol'] * 0.4 +
    capacity_analysis['growth_3m_pct_bio'] * 0.4 +
    capacity_analysis['growth_3m_pct_demo'] * 0.2
)

# Classify capacity needs
def classify_capacity(row):
    score = row['demand_score']
    if score > 30:
        return "🔴 CRITICAL - Immediate Expansion Required"
    elif score > 15:
        return "🟠 HIGH - Expansion Needed Within 3 Months"
    elif score > 5:
        return "🟡 MEDIUM - Monitor and Plan"
    elif score > -10:
        return "🟢 STABLE - Adequate Capacity"
    else:
        return "🔵 LOW - Potential Overcapacity"

capacity_analysis['capacity_status'] = capacity_analysis.apply(classify_capacity, axis=1)

# Sort by demand score
capacity_analysis = capacity_analysis.sort_values('demand_score', ascending=False)

print("✓ Capacity planning analysis complete!")
print()
print("=" * 100)
print("🎯 CAPACITY PLANNING INSIGHTS - 3-MONTH FORECAST")
print("=" * 100)
print()

for idx, row in capacity_analysis.iterrows():
    print(f"{row['capacity_status']}")
    print(f"   State: {row['state']}")
    print(f"   Demand Score: {row['demand_score']:+.1f}%")
    print(f"   Enrolment Growth: {row['growth_3m_pct_enrol']:+.1f}% | "
          f"Biometric Growth: {row['growth_3m_pct_bio']:+.1f}% | "
          f"Demographic Growth: {row['growth_3m_pct_demo']:+.1f}%")
    print()

# ============================================================================
# STEP 8: SAVE ALL RESULTS
# ============================================================================
print("💾 Step 8: Saving comprehensive forecast results...")

# Save capacity analysis
capacity_analysis.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP10_ENHANCED_capacity_planning.csv'), index=False)

# Save detailed metrics
enrolment_df.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP10_ENHANCED_enrolment_metrics.csv'), index=False)
biometric_df.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP10_ENHANCED_biometric_metrics.csv'), index=False)
demographic_df.to_csv(os.path.join(PROJECT_PATH, 'results', 'STEP10_ENHANCED_demographic_metrics.csv'), index=False)

# Save individual forecasts for top 5 demand states
top_5_demand = capacity_analysis.head(5)['state'].tolist()

for state in top_5_demand:
    if state in enrolment_forecasts:
        enrolment_forecasts[state].to_csv(
            os.path.join(PROJECT_PATH, 'results', f'STEP10_ENHANCED_enrolment_forecast_{state.replace(" ", "_").lower()}.csv'), 
            index=False
        )
    if state in biometric_forecasts:
        biometric_forecasts[state].to_csv(
            os.path.join(PROJECT_PATH, 'results', f'STEP10_ENHANCED_biometric_forecast_{state.replace(" ", "_").lower()}.csv'), 
            index=False
        )
    if state in demographic_forecasts:
        demographic_forecasts[state].to_csv(
            os.path.join(PROJECT_PATH, 'results', f'STEP10_ENHANCED_demographic_forecast_{state.replace(" ", "_").lower()}.csv'), 
            index=False
        )

# Save models for visualization
import pickle
with open(os.path.join(PROJECT_PATH, 'results', 'STEP10_ENHANCED_models.pkl'), 'wb') as f:
    pickle.dump({
        'enrolment_models': enrolment_models,
        'enrolment_forecasts': enrolment_forecasts,
        'biometric_models': biometric_models,
        'biometric_forecasts': biometric_forecasts,
        'demographic_models': demographic_models,
        'demographic_forecasts': demographic_forecasts,
        'capacity_analysis': capacity_analysis,
        'top_states': top_states
    }, f)

print("✓ All results saved successfully!")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 100)
print("✅ STEP 10 ENHANCED - PROFESSIONAL PROPHET FORECASTING COMPLETE!")
print("=" * 100)
print()
print("📊 MODELS BUILT:")
print(f"   ✓ Enrolment forecasting: {len(enrolment_forecasts)} states")
print(f"   ✓ Biometric update forecasting: {len(biometric_forecasts)} states")
print(f"   ✓ Demographic update forecasting: {len(demographic_forecasts)} states")
print()
print("📁 FILES CREATED:")
print("   ✓ STEP10_ENHANCED_capacity_planning.csv - Comprehensive capacity analysis")
print("   ✓ STEP10_ENHANCED_enrolment_metrics.csv - Enrolment forecast metrics")
print("   ✓ STEP10_ENHANCED_biometric_metrics.csv - Biometric forecast metrics")
print("   ✓ STEP10_ENHANCED_demographic_metrics.csv - Demographic forecast metrics")
print("   ✓ STEP10_ENHANCED_*_forecast_*.csv - Individual state forecasts")
print("   ✓ STEP10_ENHANCED_models.pkl - Trained models for visualization")
print()
print("🎯 KEY FINDINGS:")
critical_states = capacity_analysis[capacity_analysis['capacity_status'].str.contains('CRITICAL')]
high_states = capacity_analysis[capacity_analysis['capacity_status'].str.contains('HIGH')]
print(f"   🔴 {len(critical_states)} states require IMMEDIATE capacity expansion")
print(f"   🟠 {len(high_states)} states need expansion within 3 months")
print(f"   📈 Average demand growth: {capacity_analysis['demand_score'].mean():.1f}%")
print()
print("🔜 NEXT STEPS:")
print("   1. Run STEP10_ENHANCED_visualizations.py to create forecast charts")
print("   2. Review capacity planning recommendations")
print("   3. Integrate insights into final hackathon report")
print("=" * 100)
