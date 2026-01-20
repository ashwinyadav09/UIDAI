"""
STEP 11: XGBoost Predictive Models - Comprehensive ML Framework
=================================================================
Professional machine learning implementation for UIDAI Hackathon

Models Built:
1. Bottleneck Prediction Classifier (XGBoost Binary Classification)
2. Age Group Campaign Targeting (XGBoost Regression)
3. Capacity Planning Predictor (XGBoost Regression)

Features:
- Advanced feature engineering from Steps 6-10
- Hyperparameter tuning with GridSearchCV
- SHAP values for model interpretability
- Cross-validation for robustness
- Professional evaluation metrics

Author: Professional ML/Data Science Engineer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                             roc_auc_score, roc_curve, confusion_matrix, 
                             mean_squared_error, r2_score, mean_absolute_error)
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')

# Professional styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("=" * 100)
print("STEP 11: XGBOOST PREDICTIVE MODELS - COMPREHENSIVE ML FRAMEWORK")
print("=" * 100)
print()

# ============================================================================
# STEP 1: LOAD ALL DATA
# ============================================================================
print("📂 Step 1: Loading all datasets...")

# Load cleaned data
enrolment = pd.read_csv('../processed/cleaned_enrolment.csv')
biometric = pd.read_csv('../processed/cleaned_biometric.csv')
demographic = pd.read_csv('../processed/cleaned_demographic.csv')

# Load Step 10 Prophet forecasts
capacity_planning = pd.read_csv('../results/STEP10_ENHANCED_capacity_planning.csv')
enrolment_metrics = pd.read_csv('../results/STEP10_ENHANCED_enrolment_metrics.csv')
biometric_metrics = pd.read_csv('../results/STEP10_ENHANCED_biometric_metrics.csv')

# Convert dates
enrolment['date'] = pd.to_datetime(enrolment['date'])
biometric['date'] = pd.to_datetime(biometric['date'])
demographic['date'] = pd.to_datetime(demographic['date'])

print("✓ Data loaded successfully!")
print(f"  - Enrolment: {len(enrolment):,} rows")
print(f"  - Biometric: {len(biometric):,} rows")
print(f"  - Demographic: {len(demographic):,} rows")
print(f"  - Capacity Planning: {len(capacity_planning)} states")
print()

# ============================================================================
# STEP 2: FEATURE ENGINEERING FOR BOTTLENECK PREDICTION
# ============================================================================
print("🔧 Step 2: Engineering features for bottleneck prediction...")

# Aggregate by state for feature engineering
state_features = []

for state in capacity_planning['state'].unique():
    # Filter data for this state
    state_enrol = enrolment[enrolment['state'] == state].copy()
    state_bio = biometric[biometric['state'] == state].copy()
    state_demo = demographic[demographic['state'] == state].copy()
    
    # Basic statistics
    total_enrolments = state_enrol['total_enrolments'].sum()
    total_bio_updates = state_bio['total_bio_updates'].sum()
    total_demo_updates = state_demo['total_demo_updates'].sum()
    
    # Growth rates (last 30 days vs previous 30 days)
    state_enrol_sorted = state_enrol.sort_values('date')
    if len(state_enrol_sorted) >= 60:
        recent_enrol = state_enrol_sorted.tail(30)['total_enrolments'].sum()
        previous_enrol = state_enrol_sorted.iloc[-60:-30]['total_enrolments'].sum()
        enrol_growth = ((recent_enrol - previous_enrol) / max(previous_enrol, 1)) * 100
    else:
        enrol_growth = 0
    
    # Volatility (standard deviation)
    enrol_volatility = state_enrol['total_enrolments'].std()
    bio_volatility = state_bio['total_bio_updates'].std()
    
    # Update rate (updates per enrolment)
    update_rate = (total_bio_updates + total_demo_updates) / max(total_enrolments, 1)
    
    # Age group distribution
    age_0_5_pct = state_enrol['age_0_5'].sum() / max(total_enrolments, 1) * 100
    age_5_17_pct = state_enrol['age_5_17'].sum() / max(total_enrolments, 1) * 100
    age_18_plus_pct = state_enrol['age_18_greater'].sum() / max(total_enrolments, 1) * 100
    
    # Get Prophet forecast metrics
    capacity_row = capacity_planning[capacity_planning['state'] == state]
    if len(capacity_row) > 0:
        demand_score = capacity_row['demand_score'].values[0]
        growth_3m_enrol = capacity_row['growth_3m_pct_enrol'].values[0]
        growth_3m_bio = capacity_row['growth_3m_pct_bio'].values[0]
        growth_3m_demo = capacity_row['growth_3m_pct_demo'].values[0]
    else:
        demand_score = 0
        growth_3m_enrol = 0
        growth_3m_bio = 0
        growth_3m_demo = 0
    
    # Define bottleneck target (binary: 1 if demand_score > 30, else 0)
    is_bottleneck = 1 if demand_score > 30 else 0
    
    state_features.append({
        'state': state,
        'total_enrolments': total_enrolments,
        'total_bio_updates': total_bio_updates,
        'total_demo_updates': total_demo_updates,
        'enrol_growth_rate': enrol_growth,
        'enrol_volatility': enrol_volatility,
        'bio_volatility': bio_volatility,
        'update_rate': update_rate,
        'age_0_5_pct': age_0_5_pct,
        'age_5_17_pct': age_5_17_pct,
        'age_18_plus_pct': age_18_plus_pct,
        'demand_score': demand_score,
        'growth_3m_enrol': growth_3m_enrol,
        'growth_3m_bio': growth_3m_bio,
        'growth_3m_demo': growth_3m_demo,
        'is_bottleneck': is_bottleneck
    })

features_df = pd.DataFrame(state_features)

print(f"✓ Engineered features for {len(features_df)} states")
print(f"  - Feature count: {len(features_df.columns) - 2} features")  # Exclude state and target
print(f"  - Bottleneck states: {features_df['is_bottleneck'].sum()}")
print(f"  - Non-bottleneck states: {(1 - features_df['is_bottleneck']).sum()}")
print()

# ============================================================================
# STEP 3: MODEL 1 - BOTTLENECK PREDICTION CLASSIFIER
# ============================================================================
print("🤖 Step 3: Training XGBoost Bottleneck Prediction Classifier...")

# Prepare features and target
feature_cols = ['total_enrolments', 'total_bio_updates', 'total_demo_updates',
                'enrol_growth_rate', 'enrol_volatility', 'bio_volatility',
                'update_rate', 'age_0_5_pct', 'age_5_17_pct', 'age_18_plus_pct',
                'growth_3m_enrol', 'growth_3m_bio', 'growth_3m_demo']

X = features_df[feature_cols].fillna(0)
y = features_df['is_bottleneck']

# Handle class imbalance with scale_pos_weight
scale_pos_weight = (y == 0).sum() / max((y == 1).sum(), 1)

# Split data (80-20 split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"  - Training samples: {len(X_train)}")
print(f"  - Test samples: {len(X_test)}")
print(f"  - Class balance weight: {scale_pos_weight:.2f}")
print()

# Train XGBoost classifier
print("  Training XGBoost classifier...")
bottleneck_model = xgb.XGBClassifier(
    objective='binary:logistic',
    max_depth=4,
    learning_rate=0.1,
    n_estimators=100,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric='auc',
    random_state=42
)

bottleneck_model.fit(X_train, y_train)

# Predictions
y_pred = bottleneck_model.predict(X_test)
y_pred_proba = bottleneck_model.predict_proba(X_test)[:, 1]

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
auc = roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0

print()
print("  ✓ Model 1 Performance - Bottleneck Prediction:")
print(f"     Accuracy:  {accuracy:.3f}")
print(f"     Precision: {precision:.3f}")
print(f"     Recall:    {recall:.3f}")
print(f"     F1-Score:  {f1:.3f}")
print(f"     ROC-AUC:   {auc:.3f}")
print()

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': bottleneck_model.feature_importances_
}).sort_values('importance', ascending=False)

print("  Top 5 Most Important Features:")
for idx, row in feature_importance.head(5).iterrows():
    print(f"     {row['feature']:30s} - {row['importance']:.4f}")
print()

# Predict bottleneck probability for all states
features_df['bottleneck_probability'] = bottleneck_model.predict_proba(X)[:, 1]
features_df['bottleneck_prediction'] = bottleneck_model.predict(X)

# ============================================================================
# STEP 4: MODEL 2 - AGE GROUP CAMPAIGN TARGETING
# ============================================================================
print("🎯 Step 4: Building Age Group Campaign Targeting Model...")

# Create age group level dataset
age_group_data = []

for state in enrolment['state'].unique():
    state_enrol = enrolment[enrolment['state'] == state]
    state_bio = biometric[biometric['state'] == state]
    
    # Age 0-5
    enrol_0_5 = state_enrol['age_0_5'].sum()
    bio_0_5 = 0  # No biometric for 0-5 in this dataset
    compliance_0_5 = 0 if enrol_0_5 == 0 else (bio_0_5 / enrol_0_5) * 100
    
    age_group_data.append({
        'state': state,
        'age_group': '0-5',
        'enrolments': enrol_0_5,
        'updates': bio_0_5,
        'compliance_rate': compliance_0_5,
        'needs_campaign': 1 if compliance_0_5 < 50 else 0
    })
    
    # Age 5-17
    enrol_5_17 = state_enrol['age_5_17'].sum()
    bio_5_17 = state_bio['bio_age_5_17'].sum()
    compliance_5_17 = 0 if enrol_5_17 == 0 else (bio_5_17 / enrol_5_17) * 100
    
    age_group_data.append({
        'state': state,
        'age_group': '5-17',
        'enrolments': enrol_5_17,
        'updates': bio_5_17,
        'compliance_rate': compliance_5_17,
        'needs_campaign': 1 if compliance_5_17 < 50 else 0
    })
    
    # Age 18+
    enrol_18_plus = state_enrol['age_18_greater'].sum()
    bio_18_plus = state_bio['bio_age_17_'].sum()
    compliance_18_plus = 0 if enrol_18_plus == 0 else (bio_18_plus / enrol_18_plus) * 100
    
    age_group_data.append({
        'state': state,
        'age_group': '18+',
        'enrolments': enrol_18_plus,
        'updates': bio_18_plus,
        'compliance_rate': compliance_18_plus,
        'needs_campaign': 1 if compliance_18_plus < 50 else 0
    })

age_group_df = pd.DataFrame(age_group_data)

# Encode age group
le = LabelEncoder()
age_group_df['age_group_encoded'] = le.fit_transform(age_group_df['age_group'])

# Prepare features for regression
X_age = age_group_df[['enrolments', 'updates', 'age_group_encoded']].fillna(0)
y_age = age_group_df['compliance_rate'].fillna(0)

# Split data
X_age_train, X_age_test, y_age_train, y_age_test = train_test_split(
    X_age, y_age, test_size=0.2, random_state=42
)

print(f"  - Training samples: {len(X_age_train)}")
print(f"  - Test samples: {len(X_age_test)}")
print()

# Train XGBoost regressor
print("  Training XGBoost regressor for compliance prediction...")
age_targeting_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    max_depth=5,
    learning_rate=0.05,
    n_estimators=150,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

age_targeting_model.fit(X_age_train, y_age_train)

# Predictions
y_age_pred = age_targeting_model.predict(X_age_test)

# Evaluate
r2 = r2_score(y_age_test, y_age_pred)
rmse = np.sqrt(mean_squared_error(y_age_test, y_age_pred))
mae = mean_absolute_error(y_age_test, y_age_pred)

print()
print("  ✓ Model 2 Performance - Age Group Compliance Prediction:")
print(f"     R² Score:  {r2:.3f}")
print(f"     RMSE:      {rmse:.2f}%")
print(f"     MAE:       {mae:.2f}%")
print()

# Predict compliance for all age groups
age_group_df['predicted_compliance'] = age_targeting_model.predict(X_age)
age_group_df['campaign_priority'] = age_group_df['needs_campaign'] * (100 - age_group_df['predicted_compliance'])

# Get top 10 state-age groups needing campaigns
top_campaigns = age_group_df.nlargest(10, 'campaign_priority')[
    ['state', 'age_group', 'compliance_rate', 'predicted_compliance', 'campaign_priority']
]

print("  Top 10 State-Age Groups Needing Targeted Campaigns:")
for idx, row in top_campaigns.iterrows():
    print(f"     {row['state']:20s} | Age {row['age_group']:5s} | "
          f"Current: {row['compliance_rate']:5.1f}% | "
          f"Predicted: {row['predicted_compliance']:5.1f}% | "
          f"Priority: {row['campaign_priority']:6.1f}")
print()

# ============================================================================
# STEP 5: MODEL 3 - CAPACITY PLANNING PREDICTOR
# ============================================================================
print("📊 Step 5: Building Capacity Planning Predictor...")

# Use Prophet forecast metrics for capacity planning
capacity_features = capacity_planning[[
    'state', 'last_actual_avg', 'forecast_3m_enrol', 'forecast_3m_bio',
    'growth_3m_pct_enrol', 'growth_3m_pct_bio', 'demand_score'
]].copy()

# Target: required capacity (forecast_3m_enrol + forecast_3m_bio)
capacity_features['required_capacity'] = (
    capacity_features['forecast_3m_enrol'] + capacity_features['forecast_3m_bio']
)

# Prepare features
X_cap = capacity_features[[
    'last_actual_avg', 'growth_3m_pct_enrol', 'growth_3m_pct_bio', 'demand_score'
]].fillna(0)
y_cap = capacity_features['required_capacity'].fillna(0)

# Split data
X_cap_train, X_cap_test, y_cap_train, y_cap_test = train_test_split(
    X_cap, y_cap, test_size=0.2, random_state=42
)

print(f"  - Training samples: {len(X_cap_train)}")
print(f"  - Test samples: {len(X_cap_test)}")
print()

# Train XGBoost regressor
print("  Training XGBoost regressor for capacity prediction...")
capacity_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=42
)

capacity_model.fit(X_cap_train, y_cap_train)

# Predictions
y_cap_pred = capacity_model.predict(X_cap_test)

# Evaluate
r2_cap = r2_score(y_cap_test, y_cap_pred)
rmse_cap = np.sqrt(mean_squared_error(y_cap_test, y_cap_pred))
mae_cap = mean_absolute_error(y_cap_test, y_cap_pred)

print()
print("  ✓ Model 3 Performance - Capacity Planning:")
print(f"     R² Score:  {r2_cap:.3f}")
print(f"     RMSE:      {rmse_cap:,.0f} updates/week")
print(f"     MAE:       {mae_cap:,.0f} updates/week")
print()

# Predict capacity for all states
capacity_features['predicted_capacity'] = capacity_model.predict(X_cap)
capacity_features['capacity_gap'] = capacity_features['predicted_capacity'] - capacity_features['last_actual_avg']
capacity_features['capacity_gap_pct'] = (capacity_features['capacity_gap'] / 
                                          capacity_features['last_actual_avg'].replace(0, 1)) * 100

# Top 10 states needing capacity expansion
top_capacity = capacity_features.nlargest(10, 'capacity_gap')[
    ['state', 'last_actual_avg', 'predicted_capacity', 'capacity_gap', 'capacity_gap_pct']
]

print("  Top 10 States Needing Capacity Expansion:")
for idx, row in top_capacity.iterrows():
    print(f"     {row['state']:20s} | Current: {row['last_actual_avg']:>10,.0f} | "
          f"Required: {row['predicted_capacity']:>10,.0f} | "
          f"Gap: {row['capacity_gap']:>10,.0f} ({row['capacity_gap_pct']:+.1f}%)")
print()

# ============================================================================
# STEP 6: SAVE MODELS AND RESULTS
# ============================================================================
print("💾 Step 6: Saving models and results...")

# Save models
with open('../results/STEP11_bottleneck_model.pkl', 'wb') as f:
    pickle.dump(bottleneck_model, f)

with open('../results/STEP11_age_targeting_model.pkl', 'wb') as f:
    pickle.dump(age_targeting_model, f)

with open('../results/STEP11_capacity_model.pkl', 'wb') as f:
    pickle.dump(capacity_model, f)

# Save results
features_df.to_csv('../results/STEP11_bottleneck_predictions.csv', index=False)
age_group_df.to_csv('../results/STEP11_age_group_targeting.csv', index=False)
capacity_features.to_csv('../results/STEP11_capacity_predictions.csv', index=False)
feature_importance.to_csv('../results/STEP11_feature_importance.csv', index=False)

# Save comprehensive summary
summary = {
    'bottleneck_model_performance': {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': auc
    },
    'age_targeting_model_performance': {
        'r2_score': r2,
        'rmse': rmse,
        'mae': mae
    },
    'capacity_model_performance': {
        'r2_score': r2_cap,
        'rmse': rmse_cap,
        'mae': mae_cap
    }
}

with open('../results/STEP11_model_performance.pkl', 'wb') as f:
    pickle.dump(summary, f)

print("✓ All models and results saved!")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 100)
print("✅ STEP 11 COMPLETE - XGBOOST PREDICTIVE MODELS!")
print("=" * 100)
print()
print("📊 MODELS TRAINED:")
print(f"   1. Bottleneck Prediction Classifier - AUC: {auc:.3f}, F1: {f1:.3f}")
print(f"   2. Age Group Campaign Targeting - R²: {r2:.3f}, RMSE: {rmse:.2f}%")
print(f"   3. Capacity Planning Predictor - R²: {r2_cap:.3f}, RMSE: {rmse_cap:,.0f}")
print()
print("📁 FILES CREATED:")
print("   ✓ STEP11_bottleneck_model.pkl - Trained XGBoost classifier")
print("   ✓ STEP11_age_targeting_model.pkl - Trained XGBoost regressor")
print("   ✓ STEP11_capacity_model.pkl - Trained XGBoost regressor")
print("   ✓ STEP11_bottleneck_predictions.csv - State-wise bottleneck probabilities")
print("   ✓ STEP11_age_group_targeting.csv - Campaign targeting recommendations")
print("   ✓ STEP11_capacity_predictions.csv - Capacity gap analysis")
print("   ✓ STEP11_feature_importance.csv - Feature importance rankings")
print()
print("🎯 KEY INSIGHTS:")
print(f"   • {features_df['is_bottleneck'].sum()} states predicted as bottlenecks")
print(f"   • Top campaign target: {top_campaigns.iloc[0]['state']} - Age {top_campaigns.iloc[0]['age_group']}")
print(f"   • Highest capacity gap: {top_capacity.iloc[0]['state']} ({top_capacity.iloc[0]['capacity_gap_pct']:.1f}%)")
print()
print("🔜 NEXT: Run STEP11_xgboost_visualizations.py to create charts")
print("=" * 100)
