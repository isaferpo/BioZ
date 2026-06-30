# BioZ

This GitHub repository contains the codes I have used throughout my master's thesis in bioimpedance to communicate with the impedance analyzers employed to take the measures of this work: E 5601 B for two-point measurements and Keysight LCR E4980A for four-point measurements. 

*Codes for Keysight*

MATLAB:

- InicializacionLCR_E4980A_v2d0.m: This MATLAB script stablishes remote communication with the LCR.
- VolcadoAutomaticoV3d0.m: After manual calibration of the LCR, this script triggers the measurement process and then saves the results in a CSV file.

PYTHON:

- inicializacion_LCR.py: The same MATLAB script translated into Python for a transition of the pipeline to open source.
- Medidas_LCR.py: Triggers the measurement process as well as saving the results in a CSV file in the same directory as the script.
- script_graficas.py: Turns the data from the CSV file into a graph, representing the module of the impedance as well as the phase angle versus frequency.
- medidas_autonomas_LCR.py: Allows the user to initiate the measurement progress by themselves through voice commands without the need of someone typing into the keyboard to start measuring. (Prototype)

*Code for E 56061B*

MATLAB:

- E5061Bv5d0.m: This script controls remotely the impedance analyzer and gives instructions to follow the measure process.
