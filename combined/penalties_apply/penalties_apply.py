import os
import glob
import csv
# import time
from datetime import datetime
import shutil
from collections import defaultdict
# from PIL import Image, ImageDraw, ImageFont


# +seconds
# dsq from current race (to the bottom of the list and 0 points)
# fault points - by stewards (not here)
# +positions?

class Penalty:
    def __init__(self, raceType, season, track, raceNumber, driver, penaltySeconds, penaltyPosition, isDsq):
        self.raceType = raceType
        self.season = season
        self.track = track
        self.raceNumber = raceNumber
        self.driver = driver
        self.penaltySeconds = penaltySeconds
        self.penaltyPosition = penaltyPosition
        self.isDsq = isDsq        

    def __repr__(self):
        return f"{self.raceType} {self.season} {self.track} {self.raceNumber} {self.driver} {self.penaltySeconds} {self.penaltyPosition} {self.isDsq}"


class ResultRow:
    def __init__(self, position, driver, timing, totalTimeMs, totalTimeString, bestLap, laps, points, isDsq=False):
        self.position = position
        self.driver = driver
        self.timing = timing
        self.totalTimeMs = totalTimeMs
        self.totalTimeString = totalTimeString
        self.bestLap = bestLap
        self.laps = laps
        self.points = points
        self.isDsq = isDsq

    def __repr__(self):
        return f"Pos: {self.position}, Driver: {self.driver}, Timing: {self.timing}, TotalTimeMs: {self.totalTimeMs}, TotalTime: {self.totalTimeString}, BestLap: {self.bestLap}, Laps: {self.laps}, Points:  {self.points}"


class DriverMap:
    def __init__(self, discord, race):
        self.fromDiscord = discord
        self.fromRace = race

    def __repr__(self):
        return f"{self.fromDiscord} {self.fromRace}"

def is_penalty_valid_for_race(penalty, directory, file):
    # print(f"penalty: {penalty}")
    # print(f"directory: {directory}, file: {file}")

    if (penalty.raceType.lower() == "wl"):
        raceTypeCompare = "week league"
    else:
        raceTypeCompare = penalty.raceType

    # print(f"raceTypeCompare: {raceTypeCompare}")
    if ((str(directory.lower()).find(penalty.raceType.lower()) >= 0 or str(directory.lower()).find(raceTypeCompare) >= 0)
        and str(directory.lower()).find(penalty.season.lower()) >= 0
        and str(file.lower()).find(penalty.track.lower()) >= 0 
        and str(file.lower()).find(penalty.raceNumber.lower()) >= 0):
        return True


def convert_time(ms):
    hours = int(ms // 3600000)
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    if (hours > 0):
        return f"{hours}:{minutes:02}:{seconds:02}:{milliseconds:03}"
    else:
        return f"{minutes:02}:{seconds:02}:{milliseconds:03}"


def convert_time_to_miliseconds(time):
    timeSplit = time.split(':')
    timeMiliseconds = 0

    if (len(timeSplit) == 3):
        timeMiliseconds = int(timeSplit[0]) * 60000 + int(timeSplit[1]) * 1000 + int(timeSplit[2])
    elif (len(timeSplit) == 4):
        timeMiliseconds = int(timeSplit[0]) * 3600000 + int(timeSplit[1]) * 60000 + int(timeSplit[2]) * 1000 + int(timeSplit[3])

    return timeMiliseconds



# def find_project_root(start_path, target_dir_name="acc-race-results"):
#     current_path = start_path
#     while True:
#         if os.path.basename(current_path) == target_dir_name:
#             return current_path
#         parent_path = os.path.dirname(current_path)
#         if parent_path == current_path:
#             raise FileNotFoundError(f"Katalog {target_dir_name} nie został znaleziony w ścieżce: {start_path}")
#         current_path = parent_path

def apply_penalties():

    # Ustalanie katalogu głównego projektu
    inputResultsFolder = "output_phase1"
    applyPenaltiesFolder = "penalties_apply"
    # current_dir = os.getcwd()
    # project_root = os.path.dirname(current_dir) 
    project_root = os.getcwd() 

    # Definiowanie dynamicznych ścieżek do katalogów wejściowych, wyjściowych oraz do plików czcionki i tła
    penalties_csv = os.path.join(project_root,applyPenaltiesFolder, "penalties.csv")
    input_dirs = os.path.join(project_root, inputResultsFolder)
    # input_dirs = os.path.join(project_root, "acc", "output")

    # output_dir = os.path.join(project_root, "acc", "output", "Week League")
    # background_image = os.path.join(project_root, "files", "background", "general classification.jpg")
    # font_path = os.path.join(project_root, "files", "fonts", "BigShouldersDisplay-Bold.ttf")
    # output_csv_file = os.path.join(project_root, "acc", "output", "Week League", "klasyfikacja_generalna.csv")
    # logo_image = os.path.join(project_root, "files", "Logo", "WL-GT3.png")
    # processed_files_log = os.path.join(project_root, "acc", "output", "Week League", "processed_files.txt")

    # Funkcja generująca unikalną nazwę pliku
    # def generate_unique_filename(output_dir, base_name, extension="png"):
    #     counter = 1
    #     output_file = os.path.join(output_dir, f"{base_name}.{extension}")
    #     while os.path.exists(output_file):
    #         output_file = os.path.join(output_dir, f"{base_name}({counter}).{extension}")
    #         counter += 1
    #     return output_file

    # Inicjalizacja struktury danych do przechowywania wyników
    general_classification = defaultdict(int)

    results = []
    penalties = []
    winnerTime = ""
    winnerTimeMiliseconds = 0


    # Wczytanie listy przetworzonych plików
    # processed_files = set()
    # if os.path.exists(processed_files_log):
    #     with open(processed_files_log, 'r', encoding='utf-8') as file:
    #         processed_files = set(line.strip() for line in file)

    # Przetwarzanie każdego pliku CSV w katalogu wejściowym
    # for seriesDir in glob.glob(os.path.join(input_dirs, "")):

    dirs = glob.glob(os.path.join(input_dirs, "*"))
    # print(f"{dirs}")


    # prepare penalties
    print("\n------------\n")
    # penaltiesCsv = os.path.join(penalties_dir, "penalties.csv")
    penalties = []




    try:
        with open(penalties_csv, mode='r', encoding='utf-8') as pFile:
            pReader = csv.DictReader(pFile)
            for r in pReader:
                penalties.append(Penalty(r['RaceType'], r['Season'], r['Track'], r['RaceNumber'], r['Driver'], int(r['SecondsPenalty']), int(r['PositionPenalty']), float(r['IsDSQ'])))

    except Exception as e:
                print(f"An error occurred processing file {penalties_csv}: {e}")


    # prepare drivers map (TODO move to separate file)
    driversMap = [DriverMap("Sitek2453", "sitek1410")]
    driversMap.append(DriverMap("ARN | Kielkozaur #88", "Kielkozaur"))

    for input_dir in dirs:
        for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
            # if csv_file in processed_files:
            #     print(f"Plik już przetworzony: {csv_file}")
            #     continue

            applyPenalties = False
            # print(f"penalties: {penalties}")
            # print(f"csv_file: {csv_file}")
            for penalty in penalties:
                if (is_penalty_valid_for_race(penalty, input_dir, csv_file)): 
                    applyPenalties = True

            # print(f"apply penalties: {applyPenalties}")
            if (not applyPenalties):
                print(f" \n** Penalties DO NOT apply for: {csv_file.split('/')[-1]}\n")
                continue

            try:
                if ("penalties" in csv_file.lower() or "copy" in csv_file.lower()) :
                    continue
                # prepare driver objects
                with open(csv_file, mode='r', encoding='utf-8') as file:

                    results = []
                    reader = csv.DictReader(file)
                    winnerTime = ""
                    winnerTimeMiliseconds = 0
                    # print(f"{reader}")

                    print(f"\n\n\n*** Processing file: {csv_file.split('/')[-1]}\n")

                    for row in reader:
                        # print(f"{row}")
                        if row['Position'] == 'Position':  # Pomijanie nagłówka
                            continue
                    
                        if row['Position'] == '1':
                            # winnerTime = row['Laczny czas']
                            winnerTime = row['Total time']

                        # print("--------")

                        # print(f"winner time: {winnerTime}")
                        winnerTimeMiliseconds = convert_time_to_miliseconds(winnerTime)
                        # print(f"winner time: {winnerTimeMiliseconds}")


                        position = int(row['Position'])
                        driver = row['Driver']                
                        timing = str(row['Total time'])  #str(row['Laczny czas'])
                        
                        # bestLap = row['Naj. okrazenie']
                        bestLap = row['Best lap']
                        laps = row['Laps']
                        # laps = row['Okrazenia']
                        points = int(row['Points'])

                        totalTime = 0
                        timingMiliseconds = 0

                        # print(f"timing: {timing}")
                        # GT3
                        if ("gt3" in input_dir.lower()):
                            if (timing.find(' ') > 0):
                                if (timing.split(' ')[1][0].isdigit()):
                                    timeStr = timing.split(' ')[1]
                                    timingMiliseconds = convert_time_to_miliseconds(timeStr)
                                elif (timing.split(' ')[1][0] == 'o'):
                                    extraLaps = timing.split(' ')[0].replace('+', '')                        
                                    timingMiliseconds = int(extraLaps) * convert_time_to_miliseconds(bestLap)
                            # elif (timing.find('DNF') > 0):
                            elif (position > 1):
                                # 24h if DNF to have hight miliseconds count for positions calculation
                                timingMiliseconds = (24 * 3600000)
                                points = 0

                            totalTimeMiliseconds = winnerTimeMiliseconds + timingMiliseconds
                        
                        # WL
                        elif ("week league" in input_dir.lower()):
                            if (position == 1):
                                totalTimeMiliseconds = winnerTimeMiliseconds
                            if (timing.find('(') > 0):
                                firstPart = timing.split('(')[0]
                                secondPart = timing.split('(')[1]
                                if ("+" in secondPart):
                                    totalTimeMiliseconds = convert_time_to_miliseconds(firstPart)
                                elif (secondPart[0].isdigit()):
                                    extraLaps = secondPart.split(' ')[0]
                                    timingMiliseconds = int(extraLaps) * convert_time_to_miliseconds(bestLap)
                                    totalTimeMiliseconds = winnerTimeMiliseconds + timingMiliseconds
                            # elif (timing.find('DNF') > 0):                        
                            elif (position > 1):
                                # 24h if DNF to have hight miliseconds count for positions calculation
                                timingMiliseconds = (24 * 3600000)
                                points = 0   
                                totalTimeMiliseconds = winnerTimeMiliseconds + timingMiliseconds
            
                        

                        # print(f"time: {timingMiliseconds}")
                        # print(f"total time: {totalTimeMiliseconds}") 
                        # print(f"total time string: {convert_time(totalTimeMiliseconds)} \n")              

                    
                        totalTimeString = convert_time(totalTimeMiliseconds)
                        # result = ResultRow(position, driver, timing, totalTime, bestLap, laps, points)
                        results.append(ResultRow(position, driver, timing, totalTimeMiliseconds, totalTimeString, bestLap, laps, points))

                    
                    
                    # #penalties
                    # print("\n------------\n")
                    # penaltiesCsv = os.path.join(input_dir, "penalties.csv")
                    # try:
                    #     penalties = []
                        
                    #     with open(penaltiesCsv, mode='r', encoding='utf-8') as pFile:
                    #         pReader = csv.DictReader(pFile)
                    #         for r in pReader:
                    #             penalties.append(Penalty(r['RaceType'], int(r['Season']), r['Track'], int(r['RaceNumber']), r['Driver'], int(r['SecondsPenalty']), int(r['PositionPenalty']), float(r['IsDSQ'])))
                        
                    print("Penalties")
                    # for pen in penalties:
                    #     print(f"{pen}")
                    
                    # print(f"{results}")

                    # penalties
                    # penalties.append(Penalty("WL", "suzuka", 1, "KejsPower", 30, 0, True))
                    # penalties.append(Penalty("WL", "suzuka", 1, "Sagxx", 30, 0, False))
                    # penalties.append(Penalty("WL", "suzuka", 1, "Kielkozaur", 0, 1, False))

                    # results.sort(key=lambda x: x.totalTime);

                    # drivers mapping
                    
                    print("\n---Before stewards from results -----\n")
                    for res in results:
                        print(f"{res}")

                    # time penalties
                    for penalty in penalties:

                        # print(f"penalty is valid?: {penalty}")

                        if (not is_penalty_valid_for_race(penalty, input_dir, csv_file)):
                            continue                    

                        print(f"\n Applying penalty {penalty}")

                        for driver in results:       
                            driverRaceName = ""
                                
                            if (not penalty.driver.lower() == driver.driver.lower()):                            
                                continue
                                
                            # DSQ
                            if (penalty.isDsq):
                                driver.points = 0
                                driver.totalTimeMs = 24 * 36000000 + driver.totalTimeMs
                                driver.totalTimeString = convert_time(driver.totalTimeMs)
                                driver.isDsq = True
                            else:
                                driver.totalTimeMs += (penalty.penaltySeconds * 1000)
                                driver.totalTimeString = convert_time(driver.totalTimeMs)
                            break
                    
                    
                    # set position after penalties                         
                    points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2, 1, 1, 1, 1, 1]
                    sortedResults = sorted(results, key=lambda x: x.totalTimeMs)
                    winnerTimeMsAfterPenalties = 0
                    
                    # print("\n---Before stewards from drivers (sorted) -----\n")
                    # for res in sortedResults:
                    #     print(f"{res}")

                    for res in sortedResults:
                        if (sortedResults.index(res) == 0):
                            winnerTimeMsAfterPenalties = convert_time_to_miliseconds(res.totalTimeString)
                            res.timing = convert_time(winnerTimeMsAfterPenalties)
                        else:
                            res.timing = convert_time(res.totalTimeMs-winnerTimeMsAfterPenalties)
                        
                        # print(f"position: {res.position} vs {sortedResults.index(res) + 1}")
                        res.position = sortedResults.index(res) + 1
                        if (res.points != 0 and res.position <= len(points)):
                            res.points = points[res.position - 1]                        
                        else:
                            res.points = 0

                    # set points after penalties ??


                    print("\n---After stewards-----\n")
                    for res in sortedResults:
                        print(f"{res}")

                    # save to file
                    try:
                        # make copy 
                        # shutil.copyfile(csv_file, csv_file.replace(".csv", f"_beforePenalties_{str(datetime.now())}.csv"))

                        fileRows = [] #[{'Pozycja', 'Kierowca', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty'}]
                        for res in sortedResults:                            

                            if ("DNF" not in res.bestLap):
                                lapsMoreThanWinner = (res.totalTimeMs - winnerTimeMsAfterPenalties) / convert_time_to_miliseconds(res.bestLap)
                            
                            # print(f"laps more than winner: {lapsMoreThanWinner}")

                            # print(f"best lap: {res.bestLap}")

                            if (res.position == 1):
                                timeStr = res.timing
                            elif (res.isDsq):
                                timeStr = "DSQ"
                            elif ("DNF" in res.bestLap):
                                timeStr = "DNF"
                            elif (int(lapsMoreThanWinner) == 1):
                                timeStr = f"+{int(lapsMoreThanWinner)} okrążenie"
                            elif (int(lapsMoreThanWinner) > 1):
                                timeStr = f"+{int(lapsMoreThanWinner)} okrążenia"
                            else:
                                timeStr = f"+ {res.timing}"
                            fileRows.append([res.position, res.driver, timeStr, res.bestLap, res.laps, res.points])

                        fileRows.insert(0, ['Position', 'Driver', 'Total time', 'Best lap', 'Laps', 'Points'])
                        
                        output_csv_file = csv_file.replace(".csv", "_penalties_applied.csv")
                        # output_csv_file = csv_file
                        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csvFile:
                            writer = csv.writer(csvFile)
                            writer.writerows(fileRows)    
                    
                    except Exception as e:
                        print(f"An error occurred saving {csv_file}: {e}")
                    
            except Exception as e:
                print(f"An error occurred processing file {csv_file}: {e}")
