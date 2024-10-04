
import os
import csv

from entities import entities

points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2]


color_dnf = "red"
color_default = "#191919"
color_magenta = "magenta"

dsq_text = "DSQ"
dnf_text = "DNF"
text_lap = "Okrażenie"
text_laps = "Okrążenia"



current_dir = os.getcwd()
ftp_input_dir = os.path.join(current_dir, "fromFTP")
output_phase1 = os.path.join(current_dir, "output_phase1")
output_individual_graphic = os.path.join(current_dir, "output_individual_graphic")
results_phase1 = os.path.join(current_dir, "process_results_phase1")
process_graphic_individual = os.path.join(current_dir, "process_graphic_individual")


graphicHeaders = ['Pozycja', 'Kierowca', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty']

def get_points_table():
    return points

# def points_awarded_for_position(position: int) -> int:
#     if position < 1 or position > len(points):
#         return 0
#     return points[position - 1]


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

def get_fastest_lap(results):
    fastest_lap_time = None
    for row in results:
        if fastest_lap_time is None or row.bestLap < fastest_lap_time:
            fastest_lap_time = row.bestLap
    return fastest_lap_time