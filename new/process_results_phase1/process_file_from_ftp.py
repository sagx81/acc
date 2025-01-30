
import os
import json
import glob
import csv
import datetime

from utils_entities import constants
from utils_entities import utilities
from utils_entities.processed_files import ProcessedFile

# from new.utils_entities import constants
# from new.utils_entities import utilities
# from new.utils_entities.processed_files import ProcessedFile


current_dir = os.getcwd()
input_dir = constants.files_from_ftp
output_phase1 = constants.files_result_phase_1
results_phase1 = "process_results_phase1"
processedFiles = []
processedFilesCSV = os.path.join(current_dir, results_phase1, "processed_files.csv") 

def get_race_results():

    print("\n*** Processing FTP files phase - 1 \n")

    processedFileHasValue = False
    filesSorted = sorted(glob.glob(os.path.join(input_dir, "*.json")), key=os.path.getmtime, reverse=False)
    previousRaceDay = ""    

    for json_file in filesSorted:
        try:
            # print(f"Processing file: {json_file}")

            if (json_file.split('_')[0] == previousRaceDay):
                raceIndex += 1
            else:
                raceIndex = 1

            previousRaceDay = json_file.split('_')[0]
            
            # skipp if processed
            # if (os.path.exists(processedFilesCSV) ):
            #     processedFileHasValue = True
            #     with open(processedFilesCSV, 'r', encoding='utf-8') as file:         
            #         reader = csv.DictReader(file)           
            #         # print(f"Reading processed files: {processedFilesCSV}")
            #         fileFound = False
            #         for row in reader:
            #             fileToFind = os.path.basename(json_file)
                        
            #             if (fileToFind in row['File']):
            #                 # print(f"\n SKIPPING file: {json_file}\n")
            #                 fileFound = True
            #                 break
            #         if (fileFound):
            #             continue
            
            # print(f"Openning file: {json_file}")

            with open(json_file, 'r', encoding='utf-16-le') as file:
                data = json.load(file)

                serverName = data.get('serverName')
                if ("open" in serverName.lower()):
                    # print(f"\n SKIPPING file: {json_file}\n")
                    continue
                
                if (serverName):
                    seriesDir = serverName.split('|')[1].strip()
                else:
                    seriesDir = "unknown"                

                # week LEAUGE exception - wrong name was gnerated in the FTP, server was set with spelling issue
                week_league = "WEEK LEAGUE"
                if "week leauge" in seriesDir.lower():
                    seriesDir = seriesDir.upper().replace("WEEK LEAUGE", week_league).replace("  ", " ")
                
                # determine race number by time the race was held
                raceNumber = ""
                if ("week league" in seriesDir.lower()):
                    raceNumber = f" R{int(raceIndex)}"

                seriesDir = seriesDir.upper()    
                output_dir = os.path.join(current_dir, output_phase1, seriesDir)

                #print(f"\n Output dir: {output_dir}")

                short_name = data.get('trackName', 'unknown_track')

                base_name = os.path.basename(json_file)
                date_part = base_name.split('_')[0]
                time_part = base_name.split('_')[1]

                # Quali files
                isQuali = False
                postfix = ''
                if '_Q' in json_file:
                    postfix = '_Q'
                    isQuali = True

                base_output_name = f"{short_name}-{seriesDir}{raceNumber}-{date_part}-{time_part}{postfix}"

                # output_image_file = generate_unique_filename(output_dir, base_output_name, extension="png")
                output_csv_file = utilities.generate_unique_filename(output_dir, base_output_name, extension="csv")

                lap_counts = [line['timing'].get('lapCount', 0) for line in data['sessionResult']['leaderBoardLines']]
                if lap_counts:
                    max_lap_count = max(lap_counts)
                    min_laps_required = max_lap_count * 0.75
                else:
                    min_laps_required = 0

                results = []
                best_lap_times = []
                first_driver_time = None
                first_driver_laps = max_lap_count
                first_driver_best_time_ms = 0

                for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
                    drivers = line['car']['drivers']
                    driverNumber = line['car']['raceNumber']
                    driverCar = line['car']['carModel']

                    driver_names = [driver['lastName'] for driver in drivers]
                    driver_names_str = ", ".join(driver_names)
                    total_time_ms = line['timing']['totalTime']
                    best_lap_ms = line['timing'].get('bestLap', 0)
                    lap_count = line['timing'].get('lapCount', 0)

                    # print("for loop \n")

                    # skipp spectators
                    if (lap_count == 0):
                        continue
                    elif not isQuali and lap_count < min_laps_required:
                        total_time_str = constants.dnf_text
                        best_lap_str = constants.dnf_text
                        points_awarded = 0
                    # elif isQuali: ?????
                    else:
                        if i == 0:
                            first_driver_time = total_time_ms
                            first_driver_best_time_ms = best_lap_ms
                            total_time_str = utilities.convert_time(total_time_ms)
                        else:
                            #TODO crash here : first_driver_time is none , 1st driver DNF - noo, it is about Quali
                            if isQuali:
                                time_difference = best_lap_ms - first_driver_best_time_ms
                            else:
                                time_difference = total_time_ms - first_driver_time
                            timeDiffString = utilities.convert_time(time_difference)
                            # sometimes there is negative value if total driver time was < than total time of the winner
                            # for example when joining race after start    
                            if ('-' not in timeDiffString):
                                timeDiffString = f"+{timeDiffString}"
                            
                            if isQuali:
                                total_time_ms = best_lap_ms
                                total_time_str = utilities.convert_time(best_lap_ms)
                            elif lap_count < first_driver_laps:
                                lapLabel = "lap"
                                laps_difference = first_driver_laps - lap_count
                                if laps_difference > 1:
                                    lapLabel = "laps"
                                total_time_str = f"{timeDiffString} (+{laps_difference} {lapLabel})"
                            else:
                                total_time_str = f"{timeDiffString}"

                        best_lap_str = utilities.convert_time(best_lap_ms)
                        if isQuali:
                            points_awarded = 0
                        else:
                            points_awarded = constants.points[i] if i < len(constants.points) else 1

                    # print("append results")
                    # print(f"{i}\n")
                    
                    results.append([
                        i + 1,
                        driver_names_str,
                        total_time_str,
                        total_time_ms,
                        best_lap_str,
                        lap_count,
                        points_awarded
                    ])
                    best_lap_times.append(best_lap_ms)

                results.insert(0, ['Position', 'Driver', 'Total time', 'Total time ms', 'Best lap', 'Laps', 'Points'])

                # print("best lap")
                
                if best_lap_times:
                    fastest_lap_time = min(best_lap_times)
                    fastest_lap_time_converted = utilities.convert_time(fastest_lap_time)
                else:
                    fastest_lap_time_converted = None

                print(f"output_csv_file: {output_csv_file}")

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                with open(output_csv_file, mode='w+', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(results)
                    csv_file.close()
                    # csv_file.writerows(results)

                # save processed file
                #processedFiles.append([os.path.basename(json_file), datetime.datetime.now()])
                

                # not used:
                # processedFiles.append({os.path.basename(json_file), datetime.datetime.now()})
                # processedFiles.append(ProcessedFile(os.path.basename(json_file), datetime.datetime.now()) )


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {json_file}: {e}")
        except KeyError as e:
            print(f"Missing key in JSON file {json_file}: {e}")
        # with open(json_file, 'r', encoding='utf-16-le') as file:
        #         print(json.load(file))
        except Exception as e:
            print(f"Process Results Phase1 - An error occurred processing file {json_file}: {e}")
            # return

    
    # save processed files
    # try: 
    #     # for a in processedFiles:
    #     #     print(a)

    #     if (not processedFileHasValue):
    #         processedFiles.insert(0, ['File', 'Date'])

    #     with open(processedFilesCSV, mode='a', newline='', encoding='utf-8') as csv_file:
    #         writer = csv.writer(csv_file)
    #         writer.writerows(processedFiles)
    # except Exception as e:
    #     print(f"Process Results Phase 1 Save Processed File - An error occurred processing file {processedFilesCSV}: {e}")

