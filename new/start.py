# import sys

from ftp import ftp

from utils_entities import utilities

from process_results_phase1 import process_file_from_ftp
from process_results_phase2_penalties_apply import penalties_apply
from process_results_phase2_penalties_apply import penalties_apply2
from process_results_phase3_general_classification import process_GC_phase1
from process_results_phase3_general_classification import process_GC_phase1_2
from process_results_phase4_graphics import generate_graphic
from process_results_phase4_graphics import generate_graphic2
 

# from process_graphic_individual import generate_graphic
# import process_graphic_individual.generate_graphic
# from process_general_classification import process_GC_phase1

# current_dir = os.getcwd()
#input_dir = os.path.join(current_dir, "fromFTP")
# process_results_phase1 = "process_results_phase1"
# processedFilesCSV = os.path.join(current_dir, process_results_phase1, "processed_files.csv")

# optional delete downloaded ftp files
# shutil.rmtree(constants.ftp_input_dir, ignore_errors=True)

#optional - CLEANING for testing purposes only
# if os.path.ts(processedFilesCSV):
#     os.remove(processedFilesCSV)
# shutil.rmtree(constants.output_phase1, ignore_errors=True)
# shutil.rmtree(constants.output_individual_graphic, ignore_errors=True)


# DRIVERS web update
# # Updates drivers list from web URL. Retrievs .json file with drivers list and updates local file which is used by other functionalities. 
# If request fails then previous drivers file is used.
utilities.update_drivers_list_from_web()

# 1. FTP
ftp.get_ftp_files()

process_file_from_ftp.get_race_results()

penalties_apply.apply_penalties()
penalties_apply2.apply_penalties()

generate_graphic.generate_individual_graphic()
generate_graphic2.generate_individual_graphic()

process_GC_phase1.generate_GC_phase1()
process_GC_phase1_2.generate_GC_phase1()
