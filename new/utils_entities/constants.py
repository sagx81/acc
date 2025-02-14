
import os
import csv
import json
import requests

from utils_entities import entities
from utils_entities import track_data

# from new.utils_entities import entities
# from new.utils_entities import track_data

points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2]


color_dnf = "red"
color_default = "#191919"
color_magenta = "magenta"

dsq_text = "DSQ"
dnf_text = "DNF"
# text_lap = "Okrażenie"
# text_laps = "Okrążenia"
text_lap = "Okr."
text_laps = "Okr."


# tracks = "Barcelona 
# Brands Hatch 
# Hungaroring 
# Misano 
# Monza 
# Nürburgring 
# Paul Ricard 
# Silverstone 
# Spa-Francochamps 
# Zandvoort 
# Zolder 
# Snetterton 
# Oulton Park 
# Donington Park
# Kyalami  
# Suzuka Circuit
# Laguna Seca
# Mount Panorama
# IMOLA
# Watkins Glen 
# COTA
# Indianapolis
# Circuit Ricardo Tormo
# RedBull Ring"

# online / web
drivers_web = "https://script.googleusercontent.com/macros/echo?user_content_key=LyuW03w8EuhJIzOkWPhbTRUzPG8lHG1GRQHA9jDwgXeze8yE4LWE2fyFJRcuZQwE2ecA4gQd5eB2lv77hZusmDTWH_yXNZhfm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnIMcFqZ4NRP4V9dkDbDfGqP3H1XDEV0PUFNGKS__Ipk73m3BsCic2BHaTrdxilTDGH8_RHSnmqSsHMOr95VxP6_b3lj62okUAQ&lib=MSdb85PJGIoSjHGusMzot873GRJM68q9Q"
tracks_web = "https://script.googleusercontent.com/macros/echo?user_content_key=punHLEL_HTf0TPMFDivsrJ6VbRM6M4wcia0LZQsCHyHBtVzeZqw7NH3OHxqaZs66Fe61kW3dZHlTXL6T2GM8WgazLDxn5THgm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnESQPHwrIqDrspbZcwcyGUWNpg-j7QbH1aWBkOboVyd3OrPhuEWso0Ev8_rbr7QQsQdcwg74D7Hb22NpqdVDrr3blv1BIAhc4w&lib=M_NydfZsakw_hgQy0L_PP-73GRJM68q9Q"
penalties_web = "https://docs.google.com/spreadsheets/d/1uLbXwCfIWfcnCMoQhm8L2phnhSOQgbfXHRf_WZeJaKM/edit?gid=0#gid=0"
cars_web = "https://docs.google.com/spreadsheets/d/10pfmrTH4C9_cLfGPja-5k97HfHKSRhd1jsDCVlmh6Bg/edit?gid=0#gid=0"

current_dir = os.getcwd()
files_from_ftp = os.path.join(current_dir, "files_from_ftp")
files_result_phase_1 = os.path.join(current_dir, "files_results_phase_1")
files_result_phase_2 = os.path.join(current_dir, "files_results_phase_2")
files_result_phase_3 = os.path.join(current_dir, "files_results_phase_3")
files_individual_graphic = os.path.join(current_dir, "files_result4_individual_graphics")

processedFilesCSV = os.path.join(current_dir, files_result_phase_1, "processed_files.csv")
output_phase1 = os.path.join(current_dir, "output_phase1")
process_apply_changes = current_dir
# process_apply_changes = os.path.join(current_dir, "process_results_phase2_penalties_apply")
process_graphic_individual = os.path.join(current_dir, "process_results_phase4_graphics")
# process_GC_phase1 = os.path.join(current_dir, "process_GC_phase1")
process_GC_phase1 = os.path.join(current_dir, "process_results_phase3_general_classification", "process_GC_phase1")
drivers_file = os.path.join(current_dir, "entities", "drivers.json")

logoFolder = os.path.join(process_graphic_individual, "files", "Logo")


graphicHeaders = ['Pozycja', 'Kierowca', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty']
graphicHeadersStars = ['Pozycja', 'Kierowca', 'Team', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty']

columnWidths = [170, 500, 400, 400, 250, 250]
columnWidthsStars = [100, 400, 420, 400, 215, 215, 215]
    

# def get_points_table():
#     return points

# # def points_awarded_for_position(position: int) -> int:
# #     if position < 1 or position > len(points):
# #         return 0
# #     return points[position - 1]


# def convert_time(ms):
#     hours = int(ms // 3600000)
#     minutes = int(ms // 60000)
#     seconds = int((ms % 60000) // 1000)
#     milliseconds = int(ms % 1000)
#     if (hours > 0):
#         return f"{hours}:{minutes:02}:{seconds:02}:{milliseconds:03}"
#     else:
#         return f"{minutes:02}:{seconds:02}:{milliseconds:03}"


# def get_results_from_csv(csv_file: str, inovkedBy: str):
#     results = []
    
#     with open(csv_file, mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         # print(f"*** Prepare Results list => Processing file --{inovkedBy}--: {csv_file.split('/')[-1]}\n")


#         for row in reader:
#             #skip header
#             # if (i == 0):  # no indexing available in the DictReader
#             #     continue

#             # if row['Position'] == 'Position':  # Pomijanie nagłówka
#             #     continue

#             # print(f"Row: {row}  ")

#             # getting by 'fieldName' skips first row

#             position = int(row['Position'])
#             driver = row['Driver']                
#             timing = str(row['Total time']) 
#             totalTimeMiliseconds = 0
#             # if (row['Total time ms']):
#             #     totalTimeMiliseconds = int(row['Total time ms'])            
#             bestLap = row['Best lap']
#             laps = int(row['Laps'])
#             driverPoints = int(row['Points'])        
#             totalTimeString = '' 
#             # if (row['Total time ms']):
#             #     totalTimeString = convert_time(totalTimeMiliseconds)

#             results.append(entities.ResultRow(position, driver, timing, totalTimeMiliseconds, totalTimeString, bestLap, laps, driverPoints))
            
#     # print(f"** Results prepared ** \n")
#     return results

# def get_fastest_lap(results):
#     fastest_lap_time = None
#     for row in results:
#         if fastest_lap_time is None or row.bestLap < fastest_lap_time:
#             fastest_lap_time = row.bestLap
#     return fastest_lap_time


# def get_track_name(track):
#     # print(f"for track info: {track}")
#     track_name = track
#     track_info = track_data.track_data.get(track, {})
#     # print(f"track info: {track_info}")
#     if track_info:
#         track_name = track_info.get('name', track)
#     return track_name


# def get_web_drivers():
#     # The API endpoint
#     url = "https://script.googleusercontent.com/macros/echo?user_content_key=3g5IKkMC0n8jyhO7VwdGPhnx2RWv7MjSKjeTHhFx07mdCMdfpWDNO-7iz2meYzRDZOhqhe5Clzu3uLiR_URnzX7cY2WY2gr-m5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnIMcFqZ4NRP4V9dkDbDfGqP3H1XDEV0PUFNGKS__Ipk73m3BsCic2BHaTrdxilTDGH8_RHSnmqSsHMOr95VxP6_b3lj62okUAQ&lib=MSdb85PJGIoSjHGusMzot873GRJM68q9Q"

#     # A GET request to the API
#     response = requests.get(url)

#     # Print the response
#     # print(response.json())

#     return response
    

# def get_driver_web(playerID, driversList):
#     for d in driversList:
#         if playerID == d.PlayerID:
#             return d.callsign

#     return None    



# def get_driver(fromResults):
#     json_file = drivers_file
    
#     # default name from results
#     driverName = fromResults  


#     try:
#         with open(json_file, 'r', encoding='utf-8') as file:
#             data = json.load(file)


#             # for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
#             #                     drivers = line['car']['drivers']
#             # print(f"l 130")

#             # name = data.get(['entries'],['drivers'])
#             for d in data['entries']:
#                 driversObject = d['drivers'][0]
#                 hasAlternateNames = False
#                 name = driversObject['lastName']

#                 if ('BAN' in name):
#                     continue

#                 # getattr does not work :/
#                 # x = getattr(driversObject, 'alternateNames', None)
#                 # print(f"X - {x}")
                
#                 names = []

#                 try: 
#                     names = driversObject['alternateNames']
#                 except Exception as e:
#                     hasAlternateNames = True

#                 names.append(name)
                
#                 namesLower = []
#                 for n in names:
#                     namesLower.append(n.lower().strip())

#                 if fromResults.lower().strip() in namesLower: #or fromResults.lower().strip() in name.lower().strip():
#                     driverName = name
#                     # print(f"Found driver: {driverName}")
#                     break
                

#                 # print(f"{driverName}")
#                 # print(f"{driversObject}")
                
            
#                 # names = []
#                 # names = getattr(driversObject, 'alternateNames',[])
                    

#                 # if hasattr(driversObject, 'alternateNames'):
#                 #     # names = driversObject['alternateNames']
#                 #     names = getattr(driversObject, 'alternateNames')
#                 #     # names = driversObject.alternateNames
#                 #     print(f"names: {name} {names}")
#                     # names = driversObject['alternateNames']
    

#             file.close()

#     except Exception as e:
#         print(f"GET DRIVER - An error occurred processing file {json_file}: {e}")

#     # if driverName != fromResults:
#     #     print(f"found same drivers {driverName} - {fromResults}")

#     return driverName