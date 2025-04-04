
import os
import json
import glob
import csv
import datetime
from pathlib import Path

from utils_entities import constants
from utils_entities import utilities
from utils_entities import entities

# current_dir = os.getcwd()
input_dir = constants.files_from_ftp
# output_phase1 = constants.files_result_phase_1
processedFiles = []

def get_race_results():

    print("\n*** Processing FTP files phase - 1 \n")

    items = glob.glob(os.path.join(input_dir, "*.json"))
    filesSorted = sorted(items, reverse=True)
    
    sameDayRace = ""
    sameDayQuali = ""

    driversList = utilities.get_drivers_list_offline()

    for json_file in filesSorted:
        try:

            base_name = os.path.basename(json_file)
            date_part = base_name.split('_')[0]
            time_part = base_name.split('_')[1]
            raceNumber = ""

            isQuali = False
            postfix = ''
            if '_Q' in json_file:
                isQuali = True
                postfix = '_Q'

            # process files only after 2025
            filesFilter = os.path.join(input_dir,constants.processFilesFilter)

            if (json_file < filesFilter):
                continue

            # skipp Quali files from same day but earlier hour
            if isQuali and (date_part == sameDayQuali):
                continue
            
            #try different json encodings (might change after FTP json file update)
            data = None
            try:
                with open(json_file, 'r', encoding='utf-16-le') as file:
                    data = json.load(file)
            except Exception as e:
                warning = 1
                # print(f"Error reading file: {json_file} in UTF-16-LE. {e}. Trying to read in UTF-16")

            if not data:
                try:
                    with open(json_file, 'r', encoding='utf-16') as file:
                        data = json.load(file)
                except Exception as e:
                    warning = 1
                    # print(f"Error reading file: {json_file} in UTF-16. {e}")                    

            if not data:
                print(f"!! Could not read FILE: {json_file}")
                continue

            if data:                
                # skipp not valid files (session held but no valid best laps recorded)
                if data['sessionResult']['bestlap'] == 0:
                    continue
                
                # skipp if Open session
                serverName = data.get('serverName')
                if ("open" in serverName.lower()):
                    continue

                # get server name
                if (serverName):
                    seriesDir = serverName.split('|')[1].strip()
                else:
                    seriesDir = "unknown"                
                
                # double space series naming exceptions
                if "  " in seriesDir.lower():
                    seriesDir = seriesDir.replace("  ", " ")

                # Week League
                # determine race number by time the race was held
                isWeekLeague = False
                if "week league" in seriesDir.lower():
                    isWeekLeague = True
                # week LEAUGE exceptions - wrong name was gnerated in the FTP, server was set with spelling issue
                if isWeekLeague:
                    week_league_str = "WEEK LEAGUE"
                    if isWeekLeague:
                        seriesDir = seriesDir.upper().replace("WEEK LEAUGE", week_league_str).replace("  ", " ")

                    # calculate week league reace number (exclude isQuali)                                              
                    if isWeekLeague and not isQuali:
                        if (date_part == sameDayRace):
                            raceIndex = 1
                        else:
                            raceIndex = 2
                        sameDayRace = date_part
                    
                    if isWeekLeague and not isQuali:
                        raceNumber = f" R{int(raceIndex)}"
                # Week League end

                #skipp multiple Qualis from the same day
                if isQuali:
                    sameDayQuali = date_part

                seriesDir = seriesDir.upper()    
                # output_dir = os.path.join(current_dir, output_phase1, seriesDir)
                output_dir2 = os.path.join(constants.files_results, seriesDir, 'csv')

                #print(f"\n Output dir: {output_dir}")

                short_name = data.get('trackName', 'unknown_track')
                base_output_name = f"{date_part}-{time_part}-{short_name}-{seriesDir}{raceNumber}{postfix}"
                output_csv_file2 = utilities.generate_unique_filename(output_dir2, base_output_name, extension="csv")       
                
                # skipp if file already exists (delete file manually if requires reporocess)
                if os.path.exists(output_csv_file2):
                    continue

                # min laps required for results
                lap_counts = [line['timing'].get('lapCount', 0) for line in data['sessionResult']['leaderBoardLines']]
                if lap_counts:
                    max_lap_count = max(lap_counts)
                    min_laps_required = max_lap_count * constants.driver_min_laps_to_be_classified_mult
                else:
                    min_laps_required = 0

                # results = []
                # results2 = []
                resultsV2 = []
                # resultsV2csv = []
                # best_lap_times = []
                first_driver_time = None
                first_driver_laps = max_lap_count
                first_driver_best_time_ms = 0

                for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
                    
                    #ResultRow V2 data
                    driverResult = entities.ResultRowV2()
                    driverResult.carId = line['car']['carId']
                    driverResult.raceNumber = line['car']['raceNumber']
                    driverResult.carModel = line['car']['carModel']
                    driverResult.carGroup = line['car']['carGroup']
                    driverResult.cupCategory = line['car']['cupCategory']                    
                    driverResult.isWetSession = data['sessionResult']['isWetSession']
                    driverResult.isSpectator = int(line["bIsSpectator"])
                    driverResult.missingMandatoryPitstop = line["missingMandatoryPitstop"]
                    
                    # ballast not always available
                    if 'ballastKg' in line['car']:
                        driverResult.ballastKg = line['car']['ballastKg']

                    # OLD Driver get
                    drivers = line['car']['drivers']                    
                    driver_names = [driver['lastName'] for driver in drivers]
                    driver_names_str = ", ".join(driver_names)
                    driverResult.driver = driver_names_str

                    player_ids = [driver['playerId'] for driver in drivers]
                    player_ids_str = ", ".join(player_ids)
                    driverResult.playerId = player_ids_str                    
                    
                    driver_name = ''
                    if len(player_ids) > 0:
                        driver_name = utilities.get_driver_name(player_ids[0], driversList)
                    else:
                        driver_name = driver_names_str

                    total_time_ms = line['timing']['totalTime']
                    best_lap_ms = line['timing'].get('bestLap', 0)
                    lap_count = line['timing'].get('lapCount', 0)

                    if best_lap_ms >= total_time_ms:
                        best_lap_ms = 0

                    # print("for loop \n")

                    # skipp spectators
                    # if (lap_count == 0):
                    if driverResult.isSpectator == 1:
                        continue
                    elif not isQuali and lap_count < min_laps_required:
                        total_time_str = constants.dnf_text
                        best_lap_str = constants.dnf_text
                        points_awarded = 0
                    else:
                        if i == 0 and not isQuali:
                            first_driver_time = total_time_ms
                            first_driver_best_time_ms = best_lap_ms
                            total_time_str = utilities.convert_time(total_time_ms)
                        elif i == 0 and isQuali:    
                            first_driver_time = best_lap_ms
                            first_driver_best_time_ms = best_lap_ms
                            total_time_str = utilities.convert_time(best_lap_ms)
                            total_time_ms = best_lap_ms
                        else:
                            if isQuali:
                                time_difference = best_lap_ms - first_driver_best_time_ms
                            else:
                                time_difference = total_time_ms - first_driver_time
                            timeDiffString = utilities.convert_time(time_difference)
                            
                            # sometimes there is negative value if total driver time was < than total time of the winner
                            # for example when joining race after start    
                            # in such case clear timing difference value, leave laps only
                            if ('-' not in timeDiffString):
                                timeDiffString = f"+{timeDiffString}"
                            else:
                                timeDiffString = ""

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


                    #driver results V2
                    driverResult.position = i + 1
                    driverResult.totalTimeString = total_time_str
                    driverResult.totalTimeMs = total_time_ms
                    driverResult.bestLap = best_lap_str
                    driverResult.laps = lap_count
                    driverResult.points = points_awarded
                    resultsV2.append(driverResult)

                    # best_lap_times.append(best_lap_ms)

                    # looping drivers END

                # recalculate total time for all drivers                
                if not isQuali:
                    resultsV2 = utilities.recalculate_total_time(resultsV2)

                # points calculation : maxPoints = drivers count + 1
                maxPointsV2 = resultsV2.__len__()
                for i, r in enumerate(resultsV2):
                    if not (r.points == 0):
                        r.points = maxPointsV2 - i    

                # save results csv file
                utilities.save_csv_results(output_csv_file2, output_dir2, resultsV2)

                print(f"output_csv_file: {output_csv_file2}")

                # clear related V2 files if found something to be processed - this allows to execute steps to process files
                #delete _beforePenalties - to force applyPenalties again
                beforePenaltiesFile2 = output_csv_file2.replace(".csv", f"_beforePenalties.csv")                
                if os.path.exists(beforePenaltiesFile2):
                    os.remove(beforePenaltiesFile2)

                # delete related graphic files
                graphicResultFolder = os.path.join(os.path.dirname(os.path.dirname(output_csv_file2)), 'png')
                graphicFileName2 = os.path.basename(output_csv_file2).replace(".csv", f".png")                
                graphicFile2 = os.path.join(graphicResultFolder, graphicFileName2)
                if os.path.exists(graphicFile2):
                    os.remove(graphicFile2)
                graphicFileBeforePenalties2 = graphicFile2.replace(".png", f"_beforePenalties.png")
                if os.path.exists(graphicFileBeforePenalties2):
                    os.remove(graphicFileBeforePenalties2)                
                
                # delete general classification file to force reprocessing with new results
                GcCsvFile = utilities.generate_GC_file2_csv(output_dir2)
                if os.path.exists(GcCsvFile):
                    os.remove(GcCsvFile)
                GcPngFile = utilities.generate_GC_file2_png(output_dir2)
                if os.path.exists(GcPngFile):
                    os.remove(GcPngFile)        

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {json_file}: {e}")
        except KeyError as e:
            print(f"Missing key in JSON file {json_file}: {e}")
        except Exception as e:
            print(f"Process Results Phase1 - An error occurred processing file {json_file}: {e}")
            