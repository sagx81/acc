import os
import glob
import shutil
import csv
from datetime import datetime
from collections import defaultdict
from utils_entities.constants import points
from utils_entities import constants
from utils_entities import entities
from utils_entities import utilities


def apply_penalties():

    # Ustalanie katalogu głównego projektu
    # inputResultsFolder = constants.files_result_phase_1
    # applyPenaltiesFolder = constants.process_apply_changes
    
    # project_root = os.getcwd() 

    # Definiowanie dynamicznych ścieżek do katalogów wejściowych, wyjściowych oraz do plików czcionki i tła
    # penalties_csv = os.path.join(project_root,applyPenaltiesFolder, "penalties.csv")
    # input_dirs = os.path.join(project_root, inputResultsFolder)
    penalties_csv = constants.penalties_file
    input_dirs = constants.files_result_phase_1

    results = []
    penalties = []
    winnerTime = ""

    dirs = glob.glob(os.path.join(input_dirs, "*"))


    # prepare penalties
    print("\n*** Penalties\n")
    penalties = []

    try:
        with open(penalties_csv, mode='r', encoding='utf-8') as pFile:
            pReader = csv.DictReader(pFile)
            for r in pReader:
                penalties.append(entities.Penalty(r['RaceType'], r['Season'], r['Track'], r['RaceNumber'], r['Driver'], int(r['SecondsPenalty']), int(r['PositionPenalty']), float(r['IsDSQ'])))

    except Exception as e:
        print(f"Apply Penalties open penalties csv file - An error occurred processing file {penalties_csv}: {e}")


    # prepare drivers map (TODO move to separate file)

    for input_dir in dirs:
        for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
    
            # skipp Qualifications
            if "_Q" in csv_file:
                continue

            applyPenalties = False
            for penalty in penalties:
                if (utilities.is_penalty_valid_for_race(penalty, input_dir, csv_file)): 
                    applyPenalties = True

            if (not applyPenalties):
                continue

            try:
                if ("penalties" in csv_file.lower() or "copy" in csv_file.lower()) :
                    continue
                # prepare driver objects
                with open(csv_file, mode='r', encoding='utf-8') as file:

                    results = []
                    reader = csv.DictReader(file)
                    winnerTime = ""
                    winnerLaps = 0

                    for row in reader:
                        if row['Position'] == 'Position':  # Pomijanie nagłówka
                            continue
                    
                        if row['Position'] == '1':
                            winnerTime = row['Total time']
                            winnerLaps = int(row['Laps'])

                        # if not row['Total time ms'] available - that means results are already reworked and penalties applied
                        if 'Total time ms' not in row or not row['Total time ms']:
                            break

                        position = int(row['Position'])
                        driver = row['Driver']                
                        timing = str(row['Total time'])  #str(row['Laczny czas'])
                        totalTimeMiliseconds = int(row['Total time ms'])

                        bestLap = row['Best lap']
                        laps = int(row['Laps'])
                        driverPoints = int(row['Points'])

                        totalTimeString = utilities.convert_time(totalTimeMiliseconds)
                        results.append(entities.ResultRow(position, driver, timing, totalTimeMiliseconds, totalTimeString, bestLap, laps, driverPoints))

                    # time penalties
                    for penalty in penalties:

                        if (not utilities.is_penalty_valid_for_race(penalty, input_dir, csv_file)):
                            continue                    

                        print(f"Applying penalty {penalty}")

                        for driver in results:       
                                
                            if (not penalty.driver.lower() == driver.driver.lower()):                            
                                continue
                                
                            # DSQ
                            if (penalty.isDsq):
                                driver.driverPoints = 0
                                driver.totalTimeString = constants.dsq_text
                                driver.isDsq = True
                            else:
                                driver.totalTimeMs += (penalty.penaltySeconds * 1000)
                                driver.totalTimeString = utilities.convert_time(driver.totalTimeMs)
                            break
                    
                    # set position after penalties                         
                    sortedResults = sorted(results, key=lambda x: x.totalTimeMs)
                    
                    #clear/reorder positions
                    plusLapPositions = []
                    dnfs = []
                    dsqs = []

                    for i, res in reversed(list(enumerate(sortedResults))):
                        if ("dnf" in res.timing.lower()):
                            dnfs.append(res)
                        elif res.isDsq or res.timing.lower() == "dsq":
                            dsqs.append(res)
                        elif int(res.laps) < int(winnerLaps):
                            plusLapPositions.append(res)                        
                        else:
                            continue
                        sortedResults.pop(i)
                        
                    sortedReorderPositions = []    
                    if plusLapPositions:
                        sortedReorderPositions = sorted(plusLapPositions, key=lambda x: (-x.laps, x.totalTimeMs))
                    
                    sortedResults.extend(sortedReorderPositions)
                    sortedResults.extend(dsqs)
                    sortedResults.extend(dnfs)
                    
                    maxPoints = len(sortedResults)
                    for res in sortedResults:
                        # new points calculation
                        i = sortedResults.index(res)
                        res.position = i + 1
                        if (res.driverPoints != 0):
                            res.driverPoints = maxPoints - i
                        else:
                            res.driverPoints = 0

                    # save to file
                    try:
                        # make a copy
                        fileCopy = csv_file.replace(".csv", f"_beforePenalties.csv")
                        if not os.path.exists(fileCopy): 
                        # shutil.copyfile(csv_file, csv_file.replace(".csv", f"_beforePenalties_{str(datetime.now())}.csv"))
                            shutil.copyfile(csv_file, fileCopy)

                        fileRows = []
                        lapsMoreThanWinner = 0 
                        for res in sortedResults:                            

                            if ("dnf" not in res.timing.lower()):
                                lapsMoreThanWinner = int(winnerLaps) - int(res.laps)
                            
                            # lapsLabel = "lap"
                            # if lapsMoreThanWinner > 1:
                            #     lapsLabel = "laps"

                            if (res.position == 1):
                                timeStr = res.timing
                            elif (res.isDsq):
                                timeStr = "DSQ"
                            elif ("DNF" in res.bestLap):
                                timeStr = "DNF"
                            elif (lapsMoreThanWinner >= 1):
                                timeStr = res.timing
                            else:
                                timeStr = f"{res.timing}"
                            fileRows.append([res.position, res.driver, timeStr, res.bestLap, res.laps, res.driverPoints])

                        print("*** Penalties applied! ***")

                        fileRows.insert(0, ['Position', 'Driver', 'Total time', 'Best lap', 'Laps', 'Points'])
                        
                        # output_csv_file = csv_file.replace(".csv", "_penalties_applied.csv")
                        output_csv_file = csv_file
                        with open(output_csv_file, mode='w+', newline='', encoding='utf-8') as csvFile:
                            writer = csv.writer(csvFile)
                            writer.writerows(fileRows)
                            csvFile.close()
                    
                    except Exception as e:
                        print(f"Apply Penalties save csv file - An error occurred saving {csv_file}: {e}")
                    
            except Exception as e:
                print(f"Apply Penalties open csv file - An error occurred processing file {csv_file}: {e}")
