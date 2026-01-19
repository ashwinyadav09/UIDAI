import subprocess
import sys

result = subprocess.run(
    [sys.executable, r"E:\Aadhar UIDAI\PROJECT\scripts\STEP1_deep_data_investigation.py"],
    capture_output=True,
    text=True,
    timeout=300
)

print(result.stdout)
if result.stderr:
    print("\nERRORS/WARNINGS:")
    print(result.stderr)
