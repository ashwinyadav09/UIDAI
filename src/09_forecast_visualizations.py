"""
STEP 10 ENHANCED VISUALIZATIONS: Professional Prophet Forecast Charts
========================================================================
Create publication-quality visualizations for UIDAI Hackathon submission

Visualizations:
1. Multi-state forecast comparison dashboard
2. Individual state forecast with confidence intervals
3. Capacity planning heatmap
4. Growth trajectory analysis
5. Bottleneck prediction timeline

Author: Professional ML/Data Science Engineer
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
import pickle
from matplotlib.gridspec import GridSpec
import warnings


warnings.filterwarnings('ignore')

# Professional styling
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

print("=" * 100)
print("STEP 10 ENHANCED: CREATING PROFESSIONAL FORECAST VISUALIZATIONS")
print("=" * 100)
print()

# ============================================================================
# LOAD MODELS AND DATA
# ============================================================================
print("📂 Loading forecast models and results...")

with open(os.path.join(PROJECT_PATH, 'results', 'STEP10_ENHANCED_models.pkl'), 'rb') as f:
    data = pickle.load(f)
    enrolment_models = data['enrolment_models']
    enrolment_forecasts = data['enrolment_forecasts']
    biometric_models = data['biometric_models']
    biometric_forecasts = data['biometric_forecasts']
    demographic_models = data['demographic_models']
    demographic_forecasts = data['demographic_forecasts']
    capacity_analysis = data['capacity_analysis']
    top_states = data['top_states']

# Load cleaned data for actuals
enrolment = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_enrolment.csv'))
biometric = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_biometric.csv'))
demographic = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'processed', 'cleaned_demographic.csv'))

enrolment['date'] = pd.to_datetime(enrolment['date'])
biometric['date'] = pd.to_datetime(biometric['date'])
demographic['date'] = pd.to_datetime(demographic['date'])

# Weekly aggregation
enrolment_ts = enrolment.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_enrolments': 'sum'
}).reset_index()

biometric_ts = biometric.groupby([pd.Grouper(key='date', freq='W'), 'state']).agg({
    'total_bio_updates': 'sum'
}).reset_index()

print("✓ Data loaded successfully!")
print()

# ============================================================================
# VISUALIZATION 1: CAPACITY PLANNING HEATMAP
# ============================================================================
print("📊 Creating Visualization 1: Capacity Planning Heatmap...")

fig, ax = plt.subplots(figsize=(16, 10))

# Prepare data for heatmap
heatmap_data = capacity_analysis[['state', 'growth_3m_pct_enrol', 'growth_3m_pct_bio', 'growth_3m_pct_demo']].copy()
heatmap_data.columns = ['State', 'Enrolment\nGrowth (%)', 'Biometric\nGrowth (%)', 'Demographic\nGrowth (%)']
heatmap_data = heatmap_data.set_index('State')

# Create heatmap
sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
            cbar_kws={'label': '3-Month Growth Rate (%)'}, linewidths=0.5, ax=ax)

ax.set_title('State-wise Capacity Planning Analysis\n3-Month Forecast Growth Rates', 
             fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('')
ax.set_ylabel('State', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP10_ENHANCED_1_capacity_heatmap.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP10_ENHANCED_1_capacity_heatmap.png")

# ============================================================================
# VISUALIZATION 2: TOP 6 STATES ENROLMENT FORECASTS
# ============================================================================
print("📊 Creating Visualization 2: Top 6 States Enrolment Forecasts...")

top_6_states = capacity_analysis.head(6)['state'].tolist()

fig, axes = plt.subplots(3, 2, figsize=(20, 15))
axes = axes.flatten()

for idx, state in enumerate(top_6_states):
    if state not in enrolment_forecasts:
        continue
    
    ax = axes[idx]
    
    # Get forecast
    forecast = enrolment_forecasts[state]
    
    # Get actuals
    actuals = enrolment_ts[enrolment_ts['state'] == state].copy()
    
    # Split forecast into historical and future
    last_date = actuals['date'].max()
    forecast_future = forecast[forecast['ds'] > last_date]
    forecast_hist = forecast[forecast['ds'] <= last_date]
    
    # Plot actuals
    ax.plot(actuals['date'], actuals['total_enrolments'], 'o-', 
            color='#2E86AB', linewidth=2, markersize=4, label='Actual', alpha=0.7)
    
    # Plot historical fit
    ax.plot(forecast_hist['ds'], forecast_hist['yhat'], '--', 
            color='#A23B72', linewidth=2, label='Model Fit', alpha=0.6)
    
    # Plot forecast
    ax.plot(forecast_future['ds'], forecast_future['yhat'], '-', 
            color='#F18F01', linewidth=3, label='Forecast', alpha=0.9)
    
    # Plot confidence interval
    ax.fill_between(forecast_future['ds'], 
                     forecast_future['yhat_lower'], 
                     forecast_future['yhat_upper'],
                     color='#F18F01', alpha=0.2, label='95% CI')
    
    # Formatting
    ax.set_title(f'{state.title()}\nDemand Score: {capacity_analysis[capacity_analysis["state"]==state]["demand_score"].values[0]:.1f}%', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Weekly Enrolments', fontsize=10)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(style='plain', axis='y')
    
    # Add vertical line at forecast start
    ax.axvline(last_date, color='red', linestyle=':', linewidth=2, alpha=0.5)

plt.suptitle('Top 6 High-Demand States: Enrolment Forecasts (6-Month Horizon)', 
             fontsize=20, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP10_ENHANCED_2_top6_enrolment_forecasts.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP10_ENHANCED_2_top6_enrolment_forecasts.png")

# ============================================================================
# VISUALIZATION 3: TOP 6 STATES BIOMETRIC UPDATE FORECASTS
# ============================================================================
print("📊 Creating Visualization 3: Top 6 States Biometric Update Forecasts...")

fig, axes = plt.subplots(3, 2, figsize=(20, 15))
axes = axes.flatten()

for idx, state in enumerate(top_6_states):
    if state not in biometric_forecasts:
        continue
    
    ax = axes[idx]
    
    forecast = biometric_forecasts[state]
    actuals = biometric_ts[biometric_ts['state'] == state].copy()
    
    last_date = actuals['date'].max()
    forecast_future = forecast[forecast['ds'] > last_date]
    forecast_hist = forecast[forecast['ds'] <= last_date]
    
    ax.plot(actuals['date'], actuals['total_bio_updates'], 'o-', 
            color='#06A77D', linewidth=2, markersize=4, label='Actual', alpha=0.7)
    
    ax.plot(forecast_hist['ds'], forecast_hist['yhat'], '--', 
            color='#D62246', linewidth=2, label='Model Fit', alpha=0.6)
    
    ax.plot(forecast_future['ds'], forecast_future['yhat'], '-', 
            color='#F77F00', linewidth=3, label='Forecast', alpha=0.9)
    
    ax.fill_between(forecast_future['ds'], 
                     forecast_future['yhat_lower'], 
                     forecast_future['yhat_upper'],
                     color='#F77F00', alpha=0.2, label='95% CI')
    
    ax.set_title(f'{state.title()}\nBio Growth (3M): {capacity_analysis[capacity_analysis["state"]==state]["growth_3m_pct_bio"].values[0]:.1f}%', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Weekly Biometric Updates', fontsize=10)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(style='plain', axis='y')
    ax.axvline(last_date, color='red', linestyle=':', linewidth=2, alpha=0.5)

plt.suptitle('Top 6 High-Demand States: Biometric Update Forecasts (6-Month Horizon)', 
             fontsize=20, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP10_ENHANCED_3_top6_biometric_forecasts.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP10_ENHANCED_3_top6_biometric_forecasts.png")

# ============================================================================
# VISUALIZATION 4: DEMAND SCORE RANKING
# ============================================================================
print("📊 Creating Visualization 4: State Demand Score Ranking...")

fig, ax = plt.subplots(figsize=(14, 10))

# Sort by demand score
sorted_capacity = capacity_analysis.sort_values('demand_score', ascending=True)

# Color code by status
colors = []
for status in sorted_capacity['capacity_status']:
    if 'CRITICAL' in status:
        colors.append('#DC2F02')
    elif 'HIGH' in status:
        colors.append('#F48C06')
    elif 'MEDIUM' in status:
        colors.append('#FFBA08')
    elif 'STABLE' in status:
        colors.append('#06A77D')
    else:
        colors.append('#0077B6')

bars = ax.barh(sorted_capacity['state'], sorted_capacity['demand_score'], color=colors, alpha=0.8)

ax.set_xlabel('Demand Score (3-Month Growth %)', fontsize=14, fontweight='bold')
ax.set_ylabel('State', fontsize=14, fontweight='bold')
ax.set_title('State-wise Capacity Demand Ranking\nBased on 3-Month Forecast Growth', 
             fontsize=18, fontweight='bold', pad=20)
ax.axvline(0, color='black', linewidth=0.8)
ax.axvline(30, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Critical Threshold')
ax.axvline(15, color='orange', linestyle='--', linewidth=2, alpha=0.5, label='High Threshold')
ax.grid(True, alpha=0.3, axis='x')
ax.legend(fontsize=11)

# Add value labels
for i, (idx, row) in enumerate(sorted_capacity.iterrows()):
    value = row['demand_score']
    ax.text(value + 50, i, f'{value:.1f}%', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP10_ENHANCED_4_demand_score_ranking.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP10_ENHANCED_4_demand_score_ranking.png")

# ============================================================================
# VISUALIZATION 5: COMPREHENSIVE DASHBOARD
# ============================================================================
print("📊 Creating Visualization 5: Comprehensive Forecast Dashboard...")

fig = plt.figure(figsize=(24, 16))
gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# Panel 1: Capacity Status Distribution
ax1 = fig.add_subplot(gs[0, 0])
status_counts = capacity_analysis['capacity_status'].value_counts()
colors_pie = ['#DC2F02', '#F48C06', '#FFBA08', '#06A77D', '#0077B6']
ax1.pie(status_counts.values, labels=[s.split(' - ')[0] for s in status_counts.index], 
        autopct='%1.1f%%', colors=colors_pie[:len(status_counts)], startangle=90)
ax1.set_title('Capacity Status Distribution', fontsize=14, fontweight='bold')

# Panel 2: Growth Rate Distribution
ax2 = fig.add_subplot(gs[0, 1])
ax2.hist(capacity_analysis['demand_score'], bins=15, color='#2E86AB', alpha=0.7, edgecolor='black')
ax2.axvline(capacity_analysis['demand_score'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
ax2.axvline(capacity_analysis['demand_score'].median(), color='orange', linestyle='--', linewidth=2, label='Median')
ax2.set_xlabel('Demand Score (%)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Number of States', fontsize=11, fontweight='bold')
ax2.set_title('Demand Score Distribution', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Panel 3: Top 3 Critical States Summary
ax3 = fig.add_subplot(gs[0, 2])
ax3.axis('off')
critical_states = capacity_analysis[capacity_analysis['capacity_status'].str.contains('CRITICAL')].head(3)
summary_text = "🔴 TOP 3 CRITICAL STATES\n\n"
for i, (idx, row) in enumerate(critical_states.iterrows(), 1):
    summary_text += f"{i}. {row['state'].upper()}\n"
    summary_text += f"   Demand Score: {row['demand_score']:.1f}%\n"
    summary_text += f"   Enrol: {row['growth_3m_pct_enrol']:+.1f}%\n"
    summary_text += f"   Bio: {row['growth_3m_pct_bio']:+.1f}%\n\n"
ax3.text(0.1, 0.9, summary_text, fontsize=12, verticalalignment='top', 
         family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax3.set_title('Critical Intervention Required', fontsize=14, fontweight='bold')

# Panel 4-6: Top 3 State Forecasts
top_3_critical = critical_states['state'].tolist()[:3]
for i, state in enumerate(top_3_critical):
    ax = fig.add_subplot(gs[1, i])
    
    if state in enrolment_forecasts:
        forecast = enrolment_forecasts[state]
        actuals = enrolment_ts[enrolment_ts['state'] == state].copy()
        
        last_date = actuals['date'].max()
        forecast_future = forecast[forecast['ds'] > last_date]
        
        ax.plot(actuals['date'], actuals['total_enrolments'], 'o-', 
                color='#2E86AB', linewidth=2, markersize=3, label='Actual')
        ax.plot(forecast_future['ds'], forecast_future['yhat'], '-', 
                color='#F18F01', linewidth=3, label='Forecast')
        ax.fill_between(forecast_future['ds'], forecast_future['yhat_lower'], 
                         forecast_future['yhat_upper'], color='#F18F01', alpha=0.2)
        
        ax.set_title(f'{state.title()} - Enrolment Forecast', fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Weekly Enrolments', fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.axvline(last_date, color='red', linestyle=':', linewidth=1.5, alpha=0.5)

# Panel 7-9: Biometric forecasts for top 3
for i, state in enumerate(top_3_critical):
    ax = fig.add_subplot(gs[2, i])
    
    if state in biometric_forecasts:
        forecast = biometric_forecasts[state]
        actuals = biometric_ts[biometric_ts['state'] == state].copy()
        
        last_date = actuals['date'].max()
        forecast_future = forecast[forecast['ds'] > last_date]
        
        ax.plot(actuals['date'], actuals['total_bio_updates'], 'o-', 
                color='#06A77D', linewidth=2, markersize=3, label='Actual')
        ax.plot(forecast_future['ds'], forecast_future['yhat'], '-', 
                color='#F77F00', linewidth=3, label='Forecast')
        ax.fill_between(forecast_future['ds'], forecast_future['yhat_lower'], 
                         forecast_future['yhat_upper'], color='#F77F00', alpha=0.2)
        
        ax.set_title(f'{state.title()} - Biometric Update Forecast', fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Weekly Biometric Updates', fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.axvline(last_date, color='red', linestyle=':', linewidth=1.5, alpha=0.5)

plt.suptitle('UIDAI Aadhaar Update Demand Forecasting - Comprehensive Dashboard\nProphet ML Model with 6-Month Forecast Horizon', 
             fontsize=22, fontweight='bold', y=0.995)
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP10_ENHANCED_5_comprehensive_dashboard.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP10_ENHANCED_5_comprehensive_dashboard.png")

# ============================================================================
# VISUALIZATION 6: GROWTH TRAJECTORY COMPARISON
# ============================================================================
print("📊 Creating Visualization 6: Multi-Horizon Growth Trajectory...")

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 7))

# 1-Month Growth
sorted_1m = capacity_analysis.sort_values('growth_1m_pct', ascending=False).head(10)
ax1.barh(sorted_1m['state'], sorted_1m['growth_1m_pct'], color='#06A77D', alpha=0.8)
ax1.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('1-Month Forecast\nEnrolment Growth', fontsize=14, fontweight='bold')
ax1.axvline(0, color='black', linewidth=0.8)
ax1.grid(True, alpha=0.3, axis='x')

# 3-Month Growth
sorted_3m = capacity_analysis.sort_values('growth_3m_pct_enrol', ascending=False).head(10)
ax2.barh(sorted_3m['state'], sorted_3m['growth_3m_pct_enrol'], color='#F48C06', alpha=0.8)
ax2.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('3-Month Forecast\nEnrolment Growth', fontsize=14, fontweight='bold')
ax2.axvline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='x')

# 6-Month Growth
sorted_6m = capacity_analysis.sort_values('growth_6m_pct', ascending=False).head(10)
ax3.barh(sorted_6m['state'], sorted_6m['growth_6m_pct'], color='#DC2F02', alpha=0.8)
ax3.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')
ax3.set_title('6-Month Forecast\nEnrolment Growth', fontsize=14, fontweight='bold')
ax3.axvline(0, color='black', linewidth=0.8)
ax3.grid(True, alpha=0.3, axis='x')

plt.suptitle('Multi-Horizon Growth Trajectory Analysis\nTop 10 States by Forecast Period', 
             fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PROJECT_PATH, 'visualizations', 'STEP10_ENHANCED_6_growth_trajectory.png'), bbox_inches='tight')
plt.close()

print("   ✓ Saved: STEP10_ENHANCED_6_growth_trajectory.png")

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 100)
print("✅ ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
print("=" * 100)
print()
print("📁 FILES CREATED:")
print("   ✓ STEP10_ENHANCED_1_capacity_heatmap.png")
print("   ✓ STEP10_ENHANCED_2_top6_enrolment_forecasts.png")
print("   ✓ STEP10_ENHANCED_3_top6_biometric_forecasts.png")
print("   ✓ STEP10_ENHANCED_4_demand_score_ranking.png")
print("   ✓ STEP10_ENHANCED_5_comprehensive_dashboard.png")
print("   ✓ STEP10_ENHANCED_6_growth_trajectory.png")
print()
print("🎯 READY FOR HACKATHON SUBMISSION!")
print("   These visualizations demonstrate:")
print("   • Professional ML-based forecasting with Prophet")
print("   • Multi-horizon capacity planning (1M, 3M, 6M)")
print("   • State-wise bottleneck prediction")
print("   • Actionable insights for UIDAI infrastructure planning")
print("=" * 100)
