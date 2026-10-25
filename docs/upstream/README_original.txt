## FAIR Train tensile testing data

This archive contains the raw data measured on a series of metal samples using a tensile testing machine. The archive contains two folders: data and scripts. 

Folder data contains one folder "dataClass2025" with the following subfolders

- rawData
- figs
- jsonFiles

Folder scripts contains a few Python files with auxiliary functions to read raw data, extract properties and save json dictionaries. The folder also contains the jupyter notebook that reads raw data, extracts the properties and saves the dictionaries. The script iterates over CSV files in the data/ folder, reading Sheet1/Sheet2 to extract specimen dimensions and compute engineering/true stress–strain along with key properties (Young’s modulus via elastic fit, Rp 0.2%, proportionality limit, resilience, toughness, and fracture metrics). It then generates plots saved to ../figs/ and builds structured JSON documents—containing raw data, processed arrays, properties, and metadata—saved to ../jsonFiles/ with filenames matching each source file.
Sample name and material are parsed from the filename, and arrays are serialized to lists for JSON.

#Credit

The functions and core functionality were designed and coded by Edgar Tarin as a part of the MASE6401 Project at the University of Texas at El Paso (UTEP) on 10/20/2025. The course was delivered by Brian Schuster (UTEP). The code and the folder structure were organized by Olga Wodo (University at Buffalo).