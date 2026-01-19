"""
PROFESSIONAL DATA CLEANING & PREPROCESSING PIPELINE
====================================================
Created by: Experienced Data Analyst/Engineer
Purpose: UIDAI Aadhaar Hackathon - Phase 2

This script performs comprehensive data cleaning following industry best practices:
1. Data Profiling & Quality Assessment
2. Invalid Data Detection & Removal
3. Standardization (lowercase conversion, formatting)
4. Duplicate Handling
5. Feature Engineering
6. Validation & Quality Assurance

Author: Professional Data Engineering Standards
Date: January 2026
"""

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
import re

# ============================================
# CONFIGURATION
# ============================================
BASE_PATH = r"E:\Aadhar UIDAI"
PROJECT_PATH = os.path.join(BASE_PATH, "PROJECT")
OUTPUT_FOLDER = os.path.join(PROJECT_PATH, "data", "processed")
RESULTS_FOLDER = os.path.join(PROJECT_PATH, "results")

# Create folders
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Source folders
ENROLMENT_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_enrolment", "api_data_aadhar_enrolment")
BIOMETRIC_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_biometric", "api_data_aadhar_biometric")
DEMOGRAPHIC_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_demographic", "api_data_aadhar_demographic")

# ============================================
# REFERENCE DATA: VALID INDIAN STATES & UTs
# ============================================
VALID_STATES_UTS = {
    # 28 States
    'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
    'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand',
    'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur',
    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab',
    'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura',
    'uttar pradesh', 'uttarakhand', 'west bengal',
    
    # 8 Union Territories
    'andaman and nicobar islands', 'chandigarh', 
    'dadra and nagar haveli and daman and diu',
    'delhi', 'jammu and kashmir', 'ladakh', 'lakshadweep', 'puducherry'
}

print("=" * 120)
print("PROFESSIONAL DATA CLEANING & PREPROCESSING PIPELINE - UIDAI AADHAAR DATASET")
print("=" * 120)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n✓ Reference: 28 States + 8 Union Territories = 36 valid regions loaded")
print("=" * 120)

# ============================================
# CLEANING FUNCTION
# ============================================
def professional_data_cleaning(folder_path, dataset_name, columns_to_check):
    """
    Professional-grade data cleaning function
    
    Parameters:
    - folder_path: Path to CSV files
    - dataset_name: Name of dataset (for logging)
    - columns_to_check: Dict of column names and their expected data types
    
    Returns:
    - Cleaned DataFrame
    - Quality report dictionary
    """
    
    print(f"\n{'=' * 120}")
    print(f"PROCESSING: {dataset_name.upper()} DATASET")
    print(f"{'=' * 120}")
    
    # ========================================
    # STEP 1: DATA LOADING
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 1: DATA LOADING")
    print(f"{'─' * 120}")
    
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"\n✓ Found {len(csv_files)} CSV files")
    
    dataframes = []
    total_rows_before = 0
    
    for i, file in enumerate(csv_files, 1):
        file_size = os.path.getsize(file) / (1024 * 1024)
        df_temp = pd.read_csv(file)
        rows = len(df_temp)
        total_rows_before += rows
        dataframes.append(df_temp)
        print(f"  [{i}/{len(csv_files)}] {os.path.basename(file):50s} | {rows:>10,} rows | {file_size:>8.2f} MB")
    
    # Combine all files
    df = pd.concat(dataframes, ignore_index=True)
    print(f"\n✓ Combined: {len(df):,} total rows")
    
    # Quality tracking
    quality_report = {
        'initial_rows': len(df),
        'issues_found': [],
        'rows_removed': {}
    }
    
    # ========================================
    # STEP 2: STANDARDIZE TEXT (LOWERCASE)
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 2: TEXT STANDARDIZATION (Converting to Lowercase)")
    print(f"{'─' * 120}")
    
    text_columns = ['state', 'district']
    
    for col in text_columns:
        if col in df.columns:
            before_sample = df[col].iloc[0] if len(df) > 0 else None
            df[col] = df[col].str.lower().str.strip()
            after_sample = df[col].iloc[0] if len(df) > 0 else None
            print(f"\n✓ Converted '{col}' to lowercase")
            print(f"  Example: '{before_sample}' → '{after_sample}'")
    
    # ========================================
    # STEP 3: VALIDATE STATE NAMES
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 3: STATE NAME VALIDATION")
    print(f"{'─' * 120}")
    
    # Find invalid states
    unique_states = df['state'].unique()
    print(f"\n📊 Found {len(unique_states)} unique state values")
    
    invalid_states = []
    for state in unique_states:
        if pd.isna(state):
            invalid_states.append(state)
        elif state not in VALID_STATES_UTS:
            # Check if it's a number
            if str(state).replace(' ', '').replace('.', '').isdigit():
                invalid_states.append(state)
                print(f"  ⚠️  Found NUMERIC state: '{state}'")
            else:
                # Might be a typo or variant
                invalid_states.append(state)
                print(f"  ⚠️  Found INVALID state: '{state}'")
    
    if invalid_states:
        print(f"\n⚠️  REMOVING {len(df[df['state'].isin(invalid_states)]):,} rows with invalid states")
        quality_report['issues_found'].append(f"Invalid states: {len(invalid_states)}")
        quality_report['rows_removed']['invalid_states'] = len(df[df['state'].isin(invalid_states)])
        
        # Remove invalid states
        df = df[~df['state'].isin(invalid_states)]
        print(f"✓ Removed rows. Remaining: {len(df):,}")
    else:
        print(f"\n✓ All states are valid!")
    
    # Show valid states present
    valid_states_in_data = sorted([s for s in df['state'].unique() if s in VALID_STATES_UTS])
    print(f"\n✓ Valid states/UTs present: {len(valid_states_in_data)}/36")
    print(f"  States: {', '.join(valid_states_in_data[:10])}{'...' if len(valid_states_in_data) > 10 else ''}")
    
    # ========================================
    # STEP 4: VALIDATE PINCODE
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 4: PINCODE VALIDATION")
    print(f"{'─' * 120}")
    
    # Convert pincode to string
    df['pincode'] = df['pincode'].astype(str).str.strip()
    
    # Indian pincodes must be 6 digits
    invalid_pincode_mask = (df['pincode'].str.len() != 6) | (~df['pincode'].str.isdigit())
    invalid_pincode_count = invalid_pincode_mask.sum()
    
    if invalid_pincode_count > 0:
        print(f"\n⚠️  Found {invalid_pincode_count:,} rows with invalid pincodes")
        print(f"  Sample invalid pincodes: {df[invalid_pincode_mask]['pincode'].value_counts().head(5).to_dict()}")
        
        quality_report['issues_found'].append(f"Invalid pincodes: {invalid_pincode_count}")
        quality_report['rows_removed']['invalid_pincodes'] = invalid_pincode_count
        
        df = df[~invalid_pincode_mask]
        print(f"✓ Removed rows. Remaining: {len(df):,}")
    else:
        print(f"\n✓ All pincodes are valid (6-digit)")
    
    # ========================================
    # STEP 5: VALIDATE NUMERIC COLUMNS
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 5: NUMERIC COLUMN VALIDATION")
    print(f"{'─' * 120}")
    
    numeric_cols = [c for c in df.columns if c not in ['date', 'state', 'district', 'pincode']]
    
    # Check for negative values
    for col in numeric_cols:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            print(f"\n⚠️  Found {negative_count:,} negative values in '{col}'")
            quality_report['issues_found'].append(f"Negative values in {col}: {negative_count}")
            quality_report['rows_removed'][f'negative_{col}'] = negative_count
            
            df = df[df[col] >= 0]
            print(f"✓ Removed rows. Remaining: {len(df):,}")
    
    print(f"\n✓ Numeric columns validated:")
    for col in numeric_cols:
        print(f"  {col:25s} | Min: {df[col].min():>8,.0f} | Max: {df[col].max():>10,.0f} | Mean: {df[col].mean():>8,.2f}")
    
    # ========================================
    # STEP 6: DATE VALIDATION & PARSING
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 6: DATE VALIDATION & PARSING")
    print(f"{'─' * 120}")
    
    try:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        invalid_dates = df['date'].isnull().sum()
        
        if invalid_dates > 0:
            print(f"\n⚠️  Found {invalid_dates:,} invalid dates")
            quality_report['issues_found'].append(f"Invalid dates: {invalid_dates}")
            quality_report['rows_removed']['invalid_dates'] = invalid_dates
            
            df = df[df['date'].notnull()]
            print(f"✓ Removed rows. Remaining: {len(df):,}")
        
        print(f"\n✓ Date parsing successful")
        print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"  Total days: {(df['date'].max() - df['date'].min()).days}")
        
    except Exception as e:
        print(f"\n❌ Error parsing dates: {e}")
        quality_report['issues_found'].append(f"Date parsing error: {str(e)}")
    
    # ========================================
    # STEP 7: REMOVE EXACT DUPLICATES
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 7: DUPLICATE DETECTION & REMOVAL")
    print(f"{'─' * 120}")
    
    before_dedup = len(df)
    exact_duplicates = df.duplicated().sum()
    
    print(f"\n📊 Exact duplicates (all columns identical): {exact_duplicates:,} ({exact_duplicates/before_dedup*100:.4f}%)")
    
    if exact_duplicates > 0:
        # Show example
        dup_mask = df.duplicated(keep=False)
        sample_dup = df[dup_mask].head(2)
        if len(sample_dup) > 0:
            print(f"\n  Example of duplicate:")
            print(sample_dup)
        
        df = df.drop_duplicates()
        removed = before_dedup - len(df)
        quality_report['rows_removed']['exact_duplicates'] = removed
        print(f"\n✓ Removed {removed:,} exact duplicates")
        print(f"✓ Remaining rows: {len(df):,}")
    else:
        print(f"\n✓ No exact duplicates found")
    
    # ========================================
    # STEP 8: FEATURE ENGINEERING
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 8: FEATURE ENGINEERING")
    print(f"{'─' * 120}")
    
    # Add calculated columns based on dataset type
    if dataset_name == "Enrolment":
        df['total_enrolments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
        print(f"\n✓ Added 'total_enrolments' column")
        print(f"  Total enrolments in dataset: {df['total_enrolments'].sum():,}")
        
    elif dataset_name == "Biometric":
        df['total_bio_updates'] = df['bio_age_5_17'] + df['bio_age_17_']
        print(f"\n✓ Added 'total_bio_updates' column")
        print(f"  Total biometric updates: {df['total_bio_updates'].sum():,}")
        
    elif dataset_name == "Demographic":
        df['total_demo_updates'] = df['demo_age_5_17'] + df['demo_age_17_']
        print(f"\n✓ Added 'total_demo_updates' column")
        print(f"  Total demographic updates: {df['total_demo_updates'].sum():,}")
    
    # Add time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%B')
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['day_of_month'] = df['date'].dt.day
    
    print(f"\n✓ Added time-based features:")
    print(f"  - year, month, month_name, quarter")
    print(f"  - day_of_week, week_of_year, day_of_month")
    
    # ========================================
    # STEP 9: FINAL QUALITY CHECKS
    # ========================================
    print(f"\n{'─' * 120}")
    print("STEP 9: FINAL QUALITY ASSURANCE")
    print(f"{'─' * 120}")
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        print(f"\n⚠️  Missing values found:")
        for col in df.columns:
            if missing_values[col] > 0:
                print(f"  {col}: {missing_values[col]:,} ({missing_values[col]/len(df)*100:.2f}%)")
    else:
        print(f"\n✓ No missing values")
    
    # Final summary
    quality_report['final_rows'] = len(df)
    quality_report['total_removed'] = quality_report['initial_rows'] - quality_report['final_rows']
    quality_report['data_retained_percent'] = (quality_report['final_rows'] / quality_report['initial_rows']) * 100
    
    print(f"\n{'─' * 120}")
    print(f"CLEANING SUMMARY FOR {dataset_name.upper()}")
    print(f"{'─' * 120}")
    print(f"\n  Initial rows:      {quality_report['initial_rows']:>12,}")
    print(f"  Final rows:        {quality_report['final_rows']:>12,}")
    print(f"  Rows removed:      {quality_report['total_removed']:>12,}")
    print(f"  Data retained:     {quality_report['data_retained_percent']:>11.2f}%")
    print(f"\n  Unique states:     {df['state'].nunique():>12}")
    print(f"  Unique districts:  {df['district'].nunique():>12}")
    print(f"  Unique pincodes:   {df['pincode'].nunique():>12}")
    
    return df, quality_report

# ============================================
# PROCESS ALL DATASETS
# ============================================

# Track all quality reports
all_quality_reports = {}

# Process Enrolment
df_enrol, qr_enrol = professional_data_cleaning(
    ENROLMENT_FOLDER, 
    "Enrolment",
    {'age_0_5': int, 'age_5_17': int, 'age_18_greater': int}
)
all_quality_reports['Enrolment'] = qr_enrol

# Process Biometric
df_bio, qr_bio = professional_data_cleaning(
    BIOMETRIC_FOLDER,
    "Biometric",
    {'bio_age_5_17': int, 'bio_age_17_': int}
)
all_quality_reports['Biometric'] = qr_bio

# Process Demographic
df_demo, qr_demo = professional_data_cleaning(
    DEMOGRAPHIC_FOLDER,
    "Demographic",
    {'demo_age_5_17': int, 'demo_age_17_': int}
)
all_quality_reports['Demographic'] = qr_demo

# ============================================
# SAVE CLEANED DATASETS
# ============================================
print(f"\n{'=' * 120}")
print("SAVING CLEANED DATASETS")
print(f"{'=' * 120}")

# Save Enrolment
enrol_path = os.path.join(OUTPUT_FOLDER, "cleaned_enrolment.csv")
df_enrol.to_csv(enrol_path, index=False)
enrol_size = os.path.getsize(enrol_path) / (1024 * 1024)
print(f"\n✓ Saved: cleaned_enrolment.csv")
print(f"  Rows: {len(df_enrol):,} | Size: {enrol_size:.2f} MB")

# Save Biometric
bio_path = os.path.join(OUTPUT_FOLDER, "cleaned_biometric.csv")
df_bio.to_csv(bio_path, index=False)
bio_size = os.path.getsize(bio_path) / (1024 * 1024)
print(f"\n✓ Saved: cleaned_biometric.csv")
print(f"  Rows: {len(df_bio):,} | Size: {bio_size:.2f} MB")

# Save Demographic
demo_path = os.path.join(OUTPUT_FOLDER, "cleaned_demographic.csv")
df_demo.to_csv(demo_path, index=False)
demo_size = os.path.getsize(demo_path) / (1024 * 1024)
print(f"\n✓ Saved: cleaned_demographic.csv")
print(f"  Rows: {len(df_demo):,} | Size: {demo_size:.2f} MB")

# ============================================
# GENERATE QUALITY REPORT
# ============================================
print(f"\n{'=' * 120}")
print("GENERATING DATA QUALITY REPORT")
print(f"{'=' * 120}")

summary_data = {
    'Dataset': ['Enrolment', 'Biometric', 'Demographic', 'TOTAL'],
    'Initial_Rows': [
        qr_enrol['initial_rows'],
        qr_bio['initial_rows'],
        qr_demo['initial_rows'],
        qr_enrol['initial_rows'] + qr_bio['initial_rows'] + qr_demo['initial_rows']
    ],
    'Final_Rows': [
        qr_enrol['final_rows'],
        qr_bio['final_rows'],
        qr_demo['final_rows'],
        qr_enrol['final_rows'] + qr_bio['final_rows'] + qr_demo['final_rows']
    ],
    'Rows_Removed': [
        qr_enrol['total_removed'],
        qr_bio['total_removed'],
        qr_demo['total_removed'],
        qr_enrol['total_removed'] + qr_bio['total_removed'] + qr_demo['total_removed']
    ],
    'Data_Retained_%': [
        round(qr_enrol['data_retained_percent'], 2),
        round(qr_bio['data_retained_percent'], 2),
        round(qr_demo['data_retained_percent'], 2),
        round(((qr_enrol['final_rows'] + qr_bio['final_rows'] + qr_demo['final_rows']) / 
               (qr_enrol['initial_rows'] + qr_bio['initial_rows'] + qr_demo['initial_rows'])) * 100, 2)
    ],
    'Unique_States': [
        df_enrol['state'].nunique(),
        df_bio['state'].nunique(),
        df_demo['state'].nunique(),
        '-'
    ]
}

summary_df = pd.DataFrame(summary_data)
report_path = os.path.join(RESULTS_FOLDER, 'data_cleaning_quality_report.csv')
summary_df.to_csv(report_path, index=False)

print(f"\n✓ Quality Report:")
print(summary_df.to_string(index=False))

print(f"\n✓ Saved detailed report: {report_path}")

# ============================================
# FINAL SUMMARY
# ============================================
print(f"\n{'=' * 120}")
print("✅ PROFESSIONAL DATA CLEANING COMPLETE!")
print(f"{'=' * 120}")

print(f"\n📊 OVERALL STATISTICS:")
print(f"  Total rows processed:  {summary_data['Initial_Rows'][-1]:>12,}")
print(f"  Total rows cleaned:    {summary_data['Final_Rows'][-1]:>12,}")
print(f"  Total rows removed:    {summary_data['Rows_Removed'][-1]:>12,}")
print(f"  Overall data retained: {summary_data['Data_Retained_%'][-1]:>11.2f}%")

print(f"\n📁 OUTPUT FILES:")
print(f"  Cleaned data:  {OUTPUT_FOLDER}")
print(f"  Quality report: {RESULTS_FOLDER}")

print(f"\n🎯 DATA QUALITY IMPROVEMENTS:")
print(f"  ✓ All text converted to lowercase")
print(f"  ✓ Invalid states removed (numbers, typos)")
print(f"  ✓ Invalid pincodes removed (non-6-digit)")
print(f"  ✓ Negative values removed")
print(f"  ✓ Invalid dates removed")
print(f"  ✓ Exact duplicates removed")
print(f"  ✓ Time-based features added")
print(f"  ✓ Calculated totals added")

print(f"\n🚀 READY FOR ANALYSIS!")
print(f"  Next step: Run exploratory analysis and visualizations")

print(f"\n{'=' * 120}")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'=' * 120}")
