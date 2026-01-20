"""
STEP 10 - VISUALIZATION GENERATOR: Prophet Forecast Charts
===========================================================
Creates professional visualizations for time series forecasts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("=" * 100)
print("STEP 10 - GENERATING PROPHET FORECAST VISUALIZATIONS")
print("=" * 100)
print()

# ============================================================================
# LOAD MODELS AND FORECASTS
# ============================================================================
print("📂 Loading models and forecasts...")

try:
    with open('../results/STEP10_models_and_forecasts.pkl', 'rb') as f:
        data = pickle.load(f)
    
    enrolment_models = data['enrolment_models']
    enrolment_forecasts = data['enrolment_forecasts']
    biometric_models = data['biometric_models']
    biometric_forecasts = data['biometric_forecasts']
    demographic_models = data['demographic_models']
    demographic_forecasts = data['demographic_forecasts']
    top_states = data['top_states']
    capacity_df = data['capacity_df']
    
    print(f"✓ Loaded forecasts for {len(enrolment_forecasts)} states")
    print()
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("   Please run STEP10_prophet_forecasting.py first!")
    exit()

# ============================================================================
# CHART 1: TOP 6 STATES - ENROLMENT FORECASTS
# ============================================================================
print("🎨 Creating Chart 1: Top 6 States - Enrolment Forecasts...")

# Get top 6 states by forecast growth
top_6_states = capacity_df.nlargest(6, 'enrol_growth_pct')['state'].tolist()

fig, axes = plt.subplots(3, 2, figsize=(20, 16))
fig.suptitle('Top 6 States - Enrolment Demand Forecasts (12-Week Horizon)', 
             fontsize=18, fontweight='bold', y=0.995)

for idx, (state, ax) in enumerate(zip(top_6_states, axes.flatten())):
    if state not in enrolment_forecasts:
        continue
    
    forecast = enrolment_forecasts[state]
    
    # Plot forecast
    ax.plot(forecast['ds'], forecast['yhat'], 'b-', linewidth=2, label='Forecast')
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                    alpha=0.3, color='blue', label='95% Confidence Interval')
    
    # Mark future period
    last_date = forecast['ds'].max() - pd.Timedelta(weeks=12)
    ax.axvline(last_date, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Forecast Start')
    
    # Get growth rate
    growth = capacity_df[capacity_df['state'] == state]['enrol_growth_pct'].values[0]
    
    ax.set_title(f'{state.title()} - Growth: {growth:+.1f}%', fontweight='bold', fontsize=12)
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Weekly Enrolments', fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)

plt.tight_layout()
plt.savefig('../visualizations/STEP10_1_enrolment_forecasts_top6.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP10_1_enrolment_forecasts_top6.png")
plt.close()

# ============================================================================
# CHART 2: TOP 6 STATES - BIOMETRIC UPDATE FORECASTS
# ============================================================================
print("🎨 Creating Chart 2: Top 6 States - Biometric Update Forecasts...")

top_6_bio = capacity_df.nlargest(6, 'bio_growth_pct')['state'].tolist()

fig, axes = plt.subplots(3, 2, figsize=(20, 16))
fig.suptitle('Top 6 States - Biometric Update Demand Forecasts (12-Week Horizon)', 
             fontsize=18, fontweight='bold', y=0.995)

for idx, (state, ax) in enumerate(zip(top_6_bio, axes.flatten())):
    if state not in biometric_forecasts:
        continue
    
    forecast = biometric_forecasts[state]
    
    # Plot forecast
    ax.plot(forecast['ds'], forecast['yhat'], 'g-', linewidth=2, label='Forecast')
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                    alpha=0.3, color='green', label='95% Confidence Interval')
    
    # Mark future period
    last_date = forecast['ds'].max() - pd.Timedelta(weeks=12)
    ax.axvline(last_date, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Forecast Start')
    
    # Get growth rate
    growth = capacity_df[capacity_df['state'] == state]['bio_growth_pct'].values[0]
    
    ax.set_title(f'{state.title()} - Growth: {growth:+.1f}%', fontweight='bold', fontsize=12)
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Weekly Biometric Updates', fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)

plt.tight_layout()
plt.savefig('../visualizations/STEP10_2_biometric_forecasts_top6.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP10_2_biometric_forecasts_top6.png")
plt.close()

# ============================================================================
# CHART 3: CAPACITY PLANNING DASHBOARD
# ============================================================================
print("🎨 Creating Chart 3: Capacity Planning Dashboard...")

fig = plt.figure(figsize=(20, 14))
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)
fig.suptitle('Capacity Planning Dashboard - Forecast-Based Demand Analysis', 
             fontsize=18, fontweight='bold', y=0.98)

# 3a: Growth rate comparison
ax1 = fig.add_subplot(gs[0, :])
sorted_capacity = capacity_df.sort_values('enrol_growth_pct', ascending=True)

x = np.arange(len(sorted_capacity))
width = 0.35

bars1 = ax1.barh(x - width/2, sorted_capacity['enrol_growth_pct'], width, 
                label='Enrolment Growth', color='#4A90E2', edgecolor='black', linewidth=1)
bars2 = ax1.barh(x + width/2, sorted_capacity['bio_growth_pct'], width, 
                label='Biometric Update Growth', color='#50C878', edgecolor='black', linewidth=1)

ax1.set_yticks(x)
ax1.set_yticklabels(sorted_capacity['state'].str.title(), fontsize=9)
ax1.set_xlabel('Forecasted Growth Rate (%)', fontweight='bold', fontsize=12)
ax1.set_title('State-wise Demand Growth Forecast (Next 12 Weeks)', fontweight='bold', fontsize=14)
ax1.axvline(0, color='black', linewidth=1)
ax1.axvline(20, color='red', linestyle='--', linewidth=2, alpha=0.7, label='High Growth Threshold (20%)')
ax1.axvline(-10, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Decline Threshold (-10%)')
ax1.legend(fontsize=10, loc='lower right')
ax1.grid(axis='x', alpha=0.3)

# 3b: Capacity need classification
ax2 = fig.add_subplot(gs[1, 0])
capacity_counts = capacity_df['capacity_need'].value_counts()
colors_capacity = {'HIGH - Expansion Required': '#E74C3C', 
                   'MEDIUM - Monitor Closely': '#F39C12',
                   'STABLE - No Action Needed': '#2ECC71',
                   'LOW - Potential Overcapacity': '#3498DB'}

wedges, texts, autotexts = ax2.pie(capacity_counts.values, 
                                     labels=[label.split(' - ')[0] for label in capacity_counts.index],
                                     colors=[colors_capacity.get(label, '#95A5A6') for label in capacity_counts.index],
                                     autopct='%1.1f%%',
                                     startangle=90,
                                     textprops={'fontsize': 11, 'weight': 'bold'},
                                     explode=[0.1 if 'HIGH' in label else 0 for label in capacity_counts.index])

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(12)

ax2.set_title('Capacity Need Classification', fontweight='bold', fontsize=13, pad=15)

# 3c: Top states requiring expansion
ax3 = fig.add_subplot(gs[1, 1])
high_capacity_states = capacity_df[capacity_df['capacity_need'].str.contains('HIGH')].nlargest(10, 'enrol_growth_pct')

if len(high_capacity_states) > 0:
    y_pos = np.arange(len(high_capacity_states))
    ax3.barh(y_pos, high_capacity_states['enrol_growth_pct'], 
            color='#E74C3C', edgecolor='black', linewidth=1.5, alpha=0.8)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(high_capacity_states['state'].str.title(), fontsize=10)
    ax3.set_xlabel('Enrolment Growth (%)', fontweight='bold', fontsize=11)
    ax3.set_title('States Requiring Capacity Expansion', fontweight='bold', fontsize=13)
    ax3.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(high_capacity_states['enrol_growth_pct']):
        ax3.text(v + 1, i, f'{v:.1f}%', va='center', fontweight='bold', fontsize=10)
else:
    ax3.text(0.5, 0.5, 'No states require\nhigh capacity expansion', 
            ha='center', va='center', fontsize=14, transform=ax3.transAxes)
    ax3.axis('off')

# 3d: Forecast summary table
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

summary_text = """
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    CAPACITY PLANNING SUMMARY - FORECAST INSIGHTS                              ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

FORECAST PARAMETERS:
• Forecast Horizon: 12 weeks (3 months)
• Model: Facebook Prophet with multiplicative seasonality
• Confidence Interval: 95%
• Data Aggregation: Weekly level

CAPACITY RECOMMENDATIONS:
"""

high_count = len(capacity_df[capacity_df['capacity_need'].str.contains('HIGH')])
medium_count = len(capacity_df[capacity_df['capacity_need'].str.contains('MEDIUM')])
stable_count = len(capacity_df[capacity_df['capacity_need'].str.contains('STABLE')])

summary_text += f"""
🔴 HIGH PRIORITY ({high_count} states): Immediate capacity expansion required
   → Expected growth >20% in next 12 weeks
   → Recommend: Add update centers, increase staffing, extend hours

🟡 MEDIUM PRIORITY ({medium_count} states): Monitor demand closely
   → Expected growth 10-20% in next 12 weeks
   → Recommend: Prepare contingency plans, track weekly metrics

🟢 STABLE ({stable_count} states): Current capacity adequate
   → Expected growth <10% in next 12 weeks
   → Recommend: Maintain current operations

TOP 5 STATES BY FORECASTED DEMAND:
"""

top_5_demand = capacity_df.nlargest(5, 'enrol_forecast_avg')
for idx, row in top_5_demand.iterrows():
    summary_text += f"\n  {row['state'].title():40s} → Avg Weekly Enrolments: {row['enrol_forecast_avg']:,.0f} | Growth: {row['enrol_growth_pct']:+.1f}%"

ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.9, 
                 edgecolor='black', linewidth=2))

plt.savefig('../visualizations/STEP10_3_capacity_planning_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP10_3_capacity_planning_dashboard.png")
plt.close()

# ============================================================================
# CHART 4: SEASONAL DECOMPOSITION (TOP 3 STATES)
# ============================================================================
print("🎨 Creating Chart 4: Seasonal Decomposition for Top 3 States...")

top_3_states = capacity_df.nlargest(3, 'enrol_growth_pct')['state'].tolist()

fig, axes = plt.subplots(3, 3, figsize=(22, 16))
fig.suptitle('Seasonal Decomposition - Top 3 States by Growth', 
             fontsize=18, fontweight='bold', y=0.995)

for idx, state in enumerate(top_3_states):
    if state not in enrolment_models:
        continue
    
    model = enrolment_models[state]
    forecast = enrolment_forecasts[state]
    
    # Trend
    ax_trend = axes[idx, 0]
    ax_trend.plot(forecast['ds'], forecast['trend'], 'b-', linewidth=2)
    ax_trend.set_title(f'{state.title()} - Trend Component', fontweight='bold', fontsize=11)
    ax_trend.set_ylabel('Trend', fontweight='bold')
    ax_trend.grid(alpha=0.3)
    plt.setp(ax_trend.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    
    # Weekly seasonality
    ax_weekly = axes[idx, 1]
    if 'weekly' in forecast.columns:
        ax_weekly.plot(forecast['ds'], forecast['weekly'], 'g-', linewidth=2)
    ax_weekly.set_title(f'{state.title()} - Weekly Seasonality', fontweight='bold', fontsize=11)
    ax_weekly.set_ylabel('Weekly Effect', fontweight='bold')
    ax_weekly.grid(alpha=0.3)
    plt.setp(ax_weekly.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    
    # Yearly seasonality
    ax_yearly = axes[idx, 2]
    if 'yearly' in forecast.columns:
        ax_yearly.plot(forecast['ds'], forecast['yearly'], 'r-', linewidth=2)
    ax_yearly.set_title(f'{state.title()} - Yearly Seasonality', fontweight='bold', fontsize=11)
    ax_yearly.set_ylabel('Yearly Effect', fontweight='bold')
    ax_yearly.grid(alpha=0.3)
    plt.setp(ax_yearly.get_xticklabels(), rotation=45, ha='right', fontsize=8)

plt.tight_layout()
plt.savefig('../visualizations/STEP10_4_seasonal_decomposition_top3.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP10_4_seasonal_decomposition_top3.png")
plt.close()

# ============================================================================
# CHART 5: FORECAST ACCURACY METRICS
# ============================================================================
print("🎨 Creating Chart 5: Forecast Accuracy Metrics...")

fig = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)
fig.suptitle('Forecast Quality & Accuracy Metrics', 
             fontsize=18, fontweight='bold', y=0.98)

# 5a: Confidence interval width
ax1 = fig.add_subplot(gs[0, 0])
ci_widths = []
state_names = []

for state in top_states:
    if state not in enrolment_forecasts:
        continue
    
    forecast = enrolment_forecasts[state]
    future_forecast = forecast[forecast['ds'] > forecast['ds'].max() - pd.Timedelta(weeks=12)]
    avg_ci_width = (future_forecast['yhat_upper'] - future_forecast['yhat_lower']).mean()
    avg_forecast = future_forecast['yhat'].mean()
    
    if avg_forecast > 0:
        ci_pct = (avg_ci_width / avg_forecast) * 100
        ci_widths.append(ci_pct)
        state_names.append(state)

sorted_indices = np.argsort(ci_widths)
sorted_ci = [ci_widths[i] for i in sorted_indices]
sorted_states = [state_names[i] for i in sorted_indices]

ax1.barh(range(len(sorted_ci)), sorted_ci, color='#4A90E2', edgecolor='black', linewidth=1)
ax1.set_yticks(range(len(sorted_states)))
ax1.set_yticklabels([s.title() for s in sorted_states], fontsize=9)
ax1.set_xlabel('Confidence Interval Width (% of Forecast)', fontweight='bold', fontsize=11)
ax1.set_title('Forecast Uncertainty by State', fontweight='bold', fontsize=13)
ax1.axvline(50, color='red', linestyle='--', linewidth=2, alpha=0.7, label='High Uncertainty (>50%)')
ax1.legend(fontsize=10)
ax1.grid(axis='x', alpha=0.3)

# 5b: Growth volatility
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(capacity_df['enrol_growth_pct'], capacity_df['bio_growth_pct'], 
           s=200, alpha=0.6, c=capacity_df['enrol_forecast_avg'], 
           cmap='viridis', edgecolors='black', linewidths=2)

for idx, row in capacity_df.iterrows():
    ax2.annotate(row['state'][:15].title(), 
                xy=(row['enrol_growth_pct'], row['bio_growth_pct']),
                xytext=(5, 5), textcoords='offset points', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

ax2.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
ax2.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
ax2.axhline(20, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax2.axvline(20, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax2.set_xlabel('Enrolment Growth (%)', fontweight='bold', fontsize=11)
ax2.set_ylabel('Biometric Update Growth (%)', fontweight='bold', fontsize=11)
ax2.set_title('Growth Correlation: Enrolment vs Biometric Updates', fontweight='bold', fontsize=13)
ax2.grid(alpha=0.3)

# 5c: Summary statistics
ax3 = fig.add_subplot(gs[1, :])
ax3.axis('off')

stats_text = """
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                       FORECAST QUALITY ASSESSMENT                                             ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

MODEL PERFORMANCE METRICS:
"""

avg_enrol_growth = capacity_df['enrol_growth_pct'].mean()
avg_bio_growth = capacity_df['bio_growth_pct'].mean()
max_enrol_growth = capacity_df['enrol_growth_pct'].max()
min_enrol_growth = capacity_df['enrol_growth_pct'].min()

stats_text += f"""
📊 OVERALL STATISTICS:
   • Average Enrolment Growth: {avg_enrol_growth:+.1f}%
   • Average Biometric Growth: {avg_bio_growth:+.1f}%
   • Maximum Growth State: {capacity_df.loc[capacity_df['enrol_growth_pct'].idxmax(), 'state'].title()} ({max_enrol_growth:+.1f}%)
   • Minimum Growth State: {capacity_df.loc[capacity_df['enrol_growth_pct'].idxmin(), 'state'].title()} ({min_enrol_growth:+.1f}%)

🎯 FORECAST RELIABILITY:
   • Models trained on {len(top_states)} states
   • 95% confidence intervals provided
   • Seasonal patterns captured (weekly + yearly)
   • Trend changepoints automatically detected

⚠️  LIMITATIONS:
   • Forecasts assume historical patterns continue
   • External factors (policy changes, campaigns) not modeled
   • Recommend updating forecasts monthly with new data
   • Use confidence intervals for capacity planning buffer
"""

ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.9, 
                 edgecolor='black', linewidth=2))

plt.savefig('../visualizations/STEP10_5_forecast_accuracy_metrics.png', dpi=300, bbox_inches='tight')
print("✓ Saved: STEP10_5_forecast_accuracy_metrics.png")
plt.close()

print()
print("=" * 100)
print("✅ ALL VISUALIZATIONS CREATED!")
print("=" * 100)
print()
print("📁 Generated Files:")
print("  1. STEP10_1_enrolment_forecasts_top6.png")
print("  2. STEP10_2_biometric_forecasts_top6.png")
print("  3. STEP10_3_capacity_planning_dashboard.png")
print("  4. STEP10_4_seasonal_decomposition_top3.png")
print("  5. STEP10_5_forecast_accuracy_metrics.png")
print()
print("🎨 All visualizations at 300 DPI, ready for hackathon PDF!")
print("=" * 100)
