import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select CSV File",
    filetypes=[("CSV files", "*.csv")]
)

if not file_path:
    print("No file selected.")
    exit()

df = pd.read_csv(file_path)

if len(df.columns) < 2:
    raise ValueError("CSV file must contain at least two columns: Wavelength and Intensity")

df.columns = ["wavelength", "Intensity"] + list(df.columns[2:])

df["Intensity"] = 10 ** (df["Intensity"] / 10)

df.to_csv(file_path, index=False)

print(f"Conversion complete. File overwritten:\n{os.path.basename(file_path)}")
