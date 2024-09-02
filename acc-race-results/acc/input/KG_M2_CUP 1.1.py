import os
import glob
import csv
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

# Ścieżki do katalogów
input_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\wyniki\M2 CUP"
output_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\wyniki\M2 CUP"
output_csv_file = os.path.join(output_dir, "klasyfikacja_generalna.csv")
background_image = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\input\Week League\klasyfikacja generalna.png"
logo_image = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\input\Week League\M2 CUP.png"
font_path = r"C:\Users\d.hanowicz\AppData\Local\Microsoft\Windows\Fonts\BigShouldersDisplay-Bold.ttf"
processed_files_log = os.path.join(output_dir, "processed_files.txt")

# Funkcja generująca unikalną nazwę pliku
def generate_unique_filename(output_dir, base_name, extension="png"):
    counter = 1
    output_file = os.path.join(output_dir, f"{base_name}.{extension}")
    while os.path.exists(output_file):
        output_file = os.path.join(output_dir, f"{base_name}({counter}).{extension}")
        counter += 1
    return output_file

# Inicjalizacja struktury danych do przechowywania wyników
general_classification = defaultdict(int)

# Wczytanie listy przetworzonych plików
processed_files = set()
if os.path.exists(processed_files_log):
    with open(processed_files_log, 'r', encoding='utf-8') as file:
        processed_files = set(line.strip() for line in file)

# Przetwarzanie każdego pliku CSV w katalogu wejściowym
for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
    if csv_file in processed_files:
        print(f"Plik już przetworzony: {csv_file}")
        continue

    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Pozycja'] == 'Pozycja':  # Pomijanie nagłówka
                    continue
                driver = row['Kierowca']
                points = int(row['Punkty'])

                general_classification[driver] += points

        # Dodanie pliku do przetworzonych
        processed_files.add(csv_file)

    except Exception as e:
        print(f"An error occurred processing file {csv_file}: {e}")

# Zapisywanie listy przetworzonych plików
with open(processed_files_log, mode='w', encoding='utf-8') as file:
    for processed_file in processed_files:
        file.write(processed_file + '\n')

# Tworzenie listy klasyfikacji generalnej
general_classification_list = []
for driver, points in general_classification.items():
    general_classification_list.append([driver, points])

# Sortowanie klasyfikacji generalnej według punktów (malejąco)
general_classification_list.sort(key=lambda x: -x[1])

# Dodawanie pozycji
for i, item in enumerate(general_classification_list):
    item.insert(0, i + 1)

# Zapisywanie klasyfikacji generalnej do pliku CSV
with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows([['Pozycja', 'Kierowca', 'Punkty']] + general_classification_list)

print(f"Klasyfikacja generalna została zapisana do pliku: {output_csv_file}")

# Sprawdzenie istnienia plików graficznych
if not os.path.exists(background_image):
    raise FileNotFoundError(f"Background image not found: {background_image}")

if not os.path.exists(logo_image):
    raise FileNotFoundError(f"Logo image not found: {logo_image}")

# Tworzenie obrazu tła
bg_image = Image.open(background_image).convert("RGBA")
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

# Split general_classification_list into two parts
mid_index = (len(general_classification_list) + 1) // 2  # Adjusted to split into two equal halves
left_column = general_classification_list[:mid_index]
right_column = general_classification_list[mid_index:]

# Ustawienia pozycji dla pierwszej i drugiej kolumny
left_column_x_start = 0
right_column_x_start = 985
result_y_start = header_y_start + header_line_height + 50  # Odstęp poniżej nagłówków
result_line_height = 96

# Rysowanie klasyfikacji generalnej dla lewej kolumny
for i, row in enumerate(left_column):  # Nagłówki są już pomijane
    y_position = result_y_start + i * result_line_height
    for j, cell in enumerate(row):
        x_position = left_column_x_start + sum(column_widths[:j]) + column_widths[j] // 2
        text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

# Rysowanie klasyfikacji generalnej dla prawej kolumny
for i, row in enumerate(right_column):
    y_position = result_y_start + i * result_line_height
    for j, cell in enumerate(row):
        x_position = right_column_x_start + sum(column_widths[:j]) + column_widths[j] // 2
        text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

# Dodawanie logo
logo = Image.open(logo_image).convert("RGBA")
logo_width, logo_height = logo.size

# Zmiana rozmiaru logo
new_logo_width = 400  # Ustawienia szerokości dla logo
new_logo_height = 400  # Ustawienia wysokości dla logo
logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

logo_x = 1500  # Ustawienia pozycji X dla logo
logo_y = -140  # Ustawienia pozycji Y dla logo

# Utworzenie maski z kanału alfa logo
logo_alpha = logo.split()[3]
bg_image.paste(logo, (logo_x, logo_y), mask=logo_alpha)

# Zapisywanie obrazu
output_image_file = generate_unique_filename(output_dir, "klasyfikacja_generalna", extension="png")
bg_image.save(output_image_file)
print(f"Klasyfikacja generalna została zapisana do pliku: {output_image_file}")
