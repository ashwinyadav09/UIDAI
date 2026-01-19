import pandas as pd

# Load the state summary
df = pd.read_csv('../results/STEP6_state_summary.csv')

print("=" * 80)
print("STEP 6 RESULTS SUMMARY")
print("=" * 80)
print()

print(f"Total states analyzed: {len(df)}")
print()

print("TOP 10 STATES BY TOTAL ENROLMENTS:")
print("-" * 80)
top10 = df.nlargest(10, 'total_enrolments')
for i, row in enumerate(top10.itertuples(), 1):
    print(f"{i:2d}. {row.state:40s} - {row.total_enrolments:>12,.0f} enrolments")
print()

print("NATIONAL AVERAGES:")
print("-" * 80)
print(f"Biometric Update Rate:   {df['bio_update_rate'].mean():>8.2f}%")
print(f"Demographic Update Rate: {df['demo_update_rate'].mean():>8.2f}%")
print()

print("TOP 5 STATES - BIOMETRIC UPDATE RATE:")
print("-" * 80)
top_bio = df.nlargest(5, 'bio_update_rate')
for i, row in enumerate(top_bio.itertuples(), 1):
    print(f"{i}. {row.state:40s} - {row.bio_update_rate:>8.2f}%")
print()

print("TOP 5 STATES - DEMOGRAPHIC UPDATE RATE:")
print("-" * 80)
top_demo = df.nlargest(5, 'demo_update_rate')
for i, row in enumerate(top_demo.itertuples(), 1):
    print(f"{i}. {row.state:40s} - {row.demo_update_rate:>8.2f}%")
print()

print("BOTTOM 5 STATES - BIOMETRIC UPDATE RATE (Excluding Unknown):")
print("-" * 80)
df_clean = df[df['state'] != 'unknown']
bottom_bio = df_clean.nsmallest(5, 'bio_update_rate')
for i, row in enumerate(bottom_bio.itertuples(), 1):
    print(f"{i}. {row.state:40s} - {row.bio_update_rate:>8.2f}%")
print()

print("=" * 80)
