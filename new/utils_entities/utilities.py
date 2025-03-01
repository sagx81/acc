import os
import csv
import requests
import json
from . import entities
from . import track_data
from . import constants

def convert_time(ms):
    hours = int(ms // 3600000)
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    if (hours > 0):
        return f"{hours}:{minutes:02}:{seconds:02}:{milliseconds:03}"
    else:
        return f"{minutes:02}:{seconds:02}:{milliseconds:03}"


def get_results_from_csv(csv_file: str, inovkedBy: str):
    results = []
    
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # print(f"*** Prepare Results list => Processing file --{inovkedBy}--: {csv_file.split('/')[-1]}\n")


        for row in reader:
            #skip header
            # if (i == 0):  # no indexing available in the DictReader
            #     continue

            # if row['Position'] == 'Position':  # Pomijanie nagłówka
            #     continue

            # print(f"Row: {row}  ")

            # getting by 'fieldName' skips first row

            position = int(row['Position'])
            driver = row['Driver']                
            timing = str(row['Total time']) 
            totalTimeMiliseconds = 0
            # if (row['Total time ms']):
            #     totalTimeMiliseconds = int(row['Total time ms'])            
            bestLap = row['Best lap']
            laps = int(row['Laps'])
            driverPoints = int(row['Points'])        
            totalTimeString = '' 
            # if (row['Total time ms']):
            #     totalTimeString = convert_time(totalTimeMiliseconds)

            results.append(entities.ResultRow(position, driver, timing, totalTimeMiliseconds, totalTimeString, bestLap, laps, driverPoints))
            
    # print(f"** Results prepared ** \n")
    return results


def get_results_from_csv2(csv_file, inovkedBy):
    results = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                driverResult = entities.ResultRowV2()


                # safe_cast('tst', int) # will return None
                # safe_cast('tst', int, 0) # will return 0

                driverResult.position = safe_cast(row['Position'],int,0)
                driverResult.driver = row['Driver']                
                driverResult.timing = str(row['Total time']) 
                driverResult.totalTimeString = str(row['Total time']) 
                driverResult.totalTimeMs = safe_cast(row['Total time ms'],int,0) 
                driverResult.bestLap = row['Best lap']
                driverResult.laps = safe_cast(row['Laps'],int,0)
                driverResult.points = safe_cast(row['Points'],int,0)
                driverResult.carId = safe_cast(row['Car ID'],int,0)
                driverResult.raceNumber = safe_cast(row['Race Number'],int,0)
                driverResult.carModel = safe_cast(row['Car Model'],int,0)
                driverResult.carGroup = safe_cast(row['Car Group'],int,0)
                driverResult.cupCategory = str(row['Cup Category'],int,0)
                driverResult.ballastKg = safe_cast(row['Ballast Kg'],int,0)
                driverResult.playerId = str(row['Player ID'])
                driverResult.isWetSession = safe_cast(row['Is Wet Session'],int,0)
                driverResult.isSpectator = safe_cast(row['Is Spectator'],int,0)
                driverResult.missingMandatoryPitstop = safe_cast(row['Missing Mandatory Pitstop'],int,0)

                results.append(driverResult)

    except Exception as e:
        print(f"Error: Reading from csv {csv_file} by {inovkedBy} : {e}")

    return results

def get_penalties_from_csv():
    penalties_csv = constants.penalties_file
    penalties = []
    try:
        with open(penalties_csv, mode='r', encoding='utf-8') as pFile:
            pReader = csv.DictReader(pFile)
            for r in pReader:
                penalties.append(entities.Penalty(r['RaceType'], r['Season'], r['Track'], r['RaceNumber'], r['Driver'], int(r['SecondsPenalty']), int(r['PositionPenalty']), float(r['IsDSQ'])))

    except Exception as e:
        print(f"Apply Penalties open penalties csv file - An error occurred reading penalties file {penalties_csv}: {e}")

    return penalties


def generate_unique_filename(output_dir, base_name, extension="png"):
    counter = 1
    output_file = os.path.join(output_dir, f"{base_name}.{extension}")
    # generate new file name if exists
    # while os.path.exists(output_file):
    #     output_file = os.path.join(output_dir, f"{base_name}({counter}).{extension}")
    #     counter += 1
    return output_file


def generate_GC_file(inputDir):
    output_csv_file_name = f"{os.path.basename(inputDir)}_GC.csv"
    output_csv_file = os.path.join(inputDir, output_csv_file_name)
    return output_csv_file


def get_fastest_lap(results):
    fastest_lap_time = None
    for row in results:
        if not row.bestLap == "00:00:000" and (fastest_lap_time is None or row.bestLap < fastest_lap_time):
            fastest_lap_time = row.bestLap
    return fastest_lap_time


def get_track_name(track):
    # print(f"for track info: {track}")
    track_name = track
    track_info = track_data.track_data.get(track, {})
    # print(f"track info: {track_info}")
    if track_info:
        track_name = track_info.get('name', track)
    return track_name


def get_web_drivers():
    # The API endpoint
    url = "https://script.googleusercontent.com/macros/echo?user_content_key=3g5IKkMC0n8jyhO7VwdGPhnx2RWv7MjSKjeTHhFx07mdCMdfpWDNO-7iz2meYzRDZOhqhe5Clzu3uLiR_URnzX7cY2WY2gr-m5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnIMcFqZ4NRP4V9dkDbDfGqP3H1XDEV0PUFNGKS__Ipk73m3BsCic2BHaTrdxilTDGH8_RHSnmqSsHMOr95VxP6_b3lj62okUAQ&lib=MSdb85PJGIoSjHGusMzot873GRJM68q9Q"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    # print(response.json())

    return response
    

def get_driver_web(playerID, driversList):
    for d in driversList:
        if playerID == d.PlayerID:
            return d.callsign

    return None    



def get_driver(fromResults):
    json_file = constants.drivers_file
    
    # default name from results
    driverName = fromResults  


    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)


            # for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
            #                     drivers = line['car']['drivers']
            # print(f"l 130")

            # name = data.get(['entries'],['drivers'])
            for d in data['entries']:
                driversObject = d['drivers'][0]
                hasAlternateNames = False
                name = driversObject['lastName']

                if ('BAN' in name):
                    continue

                # getattr does not work :/
                # x = getattr(driversObject, 'alternateNames', None)
                # print(f"X - {x}")
                
                names = []

                try: 
                    names = driversObject['alternateNames']
                except Exception as e:
                    hasAlternateNames = True

                names.append(name)
                
                namesLower = []
                for n in names:
                    namesLower.append(n.lower().strip())

                if fromResults.lower().strip() in namesLower: #or fromResults.lower().strip() in name.lower().strip():
                    driverName = name
                    # print(f"Found driver: {driverName}")
                    break
                

                # print(f"{driverName}")
                # print(f"{driversObject}")
                
            
                # names = []
                # names = getattr(driversObject, 'alternateNames',[])
                    

                # if hasattr(driversObject, 'alternateNames'):
                #     # names = driversObject['alternateNames']
                #     names = getattr(driversObject, 'alternateNames')
                #     # names = driversObject.alternateNames
                #     print(f"names: {name} {names}")
                    # names = driversObject['alternateNames']
    

            file.close()

    except Exception as e:
        print(f"GET DRIVER - An error occurred processing file {json_file}: {e}")

    # if driverName != fromResults:
    #     print(f"found same drivers {driverName} - {fromResults}")

    return driverName


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


def save_csv_file(output_csv_file, output_dir, results):
    try:
        print(f"output_csv_file: {output_csv_file}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_csv_file, mode='w+', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(results)
            csv_file.close()
    except Exception as e:
        print(f"An error occurred saving file {output_csv_file}: {e}")


def save_csv_results(output_csv_file, output_dir, resultsV2):
    
    # build csv output file
    reultsCsv = []
    for i,r in enumerate(resultsV2):
        reultsCsv.append([
            r.position,
            r.driver,
            r.totalTimeString,
            r.totalTimeMs,
            r.bestLap,
            r.laps,
            r.points,                        
            r.carId,
            r.raceNumber,
            r.carModel,
            r.carGroup,
            r.cupCategory,
            r.ballastKg,
            r.playerId,
            r.isWetSession,
            r.isSpectator,
            r.missingMandatoryPitstop

        ])                    
    reultsCsv.insert(0, ['Position', 'Driver', 'Total time', 'Total time ms', 'Best lap', 'Laps', 'Points', 'Car ID', 'Race Number', 'Car Model', 'Car Group', 'Cup Category', 'Ballast Kg', 'Player ID', 'Is Wet Session', 'Is Spectator', 'Missing Mandatory Pitstop'])
    
    save_csv_file(output_csv_file, output_dir, reultsCsv)



def recalculate_total_time(results):
    for i,row in enumerate(results):

        if i == 0:
            continue

        previousTotalTimeMs = results[i-1].totalTimeMs
        previousLapsCount = results[i-1].laps
        previousPenaltyMs = results[i-1].penaltyMs

        ignoreLaps = True
        if (row.isDsq):
            row.totalTimeString = "DSQ"
        elif ("DNF" in row.bestLap):
            row.totalTimeString = "DNF"        
        elif row.position > 1 and row.totalTimeMs < previousTotalTimeMs and previousPenaltyMs > 0:
            ignoreLaps = False
            row.totalTimeString = f"+{convert_time(abs(row.totalTimeMs - previousTotalTimeMs + (2*previousPenaltyMs)))}"
        elif (previousTotalTimeMs > 0):            
            ignoreLaps = False
            row.totalTimeString = f"+{convert_time(abs(row.totalTimeMs - previousTotalTimeMs))}"
            
        # + laps
        if not ignoreLaps and row.laps > 0 and row.laps - previousLapsCount < 0:
                row.totalTimeString = row.totalTimeString + f" (+ {abs(row.laps - previousLapsCount)} {constants.text_lap})"

        # if previousPenaltyMs > 0:
        #     row.totalTimeString = row.totalTimeString + f" +{convert_time(previousPenaltyMs)}            

        # previousTotalTimeMs = row.totalTimeMs
        # previousLapsCount = row.laps
        # previousPenaltyMs = row.penaltyMs

    return results


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

# def recalculate_total_time(results):
#     previousTotalTimeMs = 0
#     previousLapsCount = 0
#     previousPenaltyMs = 0
#     for row in results:
#         ignoreLaps = True
#         if (row.isDsq):
#             row.totalTimeString = "DSQ"
#         elif ("DNF" in row.bestLap):
#             row.totalTimeString = "DNF"        
#         elif row.position > 1 and row.totalTimeMs < previousTotalTimeMs and previousPenaltyMs > 0:
#             ignoreLaps = False
#             row.totalTimeString = f"+{convert_time(abs(row.totalTimeMs - previousTotalTimeMs + (2*previousPenaltyMs)))}"
#         elif (previousTotalTimeMs > 0):            
#             ignoreLaps = False
#             row.totalTimeString = f"+{convert_time(abs(row.totalTimeMs - previousTotalTimeMs))}"
            
#         # + laps
#         if not ignoreLaps and row.laps > 0 and row.laps - previousLapsCount < 0:
#                 row.totalTimeString = row.totalTimeString + f" (+ {abs(row.laps - previousLapsCount)} {constants.text_lap})"

#         # if previousPenaltyMs > 0:
#         #     row.totalTimeString = row.totalTimeString + f" +{convert_time(previousPenaltyMs)}
            

#         previousTotalTimeMs = row.totalTimeMs
#         previousLapsCount = row.laps
#         previousPenaltyMs = row.penaltyMs

#     return results
