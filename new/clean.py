import os
import shutil
import constants


if os.path.exists(constants.processedFilesCSV):
    os.remove(constants.processedFilesCSV)
shutil.rmtree(constants.output_phase1, ignore_errors=True)
shutil.rmtree(constants.output_individual_graphic, ignore_errors=True)