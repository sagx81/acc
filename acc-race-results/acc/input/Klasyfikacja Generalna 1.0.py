import os
import glob
import csv
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

# Ścieżki do katalogów
input_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\wyniki\Week League"
output_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\wyniki\Week League"
output_csv_file = os.path.join(output_dir, "klasyfikacja_generalna.csv")
background_image = os.path.join(input_dir, "grafika-kopia.jpg")
logo_image = os.path.join(input_dir, "logo_wl.png")
font_path = r"C:\Users\d.hanowicz\AppData\Local\Microsoft\Windows\Fonts\BigShouldersDisplay-Bold.ttf"

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

# Przetwarzanie każdego pliku CSV w katalogu wejściowym
for csv_file in glob.glob(os.path.join(input_dir, "*.csv")):
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Pozycja'] == 'Pozycja':  # Pomijanie nagłówka
                    continue
                driver = row['Kierowca']
                points = int(row['Punkty'])

                general_classification[driver] += points

    except Exception as e:
        print(f"An error occurred processing file {csv_file}: {e}")

# Tworzenie listy klasyfikacji generalnej
general_classification_list = []
for driver, points in general_classification.items():
    general_classification_list.append([driver, points])

# Sortowanie klasyfikacji generalnej według punktów (malejąco)
general_classification_list.sort(key=lambda x: -x[1])

# Dodawanie pozycji
for i, item in enumerate(general_classification_list):
    item.insert(0, i + 1)

# Dodawanie nagłówka kolumn
general_classification_list.insert(0, ['Pozycja', 'Kierowca', 'Punkty'])

# Zapisywanie klasyfikacji generalnej do pliku CSV
with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(general_classification_list)

print(f"Klasyfikacja generalna została zapisana do pliku: {output_csv_file}")

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
header_x_start = 20
header_y_start = 145
header_line_height = 40

# Ustawianie stałej szerokości kolumn
column_widths = [170, 700, 400]

# Rysowanie nagłówków kolumn
for j, header in enumerate(general_classification_list[0]):
    x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
    text_bbox = draw.textbbox((0, 0), header, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

# Rysowanie klasyfikacji generalnej
result_x_start = 20
result_y_start = header_y_start + header_line_height + 38  # Odstęp poniżej nagłówków
result_line_height = 96

for i, row in enumerate(general_classification_list[1:], start=1):  # Pomijamy nagłówki kolumn
    y_position = result_y_start + (i - 1) * result_line_height
    for j, cell in enumerate(row):
        x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
        text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

# Dodawanie logo
logo = Image.open(logo_image)
logo_width, logo_height = logo.size

# Zmiana rozmiaru logo
new_logo_width = 400  # Ustawienia szerokości dla logo
new_logo_height = 400  # Ustawienia wysokości dla logo
logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

logo_x = 1500  # Ustawienia pozycji X dla logo
logo_y = -140  # Ustawienia pozycji Y dla logo
bg_image.paste(logo, (logo_x, logo_y), logo)

# Zapisywanie obrazu
output_image_file = generate_unique_filename(output_dir, "klasyfikacja_generalna", extension="png")
bg_image.save(output_image_file)
print(f"Klasyfikacja generalna została zapisana do pliku: {output_image_file}")
