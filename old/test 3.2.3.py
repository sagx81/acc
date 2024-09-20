import os
import json
import glob
import csv
from PIL import Image, ImageDraw, ImageFont
from track_data import track_data  # Import track data

# Funkcja konwertująca czas w milisekundach do formatu mm:ss:ms
def convert_time(ms):
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    return f"{minutes:02}:{seconds:02}:{milliseconds:03}"

# Funkcja generująca unikalną nazwę pliku
def generate_unique_filename(output_dir, base_name, extension="png"):
    counter = 1
    output_file = os.path.join(output_dir, f"{base_name}.{extension}")
    while os.path.exists(output_file):
        output_file = os.path.join(output_dir, f"{base_name}({counter}).{extension}")
        counter += 1
    return output_file

# Ścieżki do katalogów
input_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\input"
output_dir = r"C:\Users\d.hanowicz\Desktop\AMC\Wyniki-automat\acc 2\acc\wyniki\Week League"
background_image = os.path.join(input_dir, "grafika-kopia.jpg")
font_path = r"C:\Users\d.hanowicz\AppData\Local\Microsoft\Windows\Fonts\BigShouldersDisplay-Bold.ttf"

# Punktacja za miejsca
points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2, 1, 1, 1, 1, 1]

# Definicje stałych dla formatowania
DNF_TEXT = "DNF"
DNF_COLOR = "red"  # Kolor DNF
DEFAULT_COLOR = "#191919"  # Domyślny kolor tekstu
MAGENTA_COLOR = "magenta"  # Kolor dla najlepszego okrążenia

# Przetwarzanie każdego pliku JSON w katalogu wejściowym
for json_file in glob.glob(os.path.join(input_dir, "*.json")):
    try:
        with open(json_file, 'r', encoding='utf-16-le') as file:
            data = json.load(file)
            print(f"Processing file: {json_file}")

        # Pobranie skróconej nazwy toru i przetłumaczenie na pełną nazwę
        short_name = data.get('trackName', 'unknown_track')
        track_info = track_data.get(short_name, {})
        track_name = track_info.get('name', short_name)

        # Wyodrębienie daty z nazwy pliku źródłowego
        base_name = os.path.basename(json_file)
        date_part = base_name.split('_')[0]

        # Ustawienie nazwy pliku wynikowego
        base_output_name = f"{short_name}-{date_part}"
        output_image_file = generate_unique_filename(output_dir, base_output_name, extension="png")
        output_csv_file = generate_unique_filename(output_dir, base_output_name, extension="csv")

        # Pobranie liczby okrążeń dla każdej pozycji
        lap_counts = [line['timing'].get('lapCount', 0) for line in data['sessionResult']['leaderBoardLines']]
        if lap_counts:
            max_lap_count = max(lap_counts)
            min_laps_required = max_lap_count / 2
        else:
            min_laps_required = 0

        # Tworzenie listy wyników
        results = []
        best_lap_times = []
        for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
            drivers = line['car']['drivers']
            driver_names = [driver['lastName'] for driver in drivers]
            driver_names_str = ", ".join(driver_names)
            total_time_ms = line['driverTotalTimes'][0]
            best_lap_ms = line['timing'].get('bestLap', 0)
            lap_count = line['timing'].get('lapCount', 0)  # Liczba okrążeń

            if lap_count < min_laps_required:
                # Kierowca nie przejechał połowy okrążeń
                total_time_str = DNF_TEXT
                best_lap_str = DNF_TEXT
                points_awarded = 0
            else:
                # Kierowca przejechał wymaganą liczbę okrążeń
                total_time_str = convert_time(total_time_ms)
                best_lap_str = convert_time(best_lap_ms)
                points_awarded = points[i] if i < len(points) else 1

            # Dodawanie danych do listy wyników
            results.append([
                i + 1,  # Pozycja (zgodnie z kolejnością w pliku JSON)
                driver_names_str,  # Kierowca
                total_time_str,  # Łączny czas
                best_lap_str,  # Najlepsze okrążenie
                lap_count,  # Liczba okrążeń
                points_awarded  # Punkty
            ])
            best_lap_times.append(best_lap_ms)  # Dodaj najlepszy czas okrążenia do listy
        
        # Dodawanie nagłówka kolumn
        results.insert(0, ['Pozycja', 'Kierowca', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty'])

        # Znajdowanie najszybszego okrążenia
        if best_lap_times:
            fastest_lap_time = min(best_lap_times)
            fastest_lap_time_converted = convert_time(fastest_lap_time)
        else:
            fastest_lap_time_converted = None

        # Zapisywanie wyników do pliku CSV
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(results)

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
        for j, header in enumerate(results[0]):
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
        for i, row in enumerate(results[1:], start=1):  # Pomijamy nagłówki kolumn
            y_position = result_y_start + (i - 1) * result_line_height
            for j, cell in enumerate(row):
                x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                text_bbox = draw.textbbox((0, 0), str(cell), font=font)
                text_width = text_bbox[2] - text_bbox[0]
                if cell == DNF_TEXT:  # Kolumna z DNF
                    draw.text((x_position - text_width // 2, y_position), str(cell), fill=DNF_COLOR, font=font)
                elif j == 3 and cell == fastest_lap_time_converted:  # Kolumna "Naj. okrążenie" i najszybszy czas
                    draw.text((x_position - text_width // 2, y_position), str(cell), fill=MAGENTA_COLOR, font=font)
                else:
                    draw.text((x_position - text_width // 2, y_position), str(cell), fill=DEFAULT_COLOR, font=font)

        # Zapisywanie obrazu
        bg_image.save(output_image_file)
        print(f"Ranking został zapisany do pliku: {output_image_file}")

        # Usuwanie przetworzonego pliku JSON
        os.remove(json_file)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {json_file}: {e}")
    except KeyError as e:
        print(f"Missing key in JSON file {json_file}: {e}")
        # Wyświetlenie pełnej struktury JSON w przypadku błędu
        with open(json_file, 'r', encoding='utf-16-le') as file:
            print(json.load(file))
    except Exception as e:
        print(f"An error occurred processing file {json_file}: {e}")
