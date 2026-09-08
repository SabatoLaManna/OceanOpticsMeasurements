# Sabato La Manna

from pathlib import Path
from datetime import datetime
import logging
import yaml
import numpy as np
import pandas as pd
import seabreeze
import seabreeze.spectrometers as sb
from seabreeze.cseabreeze import SeaBreezeAPI
from Analysis import *
import matplotlib.pyplot as plt
seabreeze.use("cseabreeze") 


CONFIG_FILE = r"config.yaml"


def load_config():
    with open(CONFIG_FILE, "r") as config:
        return yaml.safe_load(config)


def setup_logging():

    Path(r"logs").mkdir(exist_ok=True)

    logging.basicConfig(
    filename="logs/measurement.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
    )


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def connect_to_spectrometer(Target_SerialNumber):
    logging.info("Searching for devices")
    Device_list = sb.list_devices()

    if not Device_list:
        logging.warning("No devices found")
        raise RuntimeError("No devices found!")

    for Device in Device_list:
        Spec = sb.Spectrometer(Device)
        if Spec.serial_number == Target_SerialNumber:
            logging.info(f"Connected to spectrometer {Spec.model} with serial number {Spec.serial_number}")
            
            return Spec

        
    logging.info("Required spectrometer not found")
    raise RuntimeError("Required spectrometer not found")

def set_integrationtime(Spectrometer, Integrationtime):
    Spectrometer.integration_time_micros(Integrationtime)
    logging.info(f"Integration time set up {Integrationtime} microseconds.")


def acquire_spectrum(Spectrometer, Scans):
    logging.info(f"Acquiring {Scans} scans.")
    Measurements = []

    for i in range(Scans):
        Measurements.append(Spectrometer.intensities())
        logging.info(f"{i}/{Scans}")
    Wavelengths = Spectrometer.wavelengths()
    Avg = np.mean(Measurements, axis=0)
    return Wavelengths, Avg

def save(Wavelenghts, Intensities, Serial, Notes, WL):
    Path("data/spectra").mkdir(parents=True, exist_ok=True)
    Path("data/ReadingPlots").mkdir(parents=True, exist_ok=True)
    TIME = timestamp()
    FileName = f"data/spectra/{TIME}_{Serial}_{WL}_{Notes}.csv"
    plt.figure(figsize=(10, 5))
    plt.plot(Wavelenghts, Intensities, linewidth=1)

    plt.title(f"Measured intensity {Serial} @{TIME} | {Notes}")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (Arbritrary units)")
    plt.grid(True)
    PlotNameFilename = f"data/ReadingPlots/Plot_{Serial}_{TIME}.png"
    
    
    plt.savefig(PlotNameFilename)
    plt.show()
    logging.info(f"Graph saved to {PlotNameFilename}")
    plt.close()
    DataFrame = pd.DataFrame({"wavelength":Wavelenghts, "Intensity": Intensities})
    DataFrame.to_csv(FileName, index=False)

    fit_mzi_csv(FileName, "wavelength", "Intensity", True, Serial, TIME)

    logging.info(f"Measurements saved to {FileName}")

    return FileName

def Main():
    setup_logging()
    Config = load_config()
    logging.info("Script starting")
    SerialNumber = Config['spectrometer']['serial_number']
    Integrationtime = Config['acquisition']['integration_time_us']
    Scans = Config['acquisition']['scans_to_average']

    try:
        Spectrometer = connect_to_spectrometer(SerialNumber)
        while True:
            WL = int(input("Enter wavelength. Enter 0 to stop.\n>>>>"))
            if WL ==0:
                print("Stopping script, please proceed to the Stitching step now.")
                exit
            Spectrometer.open()
            set_integrationtime(Spectrometer, Integrationtime)
            Wavelengths, Intensities = acquire_spectrum(Spectrometer, Scans)
            print(f"Highest Intensity Measured: {np.max(Intensities)}\nMax Insensity measureable{Spectrometer.max_intensity}")
            save(Wavelengths, Intensities, Spectrometer.serial_number, Config['acquisition']['notes'], WL)
            Spectrometer.close()

        
        


    except Exception as error:

        logging.info(f"Error with measuring. - {error}")
        raise RuntimeError(f"Error with measuring. - {error}")
    
        



if __name__ == "__main__":
    Main()