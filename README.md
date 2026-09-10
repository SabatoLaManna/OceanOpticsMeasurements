
# Ocean Optics Measurements

This is a repository which alows you to take meaurements using your Ocean Optics spectrometer and fit them to a cosine model. 
This repository is mostly meant for usage in photonics.



## Installation

To install this repository download the folders as zip file and extract them or run 
` git clone https://github.com/SabatoLaManna/OceanOpticsMeasurements.git` 

Ensure that you have Python and Pip installed on your device, or create a .venv

Open PowerShell, and navigate to the folder (`cd OceanOpticsMeasurements`). Because this repo normally contains folders, which are empty you will need to create those, and install the python libraries used. Please enter these commands in your (PowerShell) Terminal

```bash
  mkdir data, logs, data\cosine_fits, data\normalizedspectra, data\ReadingPlots, data\spectra, data\stitchedspectra
  pip install -r requirements.txt
```
    
    
## Using the system

Start by ensuring that your spectrometer is supported by the [Seabreeze library created by Andreas Poehlmann](https://python-seabreeze.readthedocs.io/en/latest/index.html), since that is what will be telling your spectrometer what to do.
### Setup
Go to the `config.yaml` file, and change the `serial_number` value to the serial number of your spectrometer. Change the `integration_time_us` to the integration time of the spectrometer in microseconds. 
`scans_to_average` is the amount of scans the spectrometer should take, and then average out those results. 20 has been the amount that I've used and I have no complaints. The higher this nunber is the more representative your results are, but the longer your run takes. The `runs_to_make` is the amount of measurements the spectrometer should take, a run is seen as taking multiple scans. This variable will not have to be used if you will use the `MultiWavelength` script.
The `notes` variable will be a part of the scan's output file if you are running `MultiWavelength`, this is to help differentiate different measurement types. 
Change the `HempelSmoothing` and `GaussianSmoothing` variables to values you wish to use when applying a smooth to the results. Please do note that this may not be 0, but if you do not want to smooth use 0.1 or smaller, and this will practicly remove all forms of smoothening. The HempelSmoothening will be applied during the normalization, and the GaussianSmoothing will be applied during analyzation.
**To take a proper measurement it is important that you first measure a reference waveguide to eliminate the effect of the Grating- or edge couplers.**
### Single mode measuring
The most simple, and easy to use way to take measurements. This takes a measurement of the current view, and fits it to the cosine model. To use this all you have to do is run the script called `MeasurementCreation_Single.py`, and the analysis will happen from itself. You will be provided with a `.csv` file of your measurement, a plot of that `.csv` file, and a cosine model fitting, each in their seperate folders. 
### MultiWavelength mode measuring
Ensure that you have updated the `config.yaml` file, and run the `MeasurementCreation_MultiWavelength.py` script. You will be prompted to provide the wavelength you are sending from the laser, and then it will take its measurements, after that you can tune your laser to another wavelength and repeat this process. This will provide you with multiple `.csv` files and plots, but no cosine model. Because you sent a single wavelength in the laser you will receive multiple peaks you will have to stitch your measurements together.
### Stitching the measurements
This takes only the spectrum that you need, by looking at the filenames. run `Stitching.py`, and you will be prompted to select multiple files. Select the `.csv` files that you want to stitch together, and let the script do the rest. It will output a new `.csv` file in `data\stitchedspectra` which can be used 
in further steps. Do this for both your reference, and MZI measurements. 
It is possible that you may have to update the `serial_letters` variable to match the letters of your serial number, as to follow the expected file format.
### Removal of the coupler's effect
Ocean Optics spectrometer meausure intensity in a linear scale, which is why you need to run the `GratingCouplerRemoval_Linear.py` script, you will first be prompted to select the stitched `.csv` file of your grating couplers, and then the `.csv` file of your stitched MZI measurements. after this you will see a graph with the cosine model, as well as an output of all the variables extracted by the data. 
### Analyzing the results
If you took your measurements and normalized your results using this sytem, your results should have already been automatically analyzed for you. But if you wish to re-analyze them with a different Gaussian smooth all you have to do is run the `SeperateAnalysis.py` script and select your normalized spectrum. 
### Using external measurements
If you have already gotten your measurements using another system, but would like to normalize them or fit them to a cosine model it is also completely possible to do that using this setup. Please make sure to follow the below steps as to ensure a proper analyzation.
#### Results in a .txt file
Remove the header of your `.txt` file, and ensure that the measurements are written in a the order `Wavelength`, `Intensity`. Open the `Convert.py` script and change the variables of `input_` and `output_file` to the path of your `.txt` file and where you want your `.csv` file to be written. Then run the script.
#### Results in dBm
Make sure that the header of your `.csv` file is exactly `wavlength` and `Intensity` (CAPITAL SENSITIVE), open the `dBmTomW.py` script, and run it. Select your `.csv` file and it will be overwritten with mW values of your dBm measurements.
#### Normalize your results (in case they aren't normalized yet)
Run the `GratingCouplerRemoval_Linear.py` script, you will first be prompted to select the stitched `.csv` file of your grating couplers, and then the `.csv` file of your  MZI measurements. after this you will see a graph with the cosine model, as well as an output of all the variables extracted by the data. 
#### Analyze your results (in case they are normalized already)
Run the `SeperateAnalysis.py` script and select your `.csv` file, the code will handle the rest.

