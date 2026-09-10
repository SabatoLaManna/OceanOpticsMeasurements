#Sabato La Manna

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import curve_fit
from datetime import datetime
import yaml

CONFIG_FILE = r"config.yaml"

def load_config():
    with open(CONFIG_FILE, "r") as config:
        return yaml.safe_load(config)



def model(x, A, B, C, D):
    return A * np.cos(B * x + C) + D

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_title_time(time_string):

    try:
        if "_" in time_string and len(time_string.split("_")) == 2:
            dt = datetime.strptime(
                time_string,
                "%Y%m%d_%H%M%S"
            )
            return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        pass

    return time_string



def fit_mzi_csv(
        csv_file,
        wavelength_column,
        intensity_column,
        plot=True,
        SerialNumber="",
        Time=""
):

    df = pd.read_csv(csv_file)

    if isinstance(wavelength_column, str):
        wavelength = df[wavelength_column].to_numpy()
    else:
        wavelength = df.iloc[:, wavelength_column].to_numpy()

    if isinstance(intensity_column, str):
        intensity = df[intensity_column].to_numpy()
    else:
        intensity = df.iloc[:, intensity_column].to_numpy()

   

    intensity_smooth = gaussian_filter1d(
        intensity,
        sigma=load_config()['Analysis']['GaussianSmoothing']
    )

    

    A0 = (
        intensity_smooth.max()
        - intensity_smooth.min()
    ) / 2

    D0 = np.mean(intensity_smooth)

    period_guess = 0.5
    B0 = 2 * np.pi / period_guess
    C0 = 0

    

    weights = np.ones_like(intensity)

    weights[
        intensity >
        np.percentile(intensity, 90)
    ] = 0.3

    x = wavelength-wavelength.mean()
    y = intensity_smooth - np.mean(intensity_smooth)

    dx = np.mean(np.diff(x))

    freqs = np.fft.rfftfreq(len(y), dx)
    fft_mag = np.abs(np.fft.rfft(y))

    peak = np.argmax(fft_mag[1:]) + 1

    freq0 = freqs[peak]
    B0 = 2*np.pi*freq0

    print("FFT B0 =", B0)
    print("FFT FSR =", 2*np.pi/B0)
    popt, pcov = curve_fit(
        model,
        x,
        intensity_smooth,
        p0=[A0, B0, C0, D0],
        maxfev=100000
    )

    A, B, C, D = popt
    print(popt)



    fit = model(
        x,
        A,
        B,
        C,
        D
    )

    residuals = intensity_smooth - fit

    ss_res = np.sum(residuals ** 2)

    ss_tot = np.sum(
        (
            intensity_smooth
            - np.mean(intensity_smooth)
        ) ** 2
    )

    r_squared = 1 - ss_res / ss_tot

    n = len(intensity)
    p = 4

    adj_r2 = 1 - (
        (1 - r_squared)
        * (n - 1)
        / (n - p - 1)
    )

    rmse = np.sqrt(
        np.mean(residuals ** 2)
    )

    rmsea = (
        rmse / abs(A) * 100
        if abs(A) > 0
        else np.nan
    )

    errors = np.sqrt(
        np.diag(pcov)
    )


    fsr = 2 * np.pi / abs(B)

    Imax = D + abs(A)
    Imin = D - abs(A)

    visibility = (
        (Imax - Imin)
        /
        (Imax + Imin)
    )
    lambda0 = np.mean(wavelength)   # nm
    fsr = 2*np.pi/abs(B)            # nm

    deltaL_um = float(input("What is the delta_L in um? enter 0 to skip the ng calculation.\n>>>>>  "))

    if deltaL_um ==0:
        ng = "Skipped"
    else:
        deltaL_nm = deltaL_um * 1000
        ng = f"{(lambda0**2 / (fsr * deltaL_nm)):.4f}"


    results = {
        "A": A,
        "B": B,
        "C": C,
        "D": D,

        "A_error": errors[0],
        "B_error": errors[1],
        "C_error": errors[2],
        "D_error": errors[3],

        "FSR": fsr,
        "Ng": ng,
        "Imax": Imax,
        "Imin": Imin,

        "PeakToPeak": 2 * abs(A),

        "Visibility": visibility,

        "R2": r_squared,
        "Adj_R2": adj_r2,

        "RMSE": rmse,
        "RMSEa": rmsea
    }


    results_txt = f"""
==================================================
FIT PARAMETERS
==================================================

A = {A:.6f} ± {errors[0]:.6f}
B = {B:.6f} ± {errors[1]:.6f}
C = {C:.6f} ± {errors[2]:.6f}
D = {D:.6f} ± {errors[3]:.6f}

==================================================
DERIVED VALUES
==================================================

FSR          = {fsr:.6f}
Ng           = {ng}
Imax         = {Imax:.6f}
Imin         = {Imin:.6f}
PeakToPeak   = {2*abs(A):.6f}
Visibility   = {visibility:.6f}

==================================================
FIT QUALITY
==================================================

R²           = {r_squared:.6f}
Adjusted R²  = {adj_r2:.6f}
RMSE         = {rmse:.6f}
RMSE/A (%)   = {rmsea:.6f}

Note: The RMSE/A is the RMSE applied to the Amplitude, and will return a percentage. The closer to 0 this is, the better the fit explains the model.
"""

    print(results_txt)


    file_stamp = timestamp()

    txt_filename = (rf"data\cosine_fits\Data_cosine_fit_{SerialNumber}_{Time}.txt")

    with open(txt_filename, "w") as f:
        f.write(results_txt)

    print(f"Results saved: {txt_filename}")


    if plot:

        x_fit = np.linspace(
            wavelength.min(),
            wavelength.max(),
            3000
        )

        y_fit = model(
            x_fit-wavelength.mean(),
            A,
            B,
            C,
            D
        )

        plt.figure(figsize=(14, 6))

        plt.plot(
            wavelength,
            intensity,
            "o",
            alpha=0.5,
            label="Measured"
        )

        plt.plot(
            wavelength,
            intensity_smooth,
            "g-",
            linewidth=3,
            label="Smoothed"
        )

        plt.plot(
            x_fit,
            y_fit,
            "r-",
            linewidth=3,
            label=f"Cosine Fit (R²={r_squared:.4f})"
        )

        display_time = format_title_time(Time)

        plt.title(
            f"Cosine Fit {SerialNumber} @ {display_time}"
        )

        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity")

        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        

        png_filename = (rf"data\cosine_fits\Plot_cosine_fit_{SerialNumber}_{Time}.png")

        plt.savefig(
            png_filename,
            dpi=300,
            bbox_inches="tight"
        )

        print(
            f"Plot saved: {png_filename}"
        )

        plt.show()

    return results