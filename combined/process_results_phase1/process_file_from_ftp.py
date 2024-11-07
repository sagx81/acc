
import os
import json
import glob
import csv
import datetime
# from combined.constants import points
# from PIL import Image, ImageDraw, ImageFont
# from process_results_phase1.track_data import track_data
from entities.processed_files import ProcessedFile
# import track_data
from constants import points
from constants import dnf_text
import constants

def convert_time(ms):
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    return f"{minutes:02}:{seconds:02}:{milliseconds:03}"

def generate_unique_filename(output_dir, base_name, extension="png"):
    counter = 1
    output_file = os.path.join(output_dir, f"{base_name}.{extension}")
    while os.path.exists(output_file):
        output_file = os.path.join(output_dir, f"{base_name}({counter}).{extension}")
        counter += 1
    return output_file

def find_project_root(start_path, target_dir_name="acc-race-results"):
    current_path = start_path
    while True:
        if os.path.basename(current_path) == target_dir_name:
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            raise FileNotFoundError(f"Katalog {target_dir_name} nie został znaleziony w ścieżce: {start_path}")
        current_path = parent_path

# Ustalanie katalogu głównego projektu
# project_root = find_project_root(os.path.abspath(__file__))

# Definiowanie dynamicznych ścieżek do katalogów wejściowych, wyjściowych oraz do plików czcionki i tła
# input_dir = os.path.join(project_root, "acc", "input")
# output_dir = os.path.join(project_root, "acc", "output", "GT3 S2")
# background_image = os.path.join(project_root, "files", "background", "race results.png")
# font_path = os.path.join(project_root, "files", "fonts", "BigShouldersDisplay-Bold.ttf")


# points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2, 1, 1, 1, 1, 1]
# points = points.get_points_table()
# points = constants.points

# GRAFIKA
# DNF_TEXT = "DNF"
# DNF_COLOR = "red"
# DEFAULT_COLOR = "#191919"
# MAGENTA_COLOR = "magenta"

current_dir = os.getcwd()
input_dir = os.path.join(current_dir, "fromFTP")
output_phase1 = "output_phase1"
results_phase1 = "process_results_phase1"
processedFiles = []
processedFilesCSV = os.path.join(current_dir, results_phase1, "processed_files.csv") 

def get_race_results():
    processedFileHasValue = False
    filesSorted = sorted(glob.glob(os.path.join(input_dir, "*.json")), key=os.path.getmtime, reverse=False)
    previousRaceDay = ""    
    # for json_file in glob.glob(os.path.join(input_dir, "*.json")):
    for json_file in filesSorted:
        try:
            print(f"Processing file: {json_file}")

            if (json_file.split('_')[0] == previousRaceDay):
                raceIndex += 1
            else:
                raceIndex = 1

            previousRaceDay = json_file.split('_')[0]
            
            # skipp if processed
            if (os.path.exists(processedFilesCSV) ):
                processedFileHasValue = True
                with open(processedFilesCSV, 'r', encoding='utf-8') as file:         
                    reader = csv.DictReader(file)           
                    print(f"Reading processed files: {processedFilesCSV}")
                    fileFound = False
                    for row in reader:
                        # row.data = json.load(file)          
                        # print(f"{data}")          
                        fileToFind = os.path.basename(json_file)
                        
                        if (fileToFind in row['File']):
                            print(f"\n SKIPPING file: {json_file}\n")
                            fileFound = True
                            break
                    if (fileFound):
                        continue
            
            print(f"Openning file: {json_file}")


            with open(json_file, 'r', encoding='utf-16-le') as file:
                data = json.load(file)

                serverName = data.get('serverName')
                # sessionIndex = data.get('sessionIndex')
                # if ("gt3" in serverName.lower()):
                if ("open" in serverName.lower()):
                    print(f"\n SKIPPING file: {json_file}\n")
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
                    # raceNumber = f" R{int(sessionIndex)}"

                seriesDir = seriesDir.upper()    
                output_dir = os.path.join(current_dir, output_phase1, seriesDir)

                # print(f"\n Output dir: {output_dir}")

                short_name = data.get('trackName', 'unknown_track')
                track_name = constants.get_track_name(short_name)
                # track_info = track_data.get(short_name, {})
                # track_name = track_info.get('name', short_name)

                base_name = os.path.basename(json_file)
                date_part = base_name.split('_')[0]
                time_part = base_name.split('_')[1]

                base_output_name = f"{short_name}-{seriesDir}{raceNumber}-{date_part}-{time_part}"

                # output_image_file = generate_unique_filename(output_dir, base_output_name, extension="png")
                output_csv_file = generate_unique_filename(output_dir, base_output_name, extension="csv")

                lap_counts = [line['timing'].get('lapCount', 0) for line in data['sessionResult']['leaderBoardLines']]
                if lap_counts:
                    max_lap_count = max(lap_counts)
                    min_laps_required = max_lap_count / 2
                else:
                    min_laps_required = 0

                results = []
                best_lap_times = []
                first_driver_time = None
                first_driver_laps = max_lap_count

                for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
                    drivers = line['car']['drivers']
                    driver_names = [driver['lastName'] for driver in drivers]
                    driver_names_str = ", ".join(driver_names)
                    total_time_ms = line['timing']['totalTime']
                    best_lap_ms = line['timing'].get('bestLap', 0)
                    lap_count = line['timing'].get('lapCount', 0)

                    # skipp spectators
                    if (lap_count == 0):
                        continue
                    elif lap_count < min_laps_required:
                        total_time_str = dnf_text
                        best_lap_str = dnf_text
                        points_awarded = 0
                    else:
                        if i == 0:
                            first_driver_time = total_time_ms
                            total_time_str = convert_time(total_time_ms)
                        else:
                            time_difference = total_time_ms - first_driver_time
                            timeDiffString = convert_time(time_difference)
                            # sometimes there is negative value if total driver time was < than total time of the winner
                            # for example when joining race after start    
                            if ('-' not in timeDiffString):
                                timeDiffString = f"+{timeDiffString}"
                            
                            if lap_count < first_driver_laps:
                                lapLabel = "lap"
                                laps_difference = first_driver_laps - lap_count
                                if laps_difference > 1:
                                    lapLabel = "laps"
                                total_time_str = f"{timeDiffString} (+{laps_difference} {lapLabel})"
                            else:
                                total_time_str = f"{timeDiffString}"

                        best_lap_str = convert_time(best_lap_ms)
                        points_awarded = points[i] if i < len(points) else 1

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

                if best_lap_times:
                    fastest_lap_time = min(best_lap_times)
                    fastest_lap_time_converted = convert_time(fastest_lap_time)
                else:
                    fastest_lap_time_converted = None

                print(f"output_csv_file: {output_csv_file}")

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(results)

                # save processed file
                # processedFiles.append({os.path.basename(json_file), datetime.datetime.now()})
                # processedFiles.append(ProcessedFile(os.path.basename(json_file), datetime.datetime.now()) )
                processedFiles.append([os.path.basename(json_file), datetime.datetime.now()])
                

            # GRAFIKA

            # if not os.path.isfile(background_image):
            #     raise FileNotFoundError(f"Background image not found: {background_image}")

            # bg_image = Image.open(background_image)
            # draw = ImageDraw.Draw(bg_image)

            # font_size = 47
            # try:
            #     font = ImageFont.truetype(font_path, font_size)
            # except IOError:
            #     print(f"Could not load font at {font_path}. Using default font.")
            #     font = ImageFont.load_default()

            # header_x_start = 20
            # header_y_start = 145
            # header_line_height = 40

            # column_widths = [170, 500, 400, 400, 250, 250]

            # for j, header in enumerate(results[0]):
            #     x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
            #     text_bbox = draw.textbbox((0, 0), header, font=font)
            #     text_width = text_bbox[2] - text_bbox[0]
            #     draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

            # title_text = track_name
            # title_bbox = draw.textbbox((0, 0), title_text, font=font)
            # title_width = title_bbox[2] - title_bbox[0]
            # title_x = (bg_image.width - title_width) // 2
            # title_y = header_y_start - header_line_height - 60

            # draw.text((title_x, title_y), title_text, fill="black", font=font)

            # result_x_start = 20
            # result_y_start = header_y_start + header_line_height + 38
            # result_line_height = 96

            # for i, row in enumerate(results[1:], start=1):
            #     y_position = result_y_start + (i - 1) * result_line_height
            #     for j, cell in enumerate(row):
            #         x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
            #         text_bbox = draw.textbbox((0, 0), str(cell), font=font)
            #         text_width = text_bbox[2] - text_bbox[0]
            #         if cell == DNF_TEXT:
            #             draw.text((x_position - text_width // 2, y_position), str(cell), fill=DNF_COLOR, font=font)
            #         elif j == 3 and cell == fastest_lap_time_converted:
            #             draw.text((x_position - text_width // 2, y_position), str(cell), fill=MAGENTA_COLOR, font=font)
            #         else:
            #             draw.text((x_position - text_width // 2, y_position), str(cell), fill=DEFAULT_COLOR, font=font)

            # bg_image.save(output_image_file)
            # print(f"Ranking został zapisany do pliku: {output_image_file}")

            # os.remove(json_file)

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
    try: 
        # for a in processedFiles:
        #     print(a)

        if (not processedFileHasValue):
            processedFiles.insert(0, ['File', 'Date'])

        with open(processedFilesCSV, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(processedFiles)
    except Exception as e:
        print(f"Process Results Phase 1 Save Processed File - An error occurred processing file {processedFilesCSV}: {e}")

