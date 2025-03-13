import os
import glob
import sys
from PIL import Image, ImageDraw, ImageFont
from utils_entities import constants
from utils_entities import utilities
from utils_entities import entities

input_files_dir = constants.files_result_phase_1
output_dir = constants.files_individual_graphic
background_image = constants.backgroundImagePath
font_path = constants.fontBoldPath
logo_folder = constants.seriesLogosFolder

def generate_individual_graphic():

    print(f"\n*** Generating individual graphics V2\n")

    if not os.path.isfile(background_image):
        raise FileNotFoundError(f"Background image not found: {background_image}")    
    
    header_x_start = 20
    header_y_start = 145
    header_line_height = 40
    font_size = 47

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Could not load font at {font_path}. Using default font.")
        font = ImageFont.load_default()

    cars = utilities.get_cars()
    
    # dirs = glob.glob(os.path.join(input_files_dir, "*"))
    # dirs = input_dirs = constants.files_results
    # dirs = glob.glob(os.path.join(input_dirs, "*"))
    dirs = utilities.get_series_directories()
    for input_dir in dirs:
        # for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
        for csv_file in utilities.get_serie_csv_files(input_dir):

            if '(' in csv_file:
                continue

            if '_GC' in csv_file:
                continue


            isQuali = False
            if '_Q' in csv_file:
                isQuali = True
                # continue

            isStars = False
            if 'stars' in input_dir.lower():
                isStars = True

            try:    

                graphicHeaders = constants.graphicHeaders
                column_widths = constants.columnWidths    
                
                if isStars:
                    column_widths = constants.columnWidthsStars
                    graphicHeaders = constants.graphicHeadersStars

                bg_image = Image.open(background_image)
                draw = ImageDraw.Draw(bg_image)

                results = utilities.get_results_from_csv2(csv_file, constants.process_graphic_individual)

                # draw header
                for j, header in enumerate(graphicHeaders):
                    x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                    text_bbox = draw.textbbox((0, 0), header, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

                # TRACK NAME
                short_name = os.path.basename(csv_file).split("-")[2].lower()
                track_name = utilities.get_track_name(short_name)
                title = track_name

                befoerePenalties = ""
                if 'beforePenalties' in csv_file:
                    befoerePenalties = " (przed karami)"

                additionalTitleText = ""
                if isQuali:
                    additionalTitleText = " (Kwalifikacje)"
                if ' R1' in csv_file:
                    additionalTitleText = f" (Wyścig 1)"
                elif ' R2' in csv_file:
                    additionalTitleText =  f" (Wyścig 2)"

                title = title + additionalTitleText + befoerePenalties

                # prepare output path
                # if "penalties_applied" in csv_file:
                #     imageFile = os.path.basename(csv_file).replace("_penalties_applied.csv", ".png")
                # else:
                
                # imageFile = os.path.basename(csv_file).replace(".csv2", "_2.png")            
                imageFile = os.path.basename(csv_file).replace(".csv", ".png")            

                # directoryPath = os.path.join(constants.files_individual_graphic, os.path.basename(input_dir))
                # directoryPath = os.path.join(constants.files_result_png, os.path.basename(input_dir))
                directoryPath = os.path.join(constants.files_results, os.path.basename(input_dir), 'png')
                if not os.path.exists(directoryPath):
                    os.makedirs(directoryPath)
                output_image_file = os.path.join(directoryPath, imageFile)
                
                # skipp if file exists
                if (os.path.exists(output_image_file)):
                    continue

                title_text = title
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

                lastHeight = 0
                # draw rows
                for i, row in enumerate(results, start=0):
                    y_position = result_y_start + i * result_line_height
                    lastHeight = y_position                    
                    jAdjustor = 0                        

                    graphicResult = entities.IndividualGraphicRow(row.position, row.driver, row.timing, row.bestLap, row.laps, row.points)                    
                    for j, cell in enumerate(vars(graphicResult).items()):                            
                        # print(f"cell: {cell}")
                        cellField = cell[0]
                        cellValue = cell[1]



                        # ommit additional columns from csv result file
                        # if cellField == "totalTimeMs" or cellField == "totalTimeString" or cellField == "isDsq" or cellField == "penaltyMs":
                        #     jAdjustor = jAdjustor + 1
                        #     continue
                        # j = j - jAdjustor

                        # # adjust columns index when Stars
                        if isStars and j > 1:
                            j = j+1

                        #if stars then team as separate column
                        team = ''
                        driver = ''
                        # # prepare driver and team from csv splitted by '/n'
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

                        # car logo
                        if cellField == 'driver':
                            carLogo = utilities.get_driver_car_model(cars, row.carModel)
                            carLogoImage = os.path.join(constants.carLogosFolder ,f"{carLogo}.png")
                            # carLogoImage = os.path.join(constants.carLogosFolder ,"mercedes-amg.png")
                            if os.path.exists(carLogoImage):
                                logo = Image.open(carLogoImage)

                                # Zmiana rozmiaru logo
                                new_logo_width = 140  # Ustawienia szerokości dla logo
                                new_logo_height = 100  # Ustawienia wysokości dla logo
                                logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

                                logo_x = 550  # Ustawienia pozycji X dla logo
                                # logo_x = x_position + text_width  # Ustawienia pozycji X dla logo
                                logo_y = y_position - 10  # Ustawienia pozycji Y dla logo
                                bg_image.paste(logo, (logo_x, logo_y), logo)


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
                
                # directoryPath = os.path.join(constants.files_individual_graphic, os.path.basename(input_dir))
                # if not os.path.exists(directoryPath):
                #     os.makedirs(directoryPath)
                
                

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
                
                # image resize
                img = bg_image.crop((0, 0, bg_image.width, lastHeight + (5 * result_line_height/2)))

                # output_image_file = os.path.join(directoryPath, imageFile)
                img.save(output_image_file, overwrite=True)
                # bg_image.save(output_image_file, overwrite=True)
                print(f"Result Image saved: {output_image_file}")

                # os.remove(json_file)

            except Exception as e:
                print(f"Generate Individual Result Graphic - An error occurred processing file {csv_file}: {e}")

# if DEBUG:
#     generate_individual_graphic()
