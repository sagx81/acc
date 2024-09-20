import os
import json
import glob
from PIL import Image, ImageDraw, ImageFont
from track_data import track_data  # Import track data

# Funkcja konwertująca czas w milisekundach do formatu mm:ss:ms
def convert_time(ms):
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    return f"{minutes:02}:{seconds:02}:{milliseconds:03}"

# Ścieżki do katalogów
input_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\input"
output_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\wyniki"
output_file = os.path.join(output_dir, "results.png")
background_image = os.path.join(input_dir, "grafika-kopia.jpg")
font_path = r"C:\Users\d.hanowicz\AppData\Local\Microsoft\Windows\Fonts\BigShouldersDisplay-Bold.ttf"

# Punktacja za miejsca
points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2, 1, 1, 1, 1, 1]

# Przetwarzanie każdego pliku JSON w katalogu wejściowym
all_results = []
best_lap_times = []  # Przechowywanie najlepszych okrążeń
track_name = "Unknown Track"  # Domyślna wartość dla pełnej nazwy toru

for json_file in glob.glob(os.path.join(input_dir, "*.json")):
    try:
        with open(json_file, 'r', encoding='utf-16-le') as file:
            data = json.load(file)
            print(f"Processing file: {json_file}")

        # Pobranie skróconej nazwy toru i przetłumaczenie na pełną nazwę
        short_name = data.get('trackName', 'unknown_track')
        track_info = track_data.get(short_name, {})
        track_name = track_info.get('name', short_name)

        # Tworzenie listy wyników
        results = []
        for line in data['sessionResult']['leaderBoardLines']:
            drivers = line['car']['drivers']
            driver_names = [driver['lastName'] for driver in drivers]
            driver_names_str = ", ".join(driver_names)
            total_time_ms = line['driverTotalTimes'][0]
            best_lap_ms = line['timing']['bestLap']
            lap_count = line['timing']['lapCount']  # Liczba okrążeń
            
            # Dodawanie danych do listy wyników
            results.append([
                driver_names_str,  # Kierowca
                lap_count,  # Liczba okrążeń
                total_time_ms,  # Łączny czas (ms)
                best_lap_ms  # Najlepsze okrążenie (ms)
            ])
        
        # Sortowanie wyników najpierw według liczby okrążeń (malejąco), potem według łącznego czasu (rosnąco)
        results.sort(key=lambda x: (-x[1], x[2]))
        
        # Aktualizowanie listy wyników z pozycjami i punktami
        sorted_results = []
        for i, result in enumerate(results):
            sorted_results.append([
                i + 1,  # Pozycja (liczby naturalne, zaczynając od 1)
                result[0],  # Kierowca
                convert_time(result[2]),  # Łączny czas
                convert_time(result[3]),  # Najlepsze okrążenie
                result[1],  # Liczba okrążeń
                points[i] if i < len(points) else 1  # Punkty
            ])
            best_lap_times.append(result[3])  # Dodaj najlepszy czas okrążenia do listy
        
        all_results.extend(sorted_results)
        
        # Usuwanie przetworzonego pliku JSON
        os.remove(json_file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {json_file}: {e}")
    except Exception as e:
        print(f"An error occurred processing file {json_file}: {e}")

# Dodawanie nagłówka kolumn
all_results.insert(0, ['Pozycja', 'Kierowca', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty'])

# Znajdowanie najszybszego okrążenia
if best_lap_times:
    fastest_lap_time = min(best_lap_times)
    fastest_lap_time_converted = convert_time(fastest_lap_time)
else:
    fastest_lap_time_converted = None

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
column_widths = [170, 500, 400, 400, 250, 250]

# Rysowanie nagłówków kolumn
for j, header in enumerate(all_results[0]):
    x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
    text_bbox = draw.textbbox((0, 0), header, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

# Rysowanie pełnej nazwy toru
title_text = track_name
title_bbox = draw.textbbox((0, 0), title_text, font=font)
title_width = title_bbox[2] - title_bbox[0]
title_x = (bg_image.width - title_width) // 2
title_y = header_y_start - header_line_height - 60  # Pozycja Y powyżej nagłówków

draw.text((title_x, title_y), title_text, fill="black", font=font)

# Ustawienia pozycji początkowej dla wyników
result_x_start = 20
result_y_start = header_y_start + header_line_height + 38  # Odstęp 10 pikseli poniżej nagłówków
result_line_height = 96

# Rysowanie wyników
for i, row in enumerate(all_results[1:], start=1):  # Pomijamy nagłówki kolumn
    y_position = result_y_start + (i - 1) * result_line_height
    for j, cell in enumerate(row):
        x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
        text_bbox = draw.textbbox((0, 0), str(cell), font=font)
        text_width = text_bbox[2] - text_bbox[0]
        if j == 3 and cell == fastest_lap_time_converted:  # Kolumna "Naj. okrążenie" i najszybszy czas
            draw.text((x_position - text_width // 2, y_position), str(cell), fill="magenta", font=font)
        else:
            draw.text((x_position - text_width // 2, y_position), str(cell), fill="#191919", font=font)

# Zapisywanie obrazu
bg_image.save(output_file)
print(f"Ranking został zapisany do pliku: {output_file}")
