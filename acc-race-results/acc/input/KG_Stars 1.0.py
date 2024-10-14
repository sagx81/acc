import os
import glob
import csv
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

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
project_root = find_project_root(os.path.abspath(__file__))

# Definiowanie dynamicznych ścieżek do katalogów wejściowych, wyjściowych oraz do plików czcionki i tła
input_dir = os.path.join(project_root, "acc", "output", "Stars")
output_dir = os.path.join(project_root, "acc", "output", "Stars")
background_image = os.path.join(project_root, "files", "background", "KG_Stars.jpg")
font_path = os.path.join(project_root, "files", "fonts", "BigShouldersDisplay-Bold.ttf")
output_csv_file = os.path.join(project_root, "acc", "output", "Stars", "klasyfikacja_generalna.csv")
logo_image = os.path.join(project_root, "files", "Logo", "Stars_baner.png")
processed_files_log = os.path.join(project_root, "acc", "output", "Stars", "processed_files.txt")

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
    with open(processed_files_log, 'r', encoding='ANSI') as file:
        processed_files = set(line.strip() for line in file)

# Przetwarzanie każdego pliku CSV w katalogu wejściowym
for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
    if csv_file in processed_files:
        print(f"Plik już przetworzony: {csv_file}")
        continue

    try:
        with open(csv_file, mode='r', encoding='ANSI') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Pozycja'] == 'Pozycja':  # Pomijanie nagłówka
                    continue
                team = row['Team']  # Zamiast 'Kierowca', teraz klasyfikujemy 'Team'
                points = int(row['Punkty'])

                general_classification[team] += points  # Sumujemy punkty dla teamu

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
for team, points in general_classification.items():
    general_classification_list.append([team, points])

# Sortowanie klasyfikacji generalnej według punktów (malejąco)
general_classification_list.sort(key=lambda x: -x[1])

# Dodawanie pozycji
for i, item in enumerate(general_classification_list):
    item.insert(0, i + 1)

# Zapisywanie klasyfikacji generalnej do pliku CSV
with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows([['Pozycja', 'Team', 'Punkty']] + general_classification_list)

print(f"Klasyfikacja generalna została zapisana do pliku: {output_csv_file}")

# Sprawdzenie istnienia plików graficznych
if not os.path.exists(background_image):
    raise FileNotFoundError(f"Background image not found: {background_image}")

if not os.path.exists(logo_image):
    raise FileNotFoundError(f"Logo image not found: {logo_image}")

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

# Ustawianie szerokości kolumny dla jednej kolumny
column_width = 1100  # Zmieniamy szerokość dla jednej kolumny

# Pozycje początkowe dla jednej kolumny
column_x_start = (bg_image.width - column_width) // 1  # Wycentrowanie kolumny na środku obrazu
result_y_start = header_y_start + header_line_height + 50  # Odstęp poniżej nagłówków
result_line_height = 96

# Rysowanie klasyfikacji generalnej dla jednej kolumny
for i, row in enumerate(general_classification_list):
    y_position = result_y_start + i * result_line_height
    for j, cell in enumerate(row):
        x_position = column_x_start + sum([column_width]) // len(row) * j
        text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

# Dodawanie logo
logo = Image.open(logo_image)
logo_width, logo_height = logo.size

# Zmiana rozmiaru logo
new_logo_width = 400  # Ustawienia szerokości dla logo
new_logo_height = 300  # Ustawienia wysokości dla logo
logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

logo_x = 1000  # Ustawienia pozycji X dla logo
logo_y = -70  # Ustawienia pozycji Y dla logo
bg_image.paste(logo, (logo_x, logo_y), logo)

# Zapisywanie obrazu
output_image_file = generate_unique_filename(output_dir, "klasyfikacja_generalna", extension="png")
bg_image.save(output_image_file)
print(f"Klasyfikacja generalna została zapisana do pliku: {output_image_file}")
