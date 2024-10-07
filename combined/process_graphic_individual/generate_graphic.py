import os
import glob
import csv
from PIL import Image, ImageDraw, ImageFont

import constants

input_dir = constants.output_phase1
output_dir = constants.output_individual_graphic
background_image = os.path.join(constants.process_graphic_individual, "files", "background", "race results.png")
font_path = os.path.join(constants.process_graphic_individual, "files", "fonts", "BigShouldersDisplay-Bold.ttf")

def generate_individual_graphic():

    print(f"\n\n ______ Generating individual graphics ____\n\n")


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

    column_widths = [170, 500, 400, 400, 250, 250]
    
    # input_dirs = os.path.join(constants.output_phase1, inputResultsFolder)
    dirs = glob.glob(os.path.join(constants.output_phase1, "*"))
    for input_dir in dirs:
        for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):

            penaltiesAppliedCsv = csv_file.replace(".csv", "_penalties_applied.csv")
            if os.path.exists(penaltiesAppliedCsv):
                csv_file = penaltiesAppliedCsv                

            try:    

                bg_image = Image.open(background_image)
                draw = ImageDraw.Draw(bg_image)
            
                # with open(csv_file, mode='r', encoding='utf-8') as file:
                
                # with open(csv_file, mode='r', encoding='utf-8') as file:
                    # reader = csv.DictReader(file)
                    
                results = constants.get_results_from_csv(csv_file, constants.process_graphic_individual)

                print(f"\n*** Results Image => Preparing Image file {csv_file}")

                for j, header in enumerate(constants.graphicHeaders):
                    x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                    text_bbox = draw.textbbox((0, 0), header, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

                # TODO track name from track_data
                track_name = os.path.basename(csv_file).split("-")[0].upper()
                print(f"Track name: {track_name}")

                title_text = track_name
                title_bbox = draw.textbbox((0, 0), title_text, font=font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (bg_image.width - title_width) // 2
                title_y = header_y_start - header_line_height - 60

                draw.text((title_x, title_y), title_text, fill="black", font=font)

                result_x_start = 20
                result_y_start = header_y_start + header_line_height + 38
                result_line_height = 96

                # print(f"{vars(results[0]).items()}")

                # for i, row in enumerate(results[1:], start=1):

                fastestLap = constants.get_fastest_lap(results)

                for i, row in enumerate(results, start=0):
                    y_position = result_y_start + i * result_line_height
                    # print(f"row: {row}")
                    jAdjustor = 0                        

                    for j, cell in enumerate(vars(row).items()):                            
                        # print(f"cell: {cell}")
                        cellField = cell[0]
                        cellValue = cell[1]

                        if cellField == "totalTimeMs" or cellField == "totalTimeString" or cellField == "isDsq":
                            jAdjustor = jAdjustor + 1
                            continue
                        j = j - jAdjustor

                        
                        # print(f"--- {jAdjustor} {j} {sum(column_widths[:j])}")

                        x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                        
                        text_bbox = draw.textbbox((0, 0), str(cellValue), font=font)
                        text_width = text_bbox[2] - text_bbox[0]

                        if ("laps" in str(cellValue)):
                            cellValue = cellValue.replace("laps", constants.text_laps)
                        elif ("lap" in str(cellValue)):
                            cellValue = cellValue.replace("lap", constants.text_lap)

                        if cellValue == constants.dnf_text or cellValue == constants.dsq_text:
                            draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_dnf, font=font)
                        elif cellField == "bestLap" and cellValue == fastestLap:
                            draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_magenta, font=font)
                        else:
                            draw.text((x_position - text_width // 2, y_position), str(cellValue), fill=constants.color_default, font=font)

                if not os.path.exists(constants.output_individual_graphic):
                    os.makedirs(constants.output_individual_graphic)
                
                directoryPath = os.path.join(constants.output_individual_graphic, os.path.basename(input_dir))
                if not os.path.exists(directoryPath):
                    os.makedirs(directoryPath)
                
                if "penalties_applied" in csv_file:
                    imageFile = os.path.basename(csv_file).replace("_penalties_applied.csv", ".png")
                else:
                    imageFile = os.path.basename(csv_file).replace(".csv", ".png")
                
                
                # output_image_file = os.path.join(constants.current_dir, constants.output_individual_graphic, input_dir, imageFile)
                output_image_file = os.path.join(directoryPath, imageFile)
                bg_image.save(output_image_file, overwrite=True)
                print(f"Result Image saved: {output_image_file}")

                # os.remove(json_file)

            except Exception as e:
                print(f"An error occurred processing file {csv_file}: {e}")