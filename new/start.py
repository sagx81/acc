# import sys

from ftp import ftp
from process_results_phase1 import process_file_from_ftp
from process_results_phase2_penalties_apply import penalties_apply
from process_results_phase4_graphics import generate_graphic
 

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
# if os.path.exists(processedFilesCSV):
#     os.remove(processedFilesCSV)
# shutil.rmtree(constants.output_phase1, ignore_errors=True)
# shutil.rmtree(constants.output_individual_graphic, ignore_errors=True)


# Process steps:
# 1. FTP
ftp.get_ftp_files()

process_file_from_ftp.get_race_results()

penalties_apply.apply_penalties()

generate_graphic.generate_individual_graphic()

process_GC_phase1.generate_GC_phase1()
