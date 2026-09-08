#Sabato La Manna

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import yaml
from tkinter import filedialog
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
from datetime import datetime

from Analysis import *


CONFIG_FILE = r"config.yaml"


def model(lam, A, B, C, D):
    return A * np.cos(B * lam + C) + D


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def hampel_filter(signal, window_size=10, n_sigma=3):

    filtered = signal.copy()

    for i in range(window_size, len(signal) - window_size):

        window = signal[i - window_size:i + window_size + 1]

        median = np.median(window)
        mad = np.median(np.abs(window - median))

        if mad == 0:
            continue

        threshold = n_sigma * 1.4826 * mad

        if np.abs(signal[i] - median) > threshold:
            filtered[i] = median

    return filtered



root = tk.Tk()
root.withdraw()

grating_file = filedialog.askopenfilename(
    title="Select Grating Coupler CSV",
    filetypes=[("CSV files", "*.csv")]
)

if not grating_file:
    quit()

mzi_file = filedialog.askopenfilename(
    title="Select MZI Measurement CSV",
    filetypes=[("CSV files", "*.csv")]
)

if not mzi_file:
    quit()



gc = pd.read_csv(grating_file)
mzi = pd.read_csv(mzi_file)

print("Grating columns:", gc.columns.tolist())
print("MZI columns:", mzi.columns.tolist())

gc_wavelength = gc["wavelength"].to_numpy()
gc_intensity = gc["Intensity"].to_numpy()

mzi_wavelength = mzi["wavelength"].to_numpy()
mzi_intensity = mzi["Intensity"].to_numpy()



gc_min = np.min(gc_wavelength)
gc_max = np.max(gc_wavelength)

overlap_mask = (
    (mzi_wavelength >= gc_min)
    & (mzi_wavelength <= gc_max)
)

mzi_wavelength = mzi_wavelength[overlap_mask]
mzi_intensity = mzi_intensity[overlap_mask]

print(
    f"Using overlap range: "
    f"{mzi_wavelength.min():.2f} nm "
    f"to "
    f"{mzi_wavelength.max():.2f} nm"
)


interp_func = interp1d(
    gc_wavelength,
    gc_intensity,
    kind="linear"
)

gc_interp = interp_func(mzi_wavelength)



window = min(51, len(gc_interp) // 2 * 2 - 1)

if window < 5:
    window = 5

gc_smooth = savgol_filter(
    gc_interp,
    window_length=window,
    polyorder=3
)

print("gc_smooth min:", np.min(gc_smooth))
print("gc_smooth max:", np.max(gc_smooth))


gc_threshold = np.max(gc_smooth) - 20

valid = gc_smooth > gc_threshold

print("GC threshold:", gc_threshold)
print("Valid points:", np.sum(valid))
print("Removed points:", len(valid) - np.sum(valid))

wavelength = mzi_wavelength[valid]



normalized_intensity = (
    mzi_intensity[valid]
    - gc_smooth[valid]
)


intensity = hampel_filter(
    normalized_intensity,
    window_size=10,
    n_sigma=3
)




plt.figure(figsize=(10, 5))
plt.plot(mzi_wavelength, gc_smooth, label="GC smooth")
plt.axhline(
    gc_threshold,
    color="red",
    linestyle="--",
    label="5% threshold"
)
plt.xlabel("Wavelength (nm)")
plt.ylabel("GC Intensity")
plt.title("Smoothed Grating Response")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.figure(figsize=(10, 5))
plt.plot(
    wavelength,
    normalized_intensity,
    ".",
    alpha=0.4,
    label="Normalized"
)

plt.plot(
    wavelength,
    intensity,
    "r-",
    linewidth=1.5,
    label="After Hampel"
)

plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized Intensity")
plt.title("Normalized MZI")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()


normalized_df = pd.DataFrame({
    "wavelength": wavelength,
    "Intensity": intensity
})

filename = input("Enter file name here (NO EXTENSIONS)\n>>>>")

output_file = rf"data\normalizedspectra\normalized_mzi_{filename}.csv"

normalized_df.to_csv(
    output_file,
    index=False
)

print(f"Saved: {output_file}")

def load_config():
    with open(CONFIG_FILE, "r") as config:
        return yaml.safe_load(config)
    

fit_mzi_csv(
    output_file,
    "wavelength",
    "Intensity",
    True,
    load_config()['spectrometer']['serial_number'],
    datetime.now().strftime("%Y%m%d_%H%M%S")
)
