
import os
import json
import glob
import csv
import datetime
from pathlib import Path

from utils_entities import constants
from utils_entities import utilities
from utils_entities import entities

#processed files
#from utils_entities.processed_files import ProcessedFile

current_dir = os.getcwd()
input_dir = constants.files_from_ftp
output_phase1 = constants.files_result_phase_1
results_phase1 = "process_results_phase1"
processedFiles = []
processedFilesCSV = os.path.join(current_dir, results_phase1, "processed_files.csv") 

def get_race_results():

    print("\n*** Processing FTP files phase - 1 \n")

    # processedFileHasValue = False
    # filesSorted = sorted(glob.glob(os.path.join(input_dir, "*.json")), key=os.path.getmtime, reverse=False)
    # path_object = Path(input_dir)
    # filesSorted = sorted(path_object.glob("*.json"), key=lambda item: item.name, reverse=True)
    # items = os.listdir(input_dir)

    items = glob.glob(os.path.join(input_dir, "*.json"))
    filesSorted = sorted(items, reverse=True)

    # previousRaceDay = ""   
    sameDayRace = ""
    sameDayQuali = ""

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
            filesFilter = os.path.join(input_dir,"250200_000000_0.json")

            if (json_file < filesFilter):
                continue


            # skipp Quali files from same day but earlier hour
            if isQuali and (date_part == sameDayQuali):
                continue
                        
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
            
            #try different json encodings (might change after FTP json file update)
            data = None
            try:
                with open(json_file, 'r', encoding='utf-16-le') as file:
                # with open(json_file, 'r', encoding='utf-8-sig') as file:
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

                # base_name = os.path.basename(json_file)
                # date_part = base_name.split('_')[0]
                # time_part = base_name.split('_')[1]
                
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
                    # elif isWeekLeague and isQuali:
                    #     sameDayQuali = date_part
                    
                    if isWeekLeague and not isQuali:
                        raceNumber = f" R{int(raceIndex)}"

                # Week League end

                #skipp multiple Qualis from the same day
                if isQuali:
                    sameDayQuali = date_part


                seriesDir = seriesDir.upper()    
                output_dir = os.path.join(current_dir, output_phase1, seriesDir)

                #print(f"\n Output dir: {output_dir}")

                short_name = data.get('trackName', 'unknown_track')

                # base_name = os.path.basename(json_file)
                # date_part = base_name.split('_')[0]
                # time_part = base_name.split('_')[1]

                # base_output_name = f"{short_name}-{seriesDir}{raceNumber}-{date_part}-{time_part}{postfix}"
                base_output_name = f"{date_part}-{time_part}-{short_name}-{seriesDir}{raceNumber}{postfix}"

                # output_image_file = generate_unique_filename(output_dir, base_output_name, extension="png")
                output_csv_file = utilities.generate_unique_filename(output_dir, base_output_name, extension="csv")

                # skipp if file already exists (delete file manually if requires reporocess)
                if os.path.exists(output_csv_file):
                    continue

                # min laps required for results
                lap_counts = [line['timing'].get('lapCount', 0) for line in data['sessionResult']['leaderBoardLines']]
                if lap_counts:
                    max_lap_count = max(lap_counts)
                    min_laps_required = max_lap_count * 0.8
                else:
                    min_laps_required = 0

                results = []
                results2 = []
                resultsV2 = []
                resultsV2csv = []
                best_lap_times = []
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
                    driverResult.isSpectator = line["bIsSpectator"]
                    driverResult.missingMandatoryPitstop = line["missingMandatoryPitstop"]
                    
                    # ballast not always available
                    if 'ballastKg' in line['car']:
                        driverResult.ballastKg = line['car']['ballastKg']

                    drivers = line['car']['drivers']
                    
                    driver_names = [driver['lastName'] for driver in drivers]
                    driver_names_str = ", ".join(driver_names)
                    driverResult.driver = driver_names_str

                    player_ids = [driver['playerId'] for driver in drivers]
                    player_ids_str = ", ".join(player_ids)
                    driverResult.playerId = player_ids_str                    
                    
                    # drivers = line['car']['drivers']
                    # driverNumber = line['car']['raceNumber']
                    # driverCar = line['car']['carModel']
                    # driver_names = [driver['lastName'] for driver in drivers]
                    # driver_names_str = ", ".join(driver_names)

                    total_time_ms = line['timing']['totalTime']
                    best_lap_ms = line['timing'].get('bestLap', 0)
                    lap_count = line['timing'].get('lapCount', 0)

                    if best_lap_ms >= total_time_ms:
                        best_lap_ms = 0

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
                            #TODO crash here : first_driver_time is none , 1st driver DNF - noo, it is about Quali
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
                    
                    
                    
                    # print("append results")
                    # print(f"{i}\n")
                    results2.append(entities.ResultRow(i + 1, driver_names_str, 0, total_time_ms, total_time_str, best_lap_str, lap_count, points_awarded))
                    # results.append([
                    #     i + 1,
                    #     driver_names_str,
                    #     total_time_str,
                    #     total_time_ms,
                    #     best_lap_str,
                    #     lap_count,
                    #     points_awarded
                    # ])

                    best_lap_times.append(best_lap_ms)
                
                # points calculation : maxPoints = drivers count + 1
                maxPoints = results2.__len__()
                for i, r in enumerate(results2):
                    if not (r.driverPoints == 0):
                        r.driverPoints = maxPoints - i                        

                # recalculate total time                
                if not isQuali:
                    results2 = utilities.recalculate_total_time(results2)

                # build csv output file
                for i,r in enumerate(results2):
                    results.append([
                        r.position,
                        r.driver,
                        r.totalTimeString,
                        r.totalTimeMs,
                        r.bestLap,
                        r.laps,
                        r.driverPoints
                    ])                    
                results.insert(0, ['Position', 'Driver', 'Total time', 'Total time ms', 'Best lap', 'Laps', 'Points'])




                # V2 points calculation : maxPoints = drivers count + 1
                maxPointsV2 = resultsV2.__len__()
                for i, r in enumerate(resultsV2):
                    if not (r.points == 0):
                        r.points = maxPointsV2 - i    

                # utilities.save_csv_results(output_csv_file, output_dir, resultsV2)



                # # build csv output file
                # for i,r in enumerate(resultsV2):
                #     resultsV2csv.append([
                #         r.position,
                #         r.driver,
                #         r.totalTimeString,
                #         r.totalTimeMs,
                #         r.bestLap,
                #         r.laps,
                #         r.points,                        
                #         r.carId,
                #         r.raceNumber,
                #         r.carModel,
                #         r.carGroup,
                #         r.cupCategory,
                #         r.ballastKg,
                #         r.playerId,
                #         r.isWetSession,
                #         r.isSpectator,
                #         r.missingMandatoryPitstopass

                #     ])                    
                # resultsV2.insert(0, ['Position', 'Driver', 'Total time', 'Total time ms', 'Best lap', 'Laps', 'Points', 'Car ID', 'Race Number', 'Car Model', 'Car Group', 'Cup Category', 'Ballast Kg', 'Player ID', 'Is Wet Session', 'Is Spectator', 'Missing Mandatory Pitstop'])
                
                # utilities.save_csv_file(output_csv_file, output_dir, resultsV2)

                # print("best lap")
                
                # if best_lap_times:
                #     fastest_lap_time = min(best_lap_times)
                #     fastest_lap_time_converted = utilities.convert_time(fastest_lap_time)
                # else:
                #     fastest_lap_time_converted = None

                print(f"output_csv_file: {output_csv_file}")

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                with open(output_csv_file, mode='w+', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(results)
                    csv_file.close()
                    # csv_file.writerows(results)

                # delete related graphic files
                csvFile = os.path.basename(output_csv_file)
                graphicFile = os.path.join(constants.files_individual_graphic, os.path.basename(output_dir),csvFile.replace(".csv", f".png"))
                if os.path.exists(graphicFile):
                    os.remove(graphicFile)
                graphicFileBeforePenalties = graphicFile.replace(".png", f"_beforePenalties.png")
                if os.path.exists(graphicFileBeforePenalties):
                    os.remove(graphicFileBeforePenalties)                
                beforePenaltiesFile = output_csv_file.replace(".csv", f"_beforePenalties.csv")                
                if os.path.exists(beforePenaltiesFile):
                    os.remove(beforePenaltiesFile)

                # delete general classification file to force reprocessing with new results
                GcFile = utilities.generate_GC_file(output_dir)
                if os.path.exists(GcFile):
                    os.remove(GcFile)

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

