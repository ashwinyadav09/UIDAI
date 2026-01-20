"""
FINAL INTELLIGENT DATA CLEANING WITH COMPREHENSIVE ERROR HANDLING
==================================================================
This script:
1. Fixes ALL typos and spelling variations (even single letter differences)
2. Handles cities/districts wrongly placed in state column
3. Creates "unknown" category instead of deleting unclear data
4. Uses fuzzy matching for close matches
5. Preserves maximum data while maintaining quality
"""

import pandas as pd


import numpy as np
import glob
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the PROJECT directory (parent of src)
PROJECT_PATH = os.path.dirname(SCRIPT_DIR)

from datetime import datetime
import re
from difflib import get_close_matches

# ============================================
# CONFIGURATION
# ============================================
# Get the base path (parent of PROJECT)
BASE_PATH = os.path.dirname(PROJECT_PATH)

OUTPUT_FOLDER = os.path.join(PROJECT_PATH, "data", "processed")
RESULTS_FOLDER = os.path.join(PROJECT_PATH, "results")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

ENROLMENT_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_enrolment", "api_data_aadhar_enrolment")
BIOMETRIC_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_biometric", "api_data_aadhar_biometric")
DEMOGRAPHIC_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_demographic", "api_data_aadhar_demographic")

# ============================================
# VALID STATES & UTs
# ============================================
VALID_STATES_UTS = {
    'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
    'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand',
    'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur',
    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab',
    'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura',
    'uttar pradesh', 'uttarakhand', 'west bengal',
    'andaman and nicobar islands', 'chandigarh', 
    'dadra and nagar haveli and daman and diu',
    'delhi', 'jammu and kashmir', 'ladakh', 'lakshadweep', 'puducherry'
}

# ============================================
# COMPREHENSIVE CORRECTION MAPPING
# ============================================
STATE_NAME_CORRECTIONS = {
    # Historical names
    'orissa': 'odisha',
    'pondicherry': 'puducherry',
    'uttaranchal': 'uttarakhand',
    
    # Typos - spelling variations
    'chhatisgarh': 'chhattisgarh',  # Single 't'
    'chattisgarh': 'chhattisgarh',
    'chhatisgrah': 'chhattisgarh',
    'west bangal': 'west bengal',
    'west bengli': 'west bengal',
    'westbengal': 'west bengal',
    'west  bengal': 'west bengal',
    
    # Format variations with &
    'andaman & nicobar islands': 'andaman and nicobar islands',
    'jammu & kashmir': 'jammu and kashmir',
    'dadra & nagar haveli': 'dadra and nagar haveli and daman and diu',
    'daman & diu': 'dadra and nagar haveli and daman and diu',
    
    # UT consolidations
    'dadra and nagar haveli': 'dadra and nagar haveli and daman and diu',
    'daman and diu': 'dadra and nagar haveli and daman and diu',
    
    # Extra words
    'the dadra and nagar haveli and daman and diu': 'dadra and nagar haveli and daman and diu',
    'nct of delhi': 'delhi',
    'new delhi': 'delhi',
    
    # Other variations
    'pondichery': 'puducherry',
    'puduchery': 'puducherry',
}

# ============================================
# CITY TO STATE MAPPING (for wrongly placed cities)
# ============================================
CITY_TO_STATE_MAPPING = {
    # Major cities
    'darbhanga': 'bihar',
    'jaipur': 'rajasthan',
    'nagpur': 'maharashtra',
    'madanapalle': 'andhra pradesh',
    'puttenahalli': 'karnataka',
    'balanagar': 'telangana',
    'raja annamalai puram': 'tamil nadu',
    
    # More cities (can be expanded)
    'bangalore': 'karnataka',
    'bengaluru': 'karnataka',
    'mumbai': 'maharashtra',
    'chennai': 'tamil nadu',
    'kolkata': 'west bengal',
    'hyderabad': 'telangana',
    'pune': 'maharashtra',
    'ahmedabad': 'gujarat',
    'lucknow': 'uttar pradesh',
    'patna': 'bihar',
    'bhopal': 'madhya pradesh',
    'chandigarh': 'chandigarh',  # UT
}

print("=" * 120)
print("FINAL INTELLIGENT DATA CLEANING WITH COMPREHENSIVE ERROR HANDLING")
print("=" * 120)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n✓ Reference: 28 States + 8 Union Territories = 36 valid regions")
print(f"✓ Loaded {len(STATE_NAME_CORRECTIONS)} direct corrections")
print(f"✓ Loaded {len(CITY_TO_STATE_MAPPING)} city→state mappings")
print("=" * 120)

# ============================================
# INTELLIGENT STATE NAME CLEANING
# ============================================
def intelligent_state_cleaning(state_name, valid_states):
    """
    Intelligent state name cleaning with multiple strategies:
    1. Direct correction mapping
    2. City to state mapping
    3. Fuzzy matching for typos
    4. Unknown category for unclear cases
    """
    if pd.isna(state_name):
        return 'unknown'
    
    # Convert to lowercase and clean
    state = str(state_name).lower().strip()
    state = re.sub(r'\s+', ' ', state)
    
    # Check if it's a number
    if state.replace(' ', '').replace('.', '').isdigit():
        return 'unknown'
    
    # Strategy 1: Direct correction mapping
    if state in STATE_NAME_CORRECTIONS:
        return STATE_NAME_CORRECTIONS[state]
    
    # Strategy 2: Already valid
    if state in valid_states:
        return state
    
    # Strategy 3: City to state mapping
    if state in CITY_TO_STATE_MAPPING:
        corrected = CITY_TO_STATE_MAPPING[state]
        print(f"      🔧 CITY DETECTED: '{state}' → '{corrected}'")
        return corrected
    
    # Strategy 4: Fuzzy matching (for typos)
    # Find close matches (similarity threshold = 0.85)
    close_matches = get_close_matches(state, valid_states, n=1, cutoff=0.85)
    if close_matches:
        corrected = close_matches[0]
        print(f"      🔧 FUZZY MATCH: '{state}' → '{corrected}'")
        return corrected
    
    # Strategy 5: If nothing works, mark as unknown
    print(f"      ⚠️  UNKNOWN: '{state}' → 'unknown' (will be kept for review)")
    return 'unknown'

# ============================================
# CLEANING FUNCTION
# ============================================
def intelligent_data_cleaning(folder_path, dataset_name):
    """
    Intelligent data cleaning with comprehensive error handling
    """
    
    print(f"\n{'=' * 120}")
    print(f"PROCESSING: {dataset_name.upper()} DATASET")
    print(f"{'=' * 120}")
    
    # STEP 1: LOAD DATA
    print(f"\n{'─' * 120}")
    print("STEP 1: DATA LOADING")
    print(f"{'─' * 120}")
    
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"\n✓ Found {len(csv_files)} CSV files")
    
    dataframes = []
    for i, file in enumerate(csv_files, 1):
        file_size = os.path.getsize(file) / (1024 * 1024)
        df_temp = pd.read_csv(file)
        rows = len(df_temp)
        dataframes.append(df_temp)
        print(f"  [{i}/{len(csv_files)}] {os.path.basename(file):50s} | {rows:>10,} rows | {file_size:>8.2f} MB")
    
    df = pd.concat(dataframes, ignore_index=True)
    print(f"\n✓ Combined: {len(df):,} total rows")
    
    quality_report = {
        'initial_rows': len(df),
        'corrections': {},
        'unknowns': 0
    }
    
    # STEP 2: INTELLIGENT STATE CLEANING
    print(f"\n{'─' * 120}")
    print("STEP 2: INTELLIGENT STATE NAME CLEANING")
    print(f"{'─' * 120}")
    
    unique_before = df['state'].nunique()
    print(f"\n📊 Unique values BEFORE: {unique_before}")
    
    df['state_original'] = df['state']
    print(f"\n🔧 Applying intelligent corrections...")
    df['state'] = df['state'].apply(lambda x: intelligent_state_cleaning(x, VALID_STATES_UTS))
    
    unique_after = df['state'].nunique()
    print(f"\n📊 Unique values AFTER: {unique_after}")
    
    # Count unknowns
    unknown_count = (df['state'] == 'unknown').sum()
    quality_report['unknowns'] = unknown_count
    
    if unknown_count > 0:
        print(f"\n📋 Records marked as 'unknown': {unknown_count:,}")
        print(f"   These are kept in dataset for manual review")
        print(f"   Check 'unknown_state_records.csv' for details")
    
    # Show corrections summary
    corrections_made = {}
    for idx, row in df.iterrows():
        if pd.notna(row['state_original']) and row['state_original'].lower().strip() != row['state']:
            orig = row['state_original']
            corr = row['state']
            key = f"{orig} → {corr}"
            corrections_made[key] = corrections_made.get(key, 0) + 1
    
    if corrections_made:
        print(f"\n✅ CORRECTIONS SUMMARY:")
        for correction, count in sorted(corrections_made.items(), key=lambda x: x[1], reverse=True)[:30]:
            print(f"   {correction:70s} : {count:>8,} rows")
    
    # Show final state distribution
    print(f"\n📊 FINAL STATE DISTRIBUTION:")
    state_counts = df['state'].value_counts()
    for state, count in state_counts.items():
        if state == 'unknown':
            print(f"   {'unknown (needs review)':45s} : {count:>10,} rows ⚠️")
        else:
            print(f"   {state:45s} : {count:>10,} rows")
    
    # STEP 3: CLEAN DISTRICT
    print(f"\n{'─' * 120}")
    print("STEP 3: DISTRICT STANDARDIZATION")
    print(f"{'─' * 120}")
    
    df['district'] = df['district'].str.lower().str.strip()
    df['district'] = df['district'].apply(lambda x: re.sub(r'\s+', ' ', str(x)) if pd.notna(x) else x)
    print(f"\n✓ Standardized {df['district'].nunique()} unique districts")
    
    # STEP 4: VALIDATE PINCODE
    print(f"\n{'─' * 120}")
    print("STEP 4: PINCODE VALIDATION")
    print(f"{'─' * 120}")
    
    df['pincode'] = df['pincode'].astype(str).str.strip()
    invalid_pincode = (df['pincode'].str.len() != 6) | (~df['pincode'].str.isdigit())
    invalid_count = invalid_pincode.sum()
    
    if invalid_count > 0:
        print(f"\n⚠️  Found {invalid_count:,} invalid pincodes - REMOVING")
        df = df[~invalid_pincode]
        print(f"✓ Remaining: {len(df):,}")
    else:
        print(f"\n✓ All pincodes valid")
    
    # STEP 5: VALIDATE NUMERIC COLUMNS
    print(f"\n{'─' * 120}")
    print("STEP 5: NUMERIC VALIDATION")
    print(f"{'─' * 120}")
    
    numeric_cols = [c for c in df.columns if c not in ['date', 'state', 'district', 'pincode', 'state_original']]
    
    for col in numeric_cols:
        negative = (df[col] < 0).sum()
        if negative > 0:
            print(f"⚠️  Removing {negative:,} rows with negative {col}")
            df = df[df[col] >= 0]
    
    print(f"\n✓ Remaining: {len(df):,}")
    
    # STEP 6: DATE PARSING
    print(f"\n{'─' * 120}")
    print("STEP 6: DATE PARSING")
    print(f"{'─' * 120}")
    
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    invalid_dates = df['date'].isnull().sum()
    
    if invalid_dates > 0:
        print(f"⚠️  Removing {invalid_dates:,} invalid dates")
        df = df[df['date'].notnull()]
    
    print(f"✓ Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    # STEP 7: REMOVE DUPLICATES
    print(f"\n{'─' * 120}")
    print("STEP 7: DUPLICATE REMOVAL")
    print(f"{'─' * 120}")
    
    df_clean = df.drop(columns=['state_original'], errors='ignore')
    dupes = df_clean.duplicated().sum()
    
    if dupes > 0:
        print(f"⚠️  Removing {dupes:,} exact duplicates")
        df = df_clean.drop_duplicates()
    else:
        df = df_clean
    
    print(f"✓ Final rows: {len(df):,}")
    
    # STEP 8: ADD FEATURES
    print(f"\n{'─' * 120}")
    print("STEP 8: FEATURE ENGINEERING")
    print(f"{'─' * 120}")
    
    if dataset_name == "Enrolment":
        df['total_enrolments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
        print(f"✓ Added total_enrolments: {df['total_enrolments'].sum():,}")
    elif dataset_name == "Biometric":
        df['total_bio_updates'] = df['bio_age_5_17'] + df['bio_age_17_']
        print(f"✓ Added total_bio_updates: {df['total_bio_updates'].sum():,}")
    elif dataset_name == "Demographic":
        df['total_demo_updates'] = df['demo_age_5_17'] + df['demo_age_17_']
        print(f"✓ Added total_demo_updates: {df['total_demo_updates'].sum():,}")
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%B')
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    print(f"✓ Added time features")
    
    quality_report['final_rows'] = len(df)
    quality_report['data_retained'] = (len(df) / quality_report['initial_rows']) * 100
    
    return df, quality_report

# ============================================
# PROCESS ALL DATASETS
# ============================================

all_reports = {}

df_enrol, qr_enrol = intelligent_data_cleaning(ENROLMENT_FOLDER, "Enrolment")
all_reports['Enrolment'] = qr_enrol

df_bio, qr_bio = intelligent_data_cleaning(BIOMETRIC_FOLDER, "Biometric")
all_reports['Biometric'] = qr_bio

df_demo, qr_demo = intelligent_data_cleaning(DEMOGRAPHIC_FOLDER, "Demographic")
all_reports['Demographic'] = qr_demo

# ============================================
# SAVE CLEANED DATA
# ============================================
print(f"\n{'=' * 120}")
print("SAVING CLEANED DATA")
print(f"{'=' * 120}")

df_enrol.to_csv(os.path.join(OUTPUT_FOLDER, "cleaned_enrolment.csv"), index=False)
print(f"✓ Saved cleaned_enrolment.csv ({len(df_enrol):,} rows)")

df_bio.to_csv(os.path.join(OUTPUT_FOLDER, "cleaned_biometric.csv"), index=False)
print(f"✓ Saved cleaned_biometric.csv ({len(df_bio):,} rows)")

df_demo.to_csv(os.path.join(OUTPUT_FOLDER, "cleaned_demographic.csv"), index=False)
print(f"✓ Saved cleaned_demographic.csv ({len(df_demo):,} rows)")

# Save unknown records for review
print(f"\n{'─' * 120}")
print("SAVING UNKNOWN RECORDS FOR MANUAL REVIEW")
print(f"{'─' * 120}")

unknown_enrol = df_enrol[df_enrol['state'] == 'unknown']
unknown_bio = df_bio[df_bio['state'] == 'unknown']
unknown_demo = df_demo[df_demo['state'] == 'unknown']

if len(unknown_enrol) > 0 or len(unknown_bio) > 0 or len(unknown_demo) > 0:
    with pd.ExcelWriter(os.path.join(RESULTS_FOLDER, 'unknown_records_for_review.xlsx')) as writer:
        if len(unknown_enrol) > 0:
            unknown_enrol.to_excel(writer, sheet_name='Enrolment', index=False)
            print(f"  Enrolment unknowns: {len(unknown_enrol):,} rows")
        if len(unknown_bio) > 0:
            unknown_bio.to_excel(writer, sheet_name='Biometric', index=False)
            print(f"  Biometric unknowns: {len(unknown_bio):,} rows")
        if len(unknown_demo) > 0:
            unknown_demo.to_excel(writer, sheet_name='Demographic', index=False)
            print(f"  Demographic unknowns: {len(unknown_demo):,} rows")
    print(f"\n✓ Saved: unknown_records_for_review.xlsx")

# ============================================
# FINAL REPORT
# ============================================
print(f"\n{'=' * 120}")
print("✅ INTELLIGENT CLEANING COMPLETE!")
print(f"{'=' * 120}")

total_initial = qr_enrol['initial_rows'] + qr_bio['initial_rows'] + qr_demo['initial_rows']
total_final = qr_enrol['final_rows'] + qr_bio['final_rows'] + qr_demo['final_rows']
total_unknown = qr_enrol['unknowns'] + qr_bio['unknowns'] + qr_demo['unknowns']

print(f"\n📊 OVERALL SUMMARY:")
print(f"  Initial rows:     {total_initial:>12,}")
print(f"  Final rows:       {total_final:>12,}")
print(f"  Data retained:    {total_final/total_initial*100:>11.2f}%")
print(f"  Unknown records:  {total_unknown:>12,} (kept for review)")

print(f"\n✅ KEY IMPROVEMENTS:")
print(f"  ✓ Typo corrections (chhatisgarh→chhattisgarh, etc.)")
print(f"  ✓ City→State mapping (jaipur→rajasthan, etc.)")
print(f"  ✓ Fuzzy matching for close typos")
print(f"  ✓ Unknown category (no data loss)")
print(f"  ✓ Maximum data preservation")

print(f"\n{'=' * 120}")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'=' * 120}")
