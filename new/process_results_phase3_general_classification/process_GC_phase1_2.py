import os
import glob
import csv
from collections import defaultdict

from utils_entities import constants
from utils_entities import utilities
from process_results_phase4_graphics import generate_graphic_gc
# from process_results_phase4_graphics import generate_graphic_gc2

input_dir = constants.files_result_phase_1
output_dir = constants.files_result_phase_3
background_image = os.path.join(constants.process_graphic_individual, "files", "background", "general classification.png")
font_path = os.path.join(constants.process_graphic_individual, "files", "fonts", "BigShouldersDisplay-Bold.ttf")

def generate_GC_phase1():

    print("** General Classification V2 ")

    driversList = utilities.get_drivers_list_offline()
    gcPenalties = utilities.get_gc_penalties_from_csv()
    
    dirs = utilities.get_series_directories()    
    for input_dir in dirs:

        output_csv_file = utilities.generate_GC_file2_csv(os.path.basename(input_dir))
        
        # skipp if file exists
        if (os.path.exists(output_csv_file)):
            continue

        # clear general classification 
        general_classification = defaultdict(int)

        # for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
        for csv_file in utilities.get_serie_csv_files(input_dir):

            # skip files which should not be processed
            if utilities.should_skip_file_processing(csv_file):
                continue

            try:
                results = utilities.get_results_from_csv2(csv_file, inovkedBy='Generate GC phase1 V2')

                for row in results:
                    name = row.driver

                    #if stars then team as separate column
                    team = ''
                    driver = ''

                    # prepare driver and team from csv splitted by '/n'
                    if (len(row.driver.split('\n')) > 1 and 'stars' in input_dir.lower()):
                        name = row.driver.split('\n')[0]

                    driverName = utilities.get_driver_name(row.playerId, driversList)
                    if not driverName:
                        driverName = name

                    general_classification[driverName] += row.points

            except Exception as e:
                print(f"Process CG phase1: An error occurred processing file {csv_file}: {e}")

        general_classification_list = []        
        for driver, points in general_classification.items():
            general_classification_list.append([driver, points])

        # apply GC penalties 
        if len(general_classification_list) > 0:
            for gcPenalty in gcPenalties:
                if (utilities.is_penalty_valid_for_race_type(gcPenalty, input_dir)):
                    driverIndex = [index for (index, item) in enumerate(general_classification_list) if item[0] == gcPenalty.driver ]
                    if len(driverIndex) > 0:
                        general_classification_list[driverIndex[0]][1] -= gcPenalty.gcPenaltyPoints

        # Sort list by points
        general_classification_list.sort(key=lambda x: -x[1])

        # Positions setup based on points
        for i, item in enumerate(general_classification_list):
            item.insert(0, i + 1)

        directoryPath = os.path.join(constants.files_result_phase_1, os.path.basename(input_dir))
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)

        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([['Position', 'Driver', 'Points']] + general_classification_list)

        print(f"Klasyfikacja generalna została zapisana do pliku: {output_csv_file}")

        raceType = os.path.basename(input_dir).split(' ')[0]

        # generate graphic
        generate_graphic_gc.generate_gc(general_classification_list, raceType, output_csv_file, input_dir)
