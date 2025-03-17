
import os
import csv
import json
# import requests

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
# drivers_web = "https://script.googleusercontent.com/macros/echo?user_content_key=LyuW03w8EuhJIzOkWPhbTRUzPG8lHG1GRQHA9jDwgXeze8yE4LWE2fyFJRcuZQwE2ecA4gQd5eB2lv77hZusmDTWH_yXNZhfm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnIMcFqZ4NRP4V9dkDbDfGqP3H1XDEV0PUFNGKS__Ipk73m3BsCic2BHaTrdxilTDGH8_RHSnmqSsHMOr95VxP6_b3lj62okUAQ&lib=MSdb85PJGIoSjHGusMzot873GRJM68q9Q"
drivers_web_url = "https://script.googleusercontent.com/macros/echo?user_content_key=AehSKLjpDS7AEI8mjebZ8r6C7H9956QrAJcYEIT54kH4KNaQAktPGdWlIwM1avQWmVnDkLOr9V7GFsK4hDaAtmV016NbfJHIU6B5h9yvP1tYEvzRFZcrqw62NNrQOq7BuqLYZ62-YZjrZVPjesSRgkfdcMJm-onpPLtFx1uQwG0t8V5fZqMF9Hb6yz7oSm5Dc5bz1GS4kDdWh5Wg7kidsO18iJnii8uuywDcUcm5WeIKiDb8djNJAiYJzEuCKI1sE-OqtCkntAV8byFk1EZ9yrRsktLt9YA5fw&lib=MSdb85PJGIoSjHGusMzot873GRJM68q9Q"
tracks_web = "https://script.googleusercontent.com/macros/echo?user_content_key=punHLEL_HTf0TPMFDivsrJ6VbRM6M4wcia0LZQsCHyHBtVzeZqw7NH3OHxqaZs66Fe61kW3dZHlTXL6T2GM8WgazLDxn5THgm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnESQPHwrIqDrspbZcwcyGUWNpg-j7QbH1aWBkOboVyd3OrPhuEWso0Ev8_rbr7QQsQdcwg74D7Hb22NpqdVDrr3blv1BIAhc4w&lib=M_NydfZsakw_hgQy0L_PP-73GRJM68q9Q"
penalties_web = "https://docs.google.com/spreadsheets/d/1uLbXwCfIWfcnCMoQhm8L2phnhSOQgbfXHRf_WZeJaKM/edit?gid=0#gid=0"
cars_web = "https://docs.google.com/spreadsheets/d/10pfmrTH4C9_cLfGPja-5k97HfHKSRhd1jsDCVlmh6Bg/edit?gid=0#gid=0"
cars_logos = "https://www.carlogos.org/car-brands/"
# https://pngimg.com/

# sets minimal file name, before defined date files will not be taken by the process - season start might be set here
processFilesFilter = "250209_000000_0.json"

current_dir = os.getcwd()
utilsFolder = os.path.join(current_dir, "utils_entities")
files_from_ftp = os.path.join(current_dir, "files_from_ftp")
files_result_phase_1 = os.path.join(current_dir, "files_results_phase_1")
files_result_phase_2 = os.path.join(current_dir, "files_results_phase_2")
files_result_phase_3 = os.path.join(current_dir, "files_results_phase_3")
files_individual_graphic = os.path.join(current_dir, "files_result4_individual_graphics")
files_result_png = os.path.join(current_dir, "results","png")
files_result_csv = os.path.join(current_dir, "results","csv")
files_results = os.path.join(current_dir, "results")

processedFilesCSV = os.path.join(current_dir, files_result_phase_1, "processed_files.csv")
carsCsvFile = os.path.join(utilsFolder, "cars.csv")
driversOfflineFile = os.path.join(utilsFolder, "drivers_web.json")

# output_phase1 = os.path.join(current_dir, "output_phase1")
process_apply_changes = current_dir
# process_apply_changes = os.path.join(current_dir, "process_results_phase2_penalties_apply")
process_graphic_individual = os.path.join(current_dir, "process_results_phase4_graphics")
# process_GC_phase1 = os.path.join(current_dir, "process_GC_phase1")
process_GC_phase1 = os.path.join(current_dir, "process_results_phase3_general_classification", "process_GC_phase1")
drivers_file = os.path.join(current_dir, "utils_entities", "drivers.json")
penalties_file = os.path.join(current_dir, "penalties.csv")

logoFolder = os.path.join(process_graphic_individual, "files", "Logo")


graphicHeaders = ['Pozycja', 'Kierowca', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty']
graphicHeadersStars = ['Pozycja', 'Kierowca', 'Team', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty']
graphicFiles = os.path.join(current_dir, "graphic_files")
backgroundImagePath = os.path.join(graphicFiles, "background", "race results.png")
fontBoldPath = os.path.join(graphicFiles,"fonts", "BigShouldersDisplay-Bold.ttf")
seriesLogosFolder = os.path.join(graphicFiles,"Logo")
carLogosFolder = os.path.join(graphicFiles,"cars")

# columnWidths = [100, 400, 200, 400, 400, 250, 250]
columnWidths = [100, 570, 400, 400, 250, 250]
result_line_height = 96
font_size = 47
columnWidthsStars = [100, 400, 420, 400, 215, 200, 150]
result_line_height_stars = 130
font_size_stars = 35

