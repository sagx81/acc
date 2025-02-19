import os
import glob
import csv
from PIL import Image, ImageDraw, ImageFont
from utils_entities import constants

# GRAFIKA KG
# Sprawdzenie istnienia plików graficznych

# input_dir = constants.output_phase1
input_dir = constants.files_result_phase_1
output_dir = constants.files_result_phase_3
background_image = os.path.join(constants.process_graphic_individual, "files", "background", "general classification.png")
font_path = os.path.join(constants.process_graphic_individual, "files", "fonts", "BigShouldersDisplay-Bold.ttf")
# logo_image = os.path.join(constants.process_graphic_individual, "files", "Logo", "race results.png")

# if not os.path.exists(background_image):
#     raise FileNotFoundError(f"Background image not found: {background_image}")

# if not os.path.exists(logo_image):
#     raise FileNotFoundError(f"Logo image not found: {logo_image}")

def generate_gc(general_classification_list, raceType, gcCsvFile):

    # Tworzenie obrazu tła
    bg_image = Image.open(background_image)
    draw = ImageDraw.Draw(bg_image)

    # Ustawienia czcionki
    font_size = 47
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Could not load font at {font_path}. Using default font.")
        font = ImageFont.load_default()

    # Ustawienia pozycji początkowej dla nagłówków kolumn
    header_y_start = 160
    header_line_height = 40

    # Ustawianie stałej szerokości kolumn
    column_widths = [140, 300, 940]

    # Podział general_classification_list na dwie części
    mid_index = (len(general_classification_list) + 1) // 2
    left_column = general_classification_list[:mid_index]
    right_column = general_classification_list[mid_index:]

    # Ustawienia pozycji dla pierwszej i drugiej kolumny
    left_column_x_start = 0
    right_column_x_start = 985
    # result_y_start = header_y_start + header_line_height + 50  # Odstęp poniżej nagłówków    
    result_line_height = 96
    result_y_start = header_y_start + header_line_height + result_line_height + result_line_height/2   # Odstęp poniżej nagłówków

    # Rysowanie klasyfikacji generalnej dla lewej kolumny
    for i, row in enumerate(left_column):
        y_position = result_y_start + i * result_line_height
        for j, cell in enumerate(row):
            x_position = left_column_x_start + sum(column_widths[:j]) + column_widths[j] // 2
            text_bbox = draw.textbbox((0, 0), str(cell), font=font)
            text_width = text_bbox[2] - text_bbox[0]
            draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

        draw.text((right_column_x_start, y_position), '|', fill="#191919", font=font)

    lastHeight = 0
    # Rysowanie klasyfikacji generalnej dla prawej kolumny
    for i, row in enumerate(right_column):
        y_position = result_y_start + i * result_line_height
        lastHeight = y_position
        for j, cell in enumerate(row):
            x_position = right_column_x_start + sum(column_widths[:j]) + column_widths[j] // 2
            text_bbox = draw.textbbox((0, 0), str(cell), font=font)
            text_width = text_bbox[2] - text_bbox[0]            
            draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

    logo_image = os.path.join(constants.logoFolder,f"{raceType}.png")
    if os.path.exists(logo_image):          
        # Dodawanie logo
        logo = Image.open(logo_image)
        # logo_width, logo_height = logo.size

        # Zmiana rozmiaru logo
        new_logo_width = 400  # Ustawienia szerokości dla logo
        new_logo_height = 400  # Ustawienia wysokości dla logo
        logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

        logo_x = 1500  # Ustawienia pozycji X dla logo
        logo_y = -140  # Ustawienia pozycji Y dla logo
        bg_image.paste(logo, (logo_x, logo_y), logo)

    # Zapisywanie obrazu
    # output_image_file = generate_unique_filename(output_dir, "klasyfikacja_generalna", extension="png")

    # image resize
    img = bg_image.crop((0, 0, bg_image.width, lastHeight + (5 * result_line_height/2)))

    output_image_file = gcCsvFile.replace('csv','png')
    img.save(output_image_file)
    # bg_image.save(output_image_file)

    # print(f"Klasyfikacja generalna została zapisana do pliku: {output_image_file}")
