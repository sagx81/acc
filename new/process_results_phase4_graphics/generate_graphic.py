import os
import glob
import sys
from PIL import Image, ImageDraw, ImageFont
from utils_entities import constants
from utils_entities import utilities


# def is_debug():
#     import sys

#     gettrace = getattr(sys, 'gettrace', None)

#     if gettrace is None:
#         return False
#     else:
#         v = gettrace()
#         if v is None:
#             return False
#         else:
#             return True

# print(f" is debug: {is_debug()}")

    # print("IS DEBUG")

# DEBUG = sys.gettrace() is not None
# print(f"\nDEBUG MODE: {DEBUG}\n")


# if DEBUG:
#     from pathlib import Path
#     sys.path.append(str(Path(__file__).parent.parent))
#     from utils_entities import constants    
# else:
#     from utils_entities import constants


# DEBUG = False
# if (len(sys.argv) == 2 and sys.argv[1] == 'debug'):
#     DEBUG = True



input_files_dir = constants.files_result_phase_1
output_dir = constants.files_individual_graphic
background_image = os.path.join(constants.process_graphic_individual, "files", "background", "race results.png")
font_path = os.path.join(constants.process_graphic_individual, "files", "fonts", "BigShouldersDisplay-Bold.ttf")
logo_folder = os.path.join(constants.process_graphic_individual,"files", "Logo")

def generate_individual_graphic():

    print(f"\n*** Generating individual graphics \n")

    # '/home/pawel/code/acc/process_results_phase4_graphics/files/background/race results.png'

    if not os.path.isfile(background_image):
        raise FileNotFoundError(f"Background image not found: {background_image}")

    
    font_size = 47
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Could not load font at {font_path}. Using default font.")
        font = ImageFont.load_default()

    header_x_start = 20
    header_y_start = 145
    header_line_height = 40

    # regular_column_widths = [170, 500, 400, 400, 250, 250]
    # stars_column_widths = [100, 400, 420, 400, 215, 215, 215]
    
    # input_dirs = os.path.join(constants.output_phase1, inputResultsFolder)
    dirs = glob.glob(os.path.join(input_files_dir, "*"))
    for input_dir in dirs:
        for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):

            #TODO: to be removed
            # if 'stars' not in input_dir.lower():
            #     continue

            isStars = False
            if 'stars' in input_dir.lower():
                isStars = True

                


            penaltiesAppliedCsv = csv_file.replace(".csv", "_penalties_applied.csv")
            if os.path.exists(penaltiesAppliedCsv):
                csv_file = penaltiesAppliedCsv                

            try:    

                bg_image = Image.open(background_image)
                draw = ImageDraw.Draw(bg_image)
            
                # with open(csv_file, mode='r', encoding='utf-8') as file:
                
                # with open(csv_file, mode='r', encoding='utf-8') as file:
                    # reader = csv.DictReader(file)
                    
                # results = constants.get_results_from_csv(csv_file, constants.process_graphic_individual)
                results = utilities.get_results_from_csv(csv_file, constants.process_graphic_individual)

                # print(f"\n*** Results Image => Preparing Image file {csv_file}")
                
                graphicHeaders = constants.graphicHeaders
                column_widths = constants.columnWidths
    
                if isStars:
                    column_widths = constants.columnWidthsStars
                    graphicHeaders = constants.graphicHeadersStars

                # print(f"{column_widths}  {graphicHeaders}")

                # draw header
                for j, header in enumerate(graphicHeaders):
                    x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                    text_bbox = draw.textbbox((0, 0), header, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

                short_name = os.path.basename(csv_file).split("-")[0].lower()
                track_name = utilities.get_track_name(short_name)

                # track_name = os.path.basename(csv_file).split("-")[0].upper()
                # print(f"Track name: {track_name}")

                title_text = track_name
                title_bbox = draw.textbbox((0, 0), title_text, font=font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (bg_image.width - title_width) // 2
                title_y = header_y_start - header_line_height - 60

                # draw track Name (center title)
                draw.text((title_x, title_y), title_text, fill="black", font=font)
                
                # lines calculation
                result_x_start = 20
                result_y_start = header_y_start + header_line_height + 38
                result_line_height = 96

                fastestLap = utilities.get_fastest_lap(results)

                # draw rows
                for i, row in enumerate(results, start=0):
                    y_position = result_y_start + i * result_line_height
                    # print(f"row: {row}")
                    jAdjustor = 0                        

                    for j, cell in enumerate(vars(row).items()):                            
                        # print(f"cell: {cell}")
                        cellField = cell[0]
                        cellValue = cell[1]

                        # ommit additional columns from csv result file
                        if cellField == "totalTimeMs" or cellField == "totalTimeString" or cellField == "isDsq":
                            jAdjustor = jAdjustor + 1
                            continue
                        j = j - jAdjustor

                        # adjust columns index when Stars
                        if isStars and j > 1:
                            j = j+1

                        #if stars then team as separate column
                        team = ''
                        driver = ''
                        # prepare driver and team from csv splitted by '/n'
                        if (cellField == 'driver' and len(cellValue.split('\n')) > 1 and 'stars' in input_dir.lower()):
                            team = cellValue.split('\n')[0]
                            driver = cellValue.split('\n')[1]
                        
                        # if team:
                        # if (cellField == 'driver'):
                        #     print(f"TEAM: {team}, driver: {driver}")

                        # print(f"--- {jAdjustor} {j} {sum(column_widths[:j])}")

                        x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                        
                        # cell value
                        text_bbox = draw.textbbox((0, 0), str(cellValue), font=font)
                        text_width = text_bbox[2] - text_bbox[0]

                        # replace lap/laps by constnant value
                        if ("laps" in str(cellValue)):
                            cellValue = cellValue.replace("laps", constants.text_laps)
                        elif ("lap" in str(cellValue)):
                            cellValue = cellValue.replace("lap", constants.text_lap)

                        # replace DNF/DSQ from constants
                        if cellValue == constants.dnf_text or cellValue == constants.dsq_text:
                            draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_dnf, font=font)
                        # color best lap 
                        elif cellField == "bestLap" and cellValue == fastestLap:
                            draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_magenta, font=font)
                        elif isStars and cellField == "driver":
                            # draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_default, font=font)

                            #driver
                            x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2                                    
                            text_bbox = draw.textbbox((0, 0), driver, font=font)
                            text_width = text_bbox[2] - text_bbox[0]
                            draw.text((x_position - text_width // 2, y_position), str(driver), fill=constants.color_default, font=font)
                            
                            #team
                            j=j+1
                            x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                            # print(f"bbbox team {text_bbox}")
                            text_bbox = draw.textbbox((0, 0), str(team), font=font)
                            text_width = text_bbox[2] - text_bbox[0]
                            draw.text((x_position - text_width // 2, y_position), str(team), fill=constants.color_default, font=font)
                            
                            #j=j+1
                        else:
                            draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_default, font=font)

                if not os.path.exists(constants.files_individual_graphic):
                    os.makedirs(constants.files_individual_graphic)
                
                directoryPath = os.path.join(constants.files_individual_graphic, os.path.basename(input_dir))
                if not os.path.exists(directoryPath):
                    os.makedirs(directoryPath)
                
                if "penalties_applied" in csv_file:
                    imageFile = os.path.basename(csv_file).replace("_penalties_applied.csv", ".png")
                else:
                    imageFile = os.path.basename(csv_file).replace(".csv", ".png")
                

                # logo
                # Dodawanie logo
                raceType = os.path.basename(input_dir).split(' ')[0]
                if raceType == 'WEEK':
                    raceType = 'WL'

                logo_image = os.path.join(constants.logoFolder,f"{raceType}.png")
                if os.path.exists(logo_image):
                    logo = Image.open(logo_image)

                    # Zmiana rozmiaru logo
                    new_logo_width = 400  # Ustawienia szerokości dla logo
                    new_logo_height = 400  # Ustawienia wysokości dla logo
                    logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

                    logo_x = 1500  # Ustawienia pozycji X dla logo
                    logo_y = -140  # Ustawienia pozycji Y dla logo
                    bg_image.paste(logo, (logo_x, logo_y), logo)

                # logo_width, logo_height = logo.size

                
                
                # output_image_file = os.path.join(constants.current_dir, constants.output_individual_graphic, input_dir, imageFile)
                output_image_file = os.path.join(directoryPath, imageFile)
                bg_image.save(output_image_file, overwrite=True)
                # print(f"Result Image saved: {output_image_file}")

                # os.remove(json_file)

            except Exception as e:
                print(f"Generate Individual Result Graphic - An error occurred processing file {csv_file}: {e}")

# if DEBUG:
#     generate_individual_graphic()
