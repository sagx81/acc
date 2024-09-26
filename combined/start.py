import os
import shutil
# import sys

from ftp import ftp
from process_results_phase1 import process_file_from_ftp
from penalties_apply import penalties_apply

current_dir = os.getcwd()
#input_dir = os.path.join(current_dir, "fromFTP")
results_phase1 = "process_results_phase1"
processedFilesCSV = os.path.join(current_dir, results_phase1, "processed_files.csv") 

#optional - CLEANING for testing purposes only
if os.path.exists(processedFilesCSV):
    os.remove(processedFilesCSV)
shutil.rmtree("output_phase1")
# os.rmdir("output_phase1")

# adding to the system path
# sys.path.insert(0, './results_phase1/')

# print(f"\n1. Pobieram pliki z FTP\n")

ftp.get_ftp_files()

process_file_from_ftp.get_race_results()

penalties_apply.apply_penalties()

# print(f"\nLecimy z obrobka wynikow")

