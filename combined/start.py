import os
import shutil
import requests
# import sys

from process_graphic_individual import generate_graphic
from ftp import ftp
import process_graphic_individual.generate_graphic
from process_results_phase1 import process_file_from_ftp
from penalties_apply import penalties_apply
from process_general_classification import process_GC_phase1
import constants

current_dir = os.getcwd()
#input_dir = os.path.join(current_dir, "fromFTP")
results_phase1 = "process_results_phase1"
processedFilesCSV = os.path.join(current_dir, results_phase1, "processed_files.csv") 

#optional - CLEANING for testing purposes only
if os.path.exists(processedFilesCSV):
    os.remove(processedFilesCSV)
shutil.rmtree(constants.output_phase1, ignore_errors=True)
shutil.rmtree(constants.output_individual_graphic, ignore_errors=True)

ftp.get_ftp_files()

process_file_from_ftp.get_race_results()

penalties_apply.apply_penalties()

generate_graphic.generate_individual_graphic()

process_GC_phase1.generate_GC_phase1()
