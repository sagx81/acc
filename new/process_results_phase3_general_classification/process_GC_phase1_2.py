import os
import glob
import csv
from collections import defaultdict

from utils_entities import constants
from utils_entities import utilities
from process_results_phase4_graphics import generate_graphic_gc

input_dir = constants.files_result_phase_1
output_dir = constants.files_result_phase_3
background_image = os.path.join(constants.process_graphic_individual, "files", "background", "general classification.png")
font_path = os.path.join(constants.process_graphic_individual, "files", "fonts", "BigShouldersDisplay-Bold.ttf")

def generate_GC_phase1():

    print("** General Classification ")
    dirs = glob.glob(os.path.join(constants.files_result_phase_1, "*"))    
    
    driversList = utilities.get_drivers_list_offline()

    for input_dir in dirs:

        # output_csv_file = utilities.generate_GC_file(input_dir)
        output_csv_file = utilities.generate_GC_file2_csv(os.path.basename(input_dir))
        output_csv_file = output_csv_file + "2"
        # skipp if file exists
        # if (os.path.exists(output_csv_file)):
        #     continue

        # clear general classification 
        general_classification = defaultdict(int)

        for csv_file in glob.glob(os.path.join(input_dir, "*.csv2")):

            # skip general classification file
            if '_gc.' in csv_file.lower():
                continue

            # skipp 'before penalties' files
            if '_beforepenalties' in csv_file.lower():
                continue

            # skipp Qualifications files
            if '_Q' in csv_file:
                continue            


            # take result with penalties if available
            # penaltiesAppliedCsv = csv_file.replace(".csv", "_penalties_applied.csv")
            # if os.path.exists(penaltiesAppliedCsv):
            #     csv_file = penaltiesAppliedCsv                

            try:
                # with open(csv_file, mode='r', encoding='utf-8') as file:
                    # reader = csv.DictReader(file)
                    
                # results = utilities.get_results_from_csv(csv_file, constants.process_GC_phase1)
                # results = utilities.get_results_from_csv(csv_file)
                results = utilities.get_results_from_csv2(csv_file, 'Generate GC phase1 V2')

                for row in results:


                    name = row.driver
                    

                    #if stars then team as separate column
                    team = ''
                    driver = ''
                    # prepare driver and team from csv splitted by '/n'
                    if (len(row.driver.split('\n')) > 1 and 'stars' in input_dir.lower()):
                        name = row.driver.split('\n')[0]
                    # driverName = utilities.get_driver(name)
                    # driverName = utilities.get_driver_web(results.playerId)
                    driverName = utilities.get_driver_name(row.playerId, driversList)
                    if not driverName:
                        driverName = name

                    general_classification[driverName] += row.points

                # Dodanie pliku do przetworzonych
                # processed_files.add(csv_file)

            except Exception as e:
                print(f"Process CG phase1: An error occurred processing file {csv_file}: {e}")

        # Zapisywanie listy przetworzonych plików
        # with open(processed_files_log, mode='w', encoding='utf-8') as file:
        #     for processed_file in processed_files:
        #         file.write(processed_file + '\n')

        # Tworzenie listy klasyfikacji generalnej
        general_classification_list = []
        
        for driver, points in general_classification.items():
            general_classification_list.append([driver, points])

        # Sortowanie klasyfikacji generalnej według punktów (malejąco)
        general_classification_list.sort(key=lambda x: -x[1])

        # Dodawanie pozycji
        for i, item in enumerate(general_classification_list):
            item.insert(0, i + 1)

        # directoryPath = os.path.join(constants.output_phase1, os.path.basename(input_dir))
        directoryPath = os.path.join(constants.files_result_phase_1, os.path.basename(input_dir))
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)

        # output_csv_file_name = f"{os.path.basename(input_dir)}_GC.csv"
        # output_csv_file = os.path.join(input_dir, output_csv_file_name)
                
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([['Position', 'Driver', 'Points']] + general_classification_list)

        print(f"Klasyfikacja generalna została zapisana do pliku: {output_csv_file}")

        raceType = os.path.basename(input_dir).split(' ')[0]
        # if raceType == 'WEEK':
        #     raceType = 'WL'

        generate_graphic_gc.generate_gc(general_classification_list, raceType, output_csv_file, input_dir)
        
        # GRAFIKA KG
        # Sprawdzenie istnienia plików graficznych
        # if not os.path.exists(background_image):
        #     raise FileNotFoundError(f"Background image not found: {background_image}")

        # if not os.path.exists(logo_image):
        #     raise FileNotFoundError(f"Logo image not found: {logo_image}")

        # # Tworzenie obrazu tła
        # bg_image = Image.open(background_image)
        # draw = ImageDraw.Draw(bg_image)

        # # Ustawienia czcionki
        # font_size = 47
        # try:
        #     font = ImageFont.truetype(font_path, font_size)
        # except IOError:
        #     print(f"Could not load font at {font_path}. Using default font.")
        #     font = ImageFont.load_default()

        # # Ustawienia pozycji początkowej dla nagłówków kolumn
        # header_y_start = 160
        # header_line_height = 40

        # # Ustawianie stałej szerokości kolumn
        # column_widths = [140, 300, 940]

        # # Podział general_classification_list na dwie części
        # mid_index = (len(general_classification_list) + 1) // 2
        # left_column = general_classification_list[:mid_index]
        # right_column = general_classification_list[mid_index:]

        # # Ustawienia pozycji dla pierwszej i drugiej kolumny
        # left_column_x_start = 0
        # right_column_x_start = 985
        # result_y_start = header_y_start + header_line_height + 50  # Odstęp poniżej nagłówków
        # result_line_height = 96

        # # Rysowanie klasyfikacji generalnej dla lewej kolumny
        # for i, row in enumerate(left_column):
        #     y_position = result_y_start + i * result_line_height
        #     for j, cell in enumerate(row):
        #         x_position = left_column_x_start + sum(column_widths[:j]) + column_widths[j] // 2
        #         text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        #         text_width = text_bbox[2] - text_bbox[0]
        #         draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

        # # Rysowanie klasyfikacji generalnej dla prawej kolumny
        # for i, row in enumerate(right_column):
        #     y_position = result_y_start + i * result_line_height
        #     for j, cell in enumerate(row):
        #         x_position = right_column_x_start + sum(column_widths[:j]) + column_widths[j] // 2
        #         text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        #         text_width = text_bbox[2] - text_bbox[0]
        #         draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

        # # Dodawanie logo
        # logo = Image.open(logo_image)
        # logo_width, logo_height = logo.size

        # # Zmiana rozmiaru logo
        # new_logo_width = 400  # Ustawienia szerokości dla logo
        # new_logo_height = 400  # Ustawienia wysokości dla logo
        # logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

        # logo_x = 1500  # Ustawienia pozycji X dla logo
        # logo_y = -140  # Ustawienia pozycji Y dla logo
        # bg_image.paste(logo, (logo_x, logo_y), logo)

        # # Zapisywanie obrazu
        # output_image_file = generate_unique_filename(output_dir, "klasyfikacja_generalna", extension="png")
        # bg_image.save(output_image_file)
        # print(f"Klasyfikacja generalna została zapisana do pliku: {output_image_file}")
