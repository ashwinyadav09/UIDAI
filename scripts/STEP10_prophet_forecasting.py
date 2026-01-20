"""
PHASE 3 - STEP 10: Time Series Forecasting with Facebook Prophet
==================================================================
Professional ML-based forecasting for Aadhaar update demand prediction

Implements:
1. State-wise Prophet models for enrolment forecasting
2. State-wise Prophet models for biometric update forecasting
3. State-wise Prophet models for demographic update forecasting
4. Capacity planning insights and bottleneck prediction
5. Seasonal decomposition and trend analysis

Author: Professional ML/Data Science Engineer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 10)

print("=" * 100)
print("PHASE 3 - STEP 10: TIME SERIES FORECASTING WITH FACEBOOK PROPHET")
print("=" * 100)
print()
print("🔮 Forecasting Objectives:")
print("  1. Predict future Aadhaar enrolment demand by state")
print("  2. Predict future biometric update demand by state")
print("  3. Predict future demographic update demand by state")
print("  4. Identify states requiring capacity expansion")
print("  5. Provide 3-6 month forecasts for resource planning")
print()

# ============================================================================
# LOAD CLEANED DATA
# ============================================================================
print("📂 Step 10.1: Loading cleaned data...")
try:
    enrolment = pd.read_csv('../processed/cleaned_enrolment.csv')
    biometric = pd.read_csv('../processed/cleaned_biometric.csv')
    demographic = pd.read_csv('../processed/cleaned_demographic.csv')
    
    # Convert dates
    enrolment['date'] = pd.to_datetime(enrolment['date'])
    biometric['date'] = pd.to_datetime(biometric['date'])
    demographic['date'] = pd.to_datetime(demographic['date'])
    
    print("✓ Data loaded successfully!")
    print(f"  - Enrolment: {len(enrolment):,} rows")
    print(f"  - Biometric: {len(biometric):,} rows")
    print(f"  - Demographic: {len(demographic):,} rows")
    print(f"  - Date range: {enrolment['date'].min()} to {enrolment['date'].max()}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

print()

# ============================================================================
# PREPARE TIME SERIES DATA
# ============================================================================
print("📊 Step 10.2: Preparing time series data...")

# Aggregate daily data to weekly level for better forecasting
# (Daily data can be too noisy for Prophet)

# Enrolment time series by state (weekly)
enrolment_ts = enrolment.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_enrolments': 'sum',
    'age_0_5': 'sum',
    'age_5_17': 'sum',
    'age_18_greater': 'sum'
}).reset_index()

# Biometric update time series by state (weekly)
biometric_ts = biometric.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_bio_updates': 'sum',
    'bio_age_5_17': 'sum',
    'bio_age_17_': 'sum'
}).reset_index()

# Demographic update time series by state (weekly)
demographic_ts = demographic.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_demo_updates': 'sum'
}).reset_index()

print(f"✓ Time series prepared:")
print(f"  - Enrolment: {len(enrolment_ts):,} state-week combinations")
print(f"  - Biometric: {len(biometric_ts):,} state-week combinations")
print(f"  - Demographic: {len(demographic_ts):,} state-week combinations")
print()

# ============================================================================
# SELECT TOP STATES FOR FORECASTING
# ============================================================================
print("🎯 Step 10.3: Selecting top states for forecasting...")

# Get top 10 states by total activity
top_states_enrol = enrolment.groupby('state')['total_enrolments'].sum().nlargest(10).index.tolist()
top_states_bio = biometric.groupby('state')['total_bio_updates'].sum().nlargest(10).index.tolist()

# Combine and get unique top states
top_states = list(set(top_states_enrol + top_states_bio))[:15]  # Top 15 states

print(f"✓ Selected {len(top_states)} states for detailed forecasting:")
for i, state in enumerate(top_states, 1):
    total_enrol = enrolment[enrolment['state'] == state]['total_enrolments'].sum()
    print(f"  {i:2d}. {state:40s} - {total_enrol:,} total enrolments")
print()

# ============================================================================
# STEP 10.4: BUILD PROPHET MODELS FOR ENROLMENT FORECASTING
# ============================================================================
print("🔮 Step 10.4: Building Prophet models for enrolment forecasting...")
print("   This may take a few minutes...")
print()

forecast_horizon = 12  # 12 weeks (3 months) ahead
enrolment_forecasts = {}
enrolment_models = {}

for idx, state in enumerate(top_states, 1):
    print(f"  [{idx}/{len(top_states)}] Forecasting enrolments for: {state}")
    
    # Prepare data for Prophet (requires 'ds' and 'y' columns)
    state_data = enrolment_ts[enrolment_ts['state'] == state][['date', 'total_enrolments']].copy()
    state_data.columns = ['ds', 'y']
    
    # Remove any rows with zero or negative values
    state_data = state_data[state_data['y'] > 0]
    
    if len(state_data) < 10:  # Need minimum data points
        print(f"      ⚠ Insufficient data ({len(state_data)} points), skipping...")
        continue
    
    try:
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05,  # Flexibility in trend changes
            interval_width=0.95  # 95% confidence intervals
        )
        
        # Fit model
        model.fit(state_data)
        
        # Make future dataframe
        future = model.make_future_dataframe(periods=forecast_horizon, freq='W')
        
        # Predict
        forecast = model.predict(future)
        
        # Store results
        enrolment_forecasts[state] = forecast
        enrolment_models[state] = model
        
        # Get forecast summary
        last_actual = state_data['y'].iloc[-1]
        avg_forecast = forecast[forecast['ds'] > state_data['ds'].max()]['yhat'].mean()
        change_pct = ((avg_forecast - last_actual) / last_actual) * 100
        
        print(f"      ✓ Last actual: {last_actual:,.0f} | Avg forecast: {avg_forecast:,.0f} | Change: {change_pct:+.1f}%")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print(f"✓ Enrolment forecasting complete: {len(enrolment_forecasts)} states modeled")
print()

# ============================================================================
# STEP 10.5: BUILD PROPHET MODELS FOR BIOMETRIC UPDATE FORECASTING
# ============================================================================
print("🔮 Step 10.5: Building Prophet models for biometric update forecasting...")
print()

biometric_forecasts = {}
biometric_models = {}

for idx, state in enumerate(top_states, 1):
    print(f"  [{idx}/{len(top_states)}] Forecasting biometric updates for: {state}")
    
    # Prepare data for Prophet
    state_data = biometric_ts[biometric_ts['state'] == state][['date', 'total_bio_updates']].copy()
    state_data.columns = ['ds', 'y']
    
    # Remove any rows with zero or negative values
    state_data = state_data[state_data['y'] > 0]
    
    if len(state_data) < 10:
        print(f"      ⚠ Insufficient data ({len(state_data)} points), skipping...")
        continue
    
    try:
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05,
            interval_width=0.95
        )
        
        # Fit model
        model.fit(state_data)
        
        # Make future dataframe
        future = model.make_future_dataframe(periods=forecast_horizon, freq='W')
        
        # Predict
        forecast = model.predict(future)
        
        # Store results
        biometric_forecasts[state] = forecast
        biometric_models[state] = model
        
        # Get forecast summary
        last_actual = state_data['y'].iloc[-1]
        avg_forecast = forecast[forecast['ds'] > state_data['ds'].max()]['yhat'].mean()
        change_pct = ((avg_forecast - last_actual) / last_actual) * 100
        
        print(f"      ✓ Last actual: {last_actual:,.0f} | Avg forecast: {avg_forecast:,.0f} | Change: {change_pct:+.1f}%")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print(f"✓ Biometric update forecasting complete: {len(biometric_forecasts)} states modeled")
print()

# ============================================================================
# STEP 10.6: BUILD PROPHET MODELS FOR DEMOGRAPHIC UPDATE FORECASTING
# ============================================================================
print("🔮 Step 10.6: Building Prophet models for demographic update forecasting...")
print()

demographic_forecasts = {}
demographic_models = {}

for idx, state in enumerate(top_states, 1):
    print(f"  [{idx}/{len(top_states)}] Forecasting demographic updates for: {state}")
    
    # Prepare data for Prophet
    state_data = demographic_ts[demographic_ts['state'] == state][['date', 'total_demo_updates']].copy()
    state_data.columns = ['ds', 'y']
    
    # Remove any rows with zero or negative values
    state_data = state_data[state_data['y'] > 0]
    
    if len(state_data) < 10:
        print(f"      ⚠ Insufficient data ({len(state_data)} points), skipping...")
        continue
    
    try:
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05,
            interval_width=0.95
        )
        
        # Fit model
        model.fit(state_data)
        
        # Make future dataframe
        future = model.make_future_dataframe(periods=forecast_horizon, freq='W')
        
        # Predict
        forecast = model.predict(future)
        
        # Store results
        demographic_forecasts[state] = forecast
        demographic_models[state] = model
        
        # Get forecast summary
        last_actual = state_data['y'].iloc[-1]
        avg_forecast = forecast[forecast['ds'] > state_data['ds'].max()]['yhat'].mean()
        change_pct = ((avg_forecast - last_actual) / last_actual) * 100
        
        print(f"      ✓ Last actual: {last_actual:,.0f} | Avg forecast: {avg_forecast:,.0f} | Change: {change_pct:+.1f}%")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print(f"✓ Demographic update forecasting complete: {len(demographic_forecasts)} states modeled")
print()

# ============================================================================
# STEP 10.7: CAPACITY PLANNING ANALYSIS
# ============================================================================
print("📈 Step 10.7: Analyzing capacity planning needs...")
print()

capacity_analysis = []

for state in top_states:
    if state not in enrolment_forecasts or state not in biometric_forecasts:
        continue
    
    # Get forecast data
    enrol_forecast = enrolment_forecasts[state]
    bio_forecast = biometric_forecasts[state]
    
    # Get future predictions only
    enrol_future = enrol_forecast[enrol_forecast['ds'] > enrol_forecast['ds'].max() - pd.Timedelta(weeks=forecast_horizon)]
    bio_future = bio_forecast[bio_forecast['ds'] > bio_forecast['ds'].max() - pd.Timedelta(weeks=forecast_horizon)]
    
    # Calculate metrics
    enrol_avg_forecast = enrol_future['yhat'].mean()
    bio_avg_forecast = bio_future['yhat'].mean()
    
    # Get historical averages
    state_enrol_hist = enrolment_ts[enrolment_ts['state'] == state]['total_enrolments'].mean()
    state_bio_hist = biometric_ts[biometric_ts['state'] == state]['total_bio_updates'].mean()
    
    # Calculate growth rates
    enrol_growth = ((enrol_avg_forecast - state_enrol_hist) / state_enrol_hist) * 100
    bio_growth = ((bio_avg_forecast - state_bio_hist) / state_bio_hist) * 100
    
    # Determine capacity need
    if enrol_growth > 20 or bio_growth > 20:
        capacity_need = "HIGH - Expansion Required"
    elif enrol_growth > 10 or bio_growth > 10:
        capacity_need = "MEDIUM - Monitor Closely"
    elif enrol_growth < -10 or bio_growth < -10:
        capacity_need = "LOW - Potential Overcapacity"
    else:
        capacity_need = "STABLE - No Action Needed"
    
    capacity_analysis.append({
        'state': state,
        'enrol_forecast_avg': enrol_avg_forecast,
        'bio_forecast_avg': bio_avg_forecast,
        'enrol_growth_pct': enrol_growth,
        'bio_growth_pct': bio_growth,
        'capacity_need': capacity_need
    })

capacity_df = pd.DataFrame(capacity_analysis)

print("✓ Capacity planning analysis complete")
print()
print("🎯 States Requiring Capacity Expansion (>20% growth):")
high_capacity = capacity_df[capacity_df['capacity_need'].str.contains('HIGH')]
if len(high_capacity) > 0:
    for idx, row in high_capacity.iterrows():
        print(f"  • {row['state']:40s} - Enrol: {row['enrol_growth_pct']:+.1f}% | Bio: {row['bio_growth_pct']:+.1f}%")
else:
    print("  None identified")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("💾 Step 10.8: Saving forecast results...")

# Save capacity analysis
capacity_df.to_csv('../results/STEP10_capacity_planning_analysis.csv', index=False)

# Save individual forecasts for top 5 states
top_5_states = capacity_df.nlargest(5, 'enrol_growth_pct')['state'].tolist()

for state in top_5_states:
    if state in enrolment_forecasts:
        enrolment_forecasts[state].to_csv(f'../results/STEP10_enrolment_forecast_{state.replace(" ", "_")}.csv', index=False)
    if state in biometric_forecasts:
        biometric_forecasts[state].to_csv(f'../results/STEP10_biometric_forecast_{state.replace(" ", "_")}.csv', index=False)
    if state in demographic_forecasts:
        demographic_forecasts[state].to_csv(f'../results/STEP10_demographic_forecast_{state.replace(" ", "_")}.csv', index=False)

print("✓ Results saved:")
print("  - STEP10_capacity_planning_analysis.csv")
print(f"  - Individual forecast files for top 5 states")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 100)
print("✅ STEP 10 COMPLETE - TIME SERIES FORECASTING WITH PROPHET!")
print("=" * 100)
print()
print("📋 WHAT WAS DONE:")
print(f"  ✓ Built Prophet models for {len(enrolment_forecasts)} states (enrolment)")
print(f"  ✓ Built Prophet models for {len(biometric_forecasts)} states (biometric updates)")
print(f"  ✓ Built Prophet models for {len(demographic_forecasts)} states (demographic updates)")
print(f"  ✓ Generated {forecast_horizon}-week forecasts for each state")
print("  ✓ Analyzed capacity planning needs")
print("  ✓ Identified states requiring expansion")
print()
print("📁 FILES CREATED:")
print("  ✓ results/STEP10_capacity_planning_analysis.csv")
print(f"  ✓ results/STEP10_*_forecast_*.csv (individual forecasts)")
print()
print("📊 KEY INSIGHTS:")
print(f"  - {len(high_capacity)} states require HIGH capacity expansion")
print(f"  - {len(capacity_df[capacity_df['capacity_need'].str.contains('MEDIUM')])} states need monitoring")
print(f"  - Forecast horizon: {forecast_horizon} weeks (3 months)")
print()
print("🔜 NEXT: Run STEP10_generate_visualizations.py to create forecast charts")
print("=" * 100)

# Store models and forecasts for visualization script
import pickle

with open('../results/STEP10_models_and_forecasts.pkl', 'wb') as f:
    pickle.dump({
        'enrolment_models': enrolment_models,
        'enrolment_forecasts': enrolment_forecasts,
        'biometric_models': biometric_models,
        'biometric_forecasts': biometric_forecasts,
        'demographic_models': demographic_models,
        'demographic_forecasts': demographic_forecasts,
        'top_states': top_states,
        'capacity_df': capacity_df
    }, f)

print("✓ Models and forecasts saved for visualization")
print()
