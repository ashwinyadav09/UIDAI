"""
DEEP DATA QUALITY INVESTIGATION - Professional Analysis
========================================================
As an experienced Data Analyst/Engineer, I will:
1. Identify ALL data quality issues
2. Create detailed profiling report
3. Identify valid states/UTs (28 states + 8 UTs in India)
4. Find invalid entries (numbers, typos, etc.)
5. Check all data consistency issues
"""

import pandas as pd
import numpy as np
import glob
import os
import re
from collections import Counter

print("=" * 100)
print("PROFESSIONAL DATA QUALITY INVESTIGATION - UIDAI AADHAAR DATASET")
print("=" * 100)

BASE_PATH = r"E:\Aadhar UIDAI"
ENROLMENT_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_enrolment", "api_data_aadhar_enrolment")
BIOMETRIC_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_biometric", "api_data_aadhar_biometric")
DEMOGRAPHIC_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_demographic", "api_data_aadhar_demographic")

# ============================================
# REFERENCE: VALID INDIAN STATES AND UTs
# ============================================
VALID_STATES = {
    # 28 States (lowercase for matching)
    'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
    'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand',
    'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur',
    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab',
    'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura',
    'uttar pradesh', 'uttarakhand', 'west bengal',
    
    # 8 Union Territories (lowercase for matching)
    'andaman and nicobar islands', 'chandigarh', 'dadra and nagar haveli and daman and diu',
    'delhi', 'jammu and kashmir', 'ladakh', 'lakshadweep', 'puducherry'
}

print("\n✓ Loaded reference: 28 States + 8 Union Territories = 36 valid regions")

# ============================================
# FUNCTION: COMPREHENSIVE DATA ANALYSIS
# ============================================
def analyze_dataset(folder_path, dataset_name):
    """
    Perform deep analysis on a dataset
    """
    print(f"\n{'=' * 100}")
    print(f"ANALYZING {dataset_name.upper()} DATASET")
    print(f"{'=' * 100}")
    
    # Load all files
    files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"\n📂 Found {len(files)} files")
    
    dfs = []
    for f in files:
        dfs.append(pd.read_csv(f))
    
    df = pd.concat(dfs, ignore_index=True)
    print(f"✓ Loaded {len(df):,} total rows")
    
    # ========================================
    # ISSUE 1: CHECK STATE NAMES
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 1: STATE NAME VALIDATION")
    print(f"{'─' * 100}")
    
    unique_states = df['state'].unique()
    print(f"\n📊 Found {len(unique_states)} unique state values")
    
    # Convert to lowercase for comparison
    df['state_lower'] = df['state'].str.lower().str.strip()
    
    # Find invalid states
    invalid_states = []
    for state in df['state_lower'].unique():
        if pd.isna(state):
            invalid_states.append(('NULL/NaN', state))
        elif state not in VALID_STATES:
            # Check if it's a number
            if state.replace(' ', '').isdigit():
                invalid_states.append(('NUMBER', state))
            else:
                invalid_states.append(('INVALID', state))
    
    if invalid_states:
        print(f"\n⚠️  FOUND {len(invalid_states)} INVALID STATE ENTRIES:")
        print(f"\n{'Type':<15} {'Invalid Value':<30} {'Count':<10}")
        print(f"{'-'*60}")
        
        for issue_type, state_val in invalid_states:
            count = len(df[df['state_lower'] == state_val])
            print(f"{issue_type:<15} {str(state_val):<30} {count:>10,}")
    else:
        print("\n✓ All state names are valid!")
    
    # Show valid states present in data
    valid_states_present = [s for s in df['state_lower'].unique() if s in VALID_STATES]
    print(f"\n✓ Valid states present in data: {len(valid_states_present)}/36")
    
    # ========================================
    # ISSUE 2: CHECK CASE CONSISTENCY
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 2: CASE CONSISTENCY")
    print(f"{'─' * 100}")
    
    # Check if all are lowercase, uppercase, or mixed
    case_analysis = {
        'All Lowercase': df['state'].str.islower().sum(),
        'All Uppercase': df['state'].str.isupper().sum(),
        'Title Case': (df['state'].str.istitle()).sum(),
        'Mixed Case': len(df) - df['state'].str.islower().sum() - df['state'].str.isupper().sum() - df['state'].str.istitle().sum()
    }
    
    print("\nCase distribution:")
    for case_type, count in case_analysis.items():
        if count > 0:
            print(f"  {case_type}: {count:,} rows ({count/len(df)*100:.2f}%)")
    
    # ========================================
    # ISSUE 3: CHECK DISTRICT NAMES
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 3: DISTRICT VALIDATION")
    print(f"{'─' * 100}")
    
    # Check for numeric districts
    df['district_lower'] = df['district'].str.lower().str.strip()
    numeric_districts = df['district_lower'].apply(lambda x: str(x).replace(' ', '').isdigit() if pd.notna(x) else False)
    
    if numeric_districts.sum() > 0:
        print(f"\n⚠️  FOUND {numeric_districts.sum():,} rows with NUMERIC district names")
        print(f"\nSample numeric districts:")
        print(df[numeric_districts]['district'].value_counts().head(10))
    else:
        print("\n✓ No numeric district names found")
    
    # Check for special characters
    special_char_pattern = re.compile(r'[^a-zA-Z\s]')
    districts_with_special = df['district'].apply(lambda x: bool(special_char_pattern.search(str(x))) if pd.notna(x) else False)
    
    if districts_with_special.sum() > 0:
        print(f"\n⚠️  FOUND {districts_with_special.sum():,} rows with special characters in district")
    
    # ========================================
    # ISSUE 4: CHECK PINCODE VALIDITY
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 4: PINCODE VALIDATION")
    print(f"{'─' * 100}")
    
    # Indian pincodes are 6-digit numbers
    df['pincode_str'] = df['pincode'].astype(str).str.strip()
    
    # Check pincode length
    invalid_pincode_length = df['pincode_str'].str.len() != 6
    print(f"\nPincodes with invalid length (not 6 digits): {invalid_pincode_length.sum():,}")
    
    # Check if all digits
    invalid_pincode_format = ~df['pincode_str'].str.isdigit()
    print(f"Pincodes with non-numeric characters: {invalid_pincode_format.sum():,}")
    
    # Show sample invalid pincodes
    if (invalid_pincode_length | invalid_pincode_format).sum() > 0:
        print(f"\nSample invalid pincodes:")
        print(df[invalid_pincode_length | invalid_pincode_format]['pincode'].value_counts().head(10))
    
    # ========================================
    # ISSUE 5: CHECK NUMERIC COLUMNS
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 5: NUMERIC COLUMN VALIDATION")
    print(f"{'─' * 100}")
    
    numeric_cols = [c for c in df.columns if c not in ['date', 'state', 'district', 'pincode', 'state_lower', 'district_lower', 'pincode_str']]
    
    for col in numeric_cols:
        print(f"\n{col}:")
        print(f"  Data type: {df[col].dtype}")
        print(f"  Missing values: {df[col].isnull().sum():,}")
        print(f"  Negative values: {(df[col] < 0).sum():,}")
        print(f"  Zero values: {(df[col] == 0).sum():,}")
        print(f"  Min: {df[col].min()}, Max: {df[col].max()}, Mean: {df[col].mean():.2f}")
    
    # ========================================
    # ISSUE 6: CHECK DATE FORMAT
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 6: DATE VALIDATION")
    print(f"{'─' * 100}")
    
    print(f"\nSample dates: {df['date'].head(10).tolist()}")
    
    try:
        df['date_parsed'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        invalid_dates = df['date_parsed'].isnull().sum()
        
        if invalid_dates > 0:
            print(f"\n⚠️  FOUND {invalid_dates:,} invalid dates")
        else:
            print(f"\n✓ All dates are valid")
            print(f"  Date range: {df['date_parsed'].min()} to {df['date_parsed'].max()}")
            print(f"  Total days: {(df['date_parsed'].max() - df['date_parsed'].min()).days}")
    except Exception as e:
        print(f"\n❌ Error parsing dates: {e}")
    
    # ========================================
    # ISSUE 7: CHECK FOR DUPLICATES
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 7: DUPLICATE DETECTION")
    print(f"{'─' * 100}")
    
    exact_dupes = df.duplicated().sum()
    print(f"\nExact duplicates (all columns): {exact_dupes:,} ({exact_dupes/len(df)*100:.4f}%)")
    
    # ========================================
    # ISSUE 8: MISSING VALUES
    # ========================================
    print(f"\n{'─' * 100}")
    print("ISSUE 8: MISSING VALUE ANALYSIS")
    print(f"{'─' * 100}")
    
    print(f"\nMissing values per column:")
    missing = df.isnull().sum()
    for col in df.columns:
        if missing[col] > 0:
            print(f"  {col}: {missing[col]:,} ({missing[col]/len(df)*100:.2f}%)")
    
    if missing.sum() == 0:
        print(f"  ✓ No missing values!")
    
    return df

# ============================================
# ANALYZE ALL DATASETS
# ============================================

print("\n" + "=" * 100)
print("STARTING COMPREHENSIVE ANALYSIS")
print("=" * 100)

# Analyze Enrolment
df_enrol = analyze_dataset(ENROLMENT_FOLDER, "ENROLMENT")

# Analyze Biometric
df_bio = analyze_dataset(BIOMETRIC_FOLDER, "BIOMETRIC")

# Analyze Demographic
df_demo = analyze_dataset(DEMOGRAPHIC_FOLDER, "DEMOGRAPHIC")

# ============================================
# SUMMARY REPORT
# ============================================
print("\n" + "=" * 100)
print("COMPREHENSIVE DATA QUALITY SUMMARY")
print("=" * 100)

print(f"\n📊 DATASET SIZES:")
print(f"  Enrolment:   {len(df_enrol):>12,} rows")
print(f"  Biometric:   {len(df_bio):>12,} rows")
print(f"  Demographic: {len(df_demo):>12,} rows")
print(f"  TOTAL:       {len(df_enrol) + len(df_bio) + len(df_demo):>12,} rows")

# Save detailed report
results_folder = r"E:\Aadhar UIDAI\PROJECT\results"
os.makedirs(results_folder, exist_ok=True)

# Create summary
summary_data = {
    'Dataset': ['Enrolment', 'Biometric', 'Demographic'],
    'Total_Rows': [len(df_enrol), len(df_bio), len(df_demo)],
    'Unique_States': [
        df_enrol['state_lower'].nunique(),
        df_bio['state_lower'].nunique() if 'state_lower' in df_bio.columns else 0,
        df_demo['state_lower'].nunique() if 'state_lower' in df_demo.columns else 0
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(os.path.join(results_folder, 'initial_data_quality_report.csv'), index=False)

print(f"\n✓ Detailed report saved to: results/initial_data_quality_report.csv")
print("\n" + "=" * 100)
print("ANALYSIS COMPLETE - READY FOR CLEANING DECISIONS")
print("=" * 100)
