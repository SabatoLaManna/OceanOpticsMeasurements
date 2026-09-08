#Sabato La Manna


# This is a helper script, for if you are trying to analyze a spectrum which was saved as a .txt file, 
# Just fill out the input's relative file path, the filepath you want of the new .csv file, and the headers you want your .csv file to use. 
# IMPORTANT: All the scrips assume that the headers are 'wavelength' and 'Intensity' in that order, so best to just keep them like that.


import csv

input_file = "MZI_Ref.txt"
output_file = "MZI_Ref.csv"

headers = ["wavelength", "Intensity"]

with open(input_file, "r") as txt_file, open(output_file, "w", newline="") as csv_file:
    writer = csv.writer(csv_file)

    writer.writerow(headers)

    for line in txt_file:
        row = line.strip().split()

        writer.writerow(row)

print(f"CSV file created: {output_file}")
