"""
Quick State Validation Check
"""
import pandas as pd
import glob
import os

# Valid states
VALID_STATES = {
    'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
    'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand',
    'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur',
    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab',
    'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura',
    'uttar pradesh', 'uttarakhand', 'west bengal',
    'andaman and nicobar islands', 'chandigarh', 'dadra and nagar haveli and daman and diu',
    'delhi', 'jammu and kashmir', 'ladakh', 'lakshadweep', 'puducherry'
}

BASE_PATH = r"E:\Aadhar UIDAI"
ENROLMENT_FOLDER = os.path.join(BASE_PATH, "api_data_aadhar_enrolment", "api_data_aadhar_enrolment")

print("Loading enrolment data...")
files = glob.glob(os.path.join(ENROLMENT_FOLDER, "*.csv"))
dfs = [pd.read_csv(f, nrows=10000) for f in files]  # Just first 10k rows for speed
df = pd.concat(dfs, ignore_index=True)

print(f"\nChecking {len(df):,} rows...")

# Get unique states
unique_states = df['state'].unique()
print(f"\nFound {len(unique_states)} unique state values:\n")

# Check each
for state in sorted(unique_states):
    state_lower = str(state).lower().strip()
    count = len(df[df['state'] == state])
    
    if state_lower in VALID_STATES:
        status = "✓ VALID"
    elif str(state).isdigit():
        status = "❌ NUMBER"
    else:
        status = "⚠️  CHECK"
    
    print(f"{status:12} | {state:40} | {count:>8,} rows")

print("\nDone!")
