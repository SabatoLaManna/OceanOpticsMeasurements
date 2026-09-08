import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# Hide the root tkinter window
root = tk.Tk()
root.withdraw()

# Ask user to select a CSV file
file_path = filedialog.askopenfilename(
    title="Select CSV File",
    filetypes=[("CSV files", "*.csv")]
)

if not file_path:
    print("No file selected.")
    exit()

# Read the CSV file
df = pd.read_csv(file_path)

# Check that at least two columns exist
if len(df.columns) < 2:
    raise ValueError("CSV file must contain at least two columns: Wavelength and Intensity")

# Rename first two columns for consistency
df.columns = ["wavelength", "Intensity"] + list(df.columns[2:])

# Convert Intensity from dBm to mW
df["Intensity"] = 10 ** (df["Intensity"] / 10)

# Overwrite the original CSV file
df.to_csv(file_path, index=False)

print(f"Conversion complete. File overwritten:\n{os.path.basename(file_path)}")
