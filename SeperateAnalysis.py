#Sabato La Manna

import os
from tkinter import Tk, filedialog
from datetime import datetime
from Analysis import fit_mzi_csv
import yaml
CONFIG_FILE = r"config.yaml"

current_folder = os.path.dirname(os.path.abspath(__file__))

def load_config():
    with open(CONFIG_FILE, "r") as config:
        return yaml.safe_load(config)
    
def select_csv_and_analyze():
    root = Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select CSV file",
        initialdir=rf"{current_folder}\data\spectra",
        filetypes=[("CSV files", "*.csv")]
    )

    if not file_path:
        print("No file selected.")
        return


    

    fit_mzi_csv(
        file_path,
        "wavelength",
        "Intensity",
        True,
        load_config()['spectrometer']['serial_number'],
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )


select_csv_and_analyze()