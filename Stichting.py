#Sabato La Manna
 
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import re



root = tk.Tk()
root.withdraw()

file_paths = filedialog.askopenfilenames(
    title="Select CSV files",
    filetypes=[("CSV Files", "*.csv")]
)

if not file_paths:
    quit()

results = []



for file_path in file_paths:

    filename = Path(file_path).stem

    match = re.search(r'QEPB\d+_(\d+)', filename)

    if not match:
        print(f"Could not extract wavelength from {filename}")
        continue

    target_wavelength = float(match.group(1))

    df = pd.read_csv(file_path)

    wavelength_col = df.columns[0]
    intensity_col = df.columns[1]

    wavelengths = df[wavelength_col].to_numpy()
    intensities = df[intensity_col].to_numpy()

    sort_idx = np.argsort(wavelengths)
    wavelengths = wavelengths[sort_idx]
    intensities = intensities[sort_idx]

    intensity = np.interp(
        target_wavelength,
        wavelengths,
        intensities
    )

    results.append({
        "wavelength": target_wavelength,
        "Intensity": intensity
    })

    print(
        f"{filename}: "
        f"{target_wavelength:.2f} nm -> "
        f"{intensity:.2f}"
    )



result_df = pd.DataFrame(results)

result_df = (
    result_df
    .sort_values("wavelength")
    .reset_index(drop=True)
)

name = input("Enter the name you want to give to the file (NO EXTENSION)\n>>>>> ")

output_file = rf"data\stitchedspectra\{name}.csv"

result_df.to_csv(
    output_file,
    index=False
)

print(f"\nSaved to {output_file}")
print(f"Total points: {len(result_df)}")