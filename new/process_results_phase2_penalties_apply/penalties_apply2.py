import os
import glob
import shutil
# import csv
# from datetime import datetime
# from collections import defaultdict
# from utils_entities.constants import points
from utils_entities import constants
# from utils_entities import entities
from utils_entities import utilities


def apply_penalties():
        
    # series directories
    # input_dirs = constants.files_result_phase_1
    input_dirs = constants.files_results
    dirs = glob.glob(os.path.join(input_dirs, "*"))

    # prepare penalties
    print("\n*** Penalties 2 \n")
    penalties = utilities.get_penalties_from_csv()

    for input_dir in dirs:
        for csv_file in glob.glob(os.path.join(input_dir, 'csv', "*.csv")):
    
            # skipp Qualifications
            if "_Q" in csv_file:
                continue

            # skipp penalties/copy files
            if ("penalties" in csv_file.lower() or "copy" in csv_file.lower()) :
                continue

            # skipp if penalties already applied (when _beforePenalties file exists for given csv)
            if os.path.exists(csv_file.replace(".csv", f"_beforePenalties.csv")):
                continue

            # check if penalties apply to current race
            applyPenalties = False
            validPenalties = []
            for penalty in penalties:
                if (utilities.is_penalty_valid_for_race(penalty, input_dir, csv_file)): 
                    validPenalties.append(penalty)
                    # applyPenalties = True
            
            if len(validPenalties) == 0:
                continue
            # if (not applyPenalties):
            #     continue


            try:

                # read results from phase1
                results = utilities.get_results_from_csv2(csv_file, "Penalties Apply")
                winnerLaps = results[0].laps

                # apply penalties
                for penalty in validPenalties:
                    for driver in results:                                   
                        
                        # find penalty driver
                        if (not penalty.driver.lower() == driver.driver.lower()):                            
                            continue

                        print(f"Applying penalty {penalty}")
    
                        # DSQ
                        if (penalty.isDsq):
                            driver.points = 0
                            driver.totalTimeString = constants.dsq_text
                            driver.timing = constants.dsq_text
                            driver.isDsq = True
                        else:
                            driver.totalTimeMs += (penalty.penaltySeconds * 1000)
                            driver.penaltyMs = (penalty.penaltySeconds * 1000)
                        break
                    
                # set position after penalties (sort by total time)                         
                sortedResults = sorted(results, key=lambda x: x.totalTimeMs)
                    
                #clear/reorder positions - separate tables to clearly separate 
                #   results,
                #   drivers with less laps than winner
                #   DNFs, 
                #   DSQs
                plusLapPositions = []
                dnfs = []
                dsqs = []

                # sorting results into proper arrays
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
                
                # sortedResult - original array - contains now only drivers withing same lap as winner
                # adding +lap drivers, DSQs and DNFs
                sortedResults.extend(sortedReorderPositions)
                sortedResults.extend(dsqs)
                sortedResults.extend(dnfs)
                
                # points and positions recalculate - after penalties
                maxPoints = len(sortedResults)
                for i, res in enumerate(sortedResults):
                    res.position = i + 1
                    if (res.points != 0):
                        res.points = maxPoints - i

                # recalculate total time str
                sortedResults = utilities.recalculate_total_time(sortedResults)

                # save to file
                try:
                    # make a copy of original file
                    fileCopy = csv_file.replace(".csv", f"_beforePenalties.csv")
                    if not os.path.exists(fileCopy): 
                        shutil.copyfile(csv_file, fileCopy)

                    utilities.save_csv_results(csv_file, constants.files_result_phase_1, sortedResults)

                    print("*** Penalties applied! ***")
                                    
                except Exception as e:
                    print(f"Apply Penalties save csv file - An error occurred saving {csv_file}: {e}")
                
            except Exception as e:
                print(f"2 Apply Penalties open csv file - An error occurred processing file {csv_file}: {e}")
