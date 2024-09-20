# import os
import sys

from ftp import ftp
from results_phase1 import process_file_from_ftp

# adding to the system path
# sys.path.insert(0, './results_phase1/')

# print(f"\n1. Pobieram pliki z FTP\n")

ftp.get_ftp_files()

process_file_from_ftp.get_race_results()

# print(f"\nLecimy z obrobka wynikow")

