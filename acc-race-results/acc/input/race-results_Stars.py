import os
import json
import glob
import csv
from PIL import Image, ImageDraw, ImageFont
from track_data import track_data

def convert_time(ms):
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    return f"{minutes:02}:{seconds:02}:{milliseconds:03}"

def clean_text(input_string):
    # Usuwa tekst przed \n i sam \n
    return input_string.split('\n')[-1] if '\n' in input_string else input_string

def generate_unique_filename(output_dir, base_name, extension="png"):
    counter = 1
    output_file = os.path.join(output_dir, f"{base_name}.{extension}")
    while os.path.exists(output_file):
        output_file = os.path.join(output_dir, f"{base_name}({counter}).{extension}")
        counter += 1
    return output_file

def find_project_root(start_path, target_dir_name="acc-race-results"):
    current_path = start_path
    while True:
        if os.path.basename(current_path) == target_dir_name:
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            raise FileNotFoundError(f"Katalog {target_dir_name} nie został znaleziony w ścieżce: {start_path}")
        current_path = parent_path

# Wczytywanie pliku teams.json
def load_teams_data(teams_file):
    with open(teams_file, 'r', encoding='utf-8') as file:
        teams_data = json.load(file)
    
    # Tworzymy mapę dla szybkiego odwoływania się po playerID
    driver_to_team = {}
    for team, drivers in teams_data.items():
        for driver_code, driver_info in drivers.items():
            driver_to_team[driver_info['playerID']] = team  # Mapujemy po playerID
    return driver_to_team

# Ustalanie katalogu głównego projektu
project_root = find_project_root(os.path.abspath(__file__))

# Zaktualizowana ścieżka do katalogu wyjściowego
output_dir = os.path.join(project_root, "acc", "output", "Stars")

# Zaktualizowana ścieżka do pliku teams.json
teams_file = os.path.join(project_root, "files", "teams.json")
teams_data = load_teams_data(teams_file)

background_image = os.path.join(project_root, "files", "background", "race results.png")
font_path = os.path.join(project_root, "files", "fonts", "BigShouldersDisplay-Bold.ttf")

points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2, 1, 1, 1, 1, 1]

DNF_TEXT = "DNF"
DNF_COLOR = "red"
DEFAULT_COLOR = "#191919"
MAGENTA_COLOR = "magenta"

for json_file in glob.glob(os.path.join(project_root, "acc", "input", "*.json")):
    try:
        print(f"Processing file: {json_file}")

        with open(json_file, 'r', encoding='utf-16-le') as file:
            data = json.load(file)

        short_name = data.get('trackName', 'unknown_track')
        track_info = track_data.get(short_name, {})
        track_name = track_info.get('name', short_name)

        base_name = os.path.basename(json_file)
        date_part = base_name.split('_')[0]

        base_output_name = f"{short_name}-{date_part}"
        output_image_file = generate_unique_filename(output_dir, base_output_name, extension="png")
        output_csv_file = generate_unique_filename(output_dir, base_output_name, extension="csv")

        lap_counts = [line['timing'].get('lapCount', 0) for line in data['sessionResult']['leaderBoardLines']]
        if lap_counts:
            max_lap_count = max(lap_counts)
            min_laps_required = max_lap_count / 2
        else:
            min_laps_required = 0

        results = []
        best_lap_times = []
        first_driver_time = None
        first_driver_laps = max_lap_count

        for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
            drivers = line['car']['drivers']
            driver_names = [driver['lastName'] for driver in drivers]
            driver_names_str = ", ".join(driver_names)
            
            # Nowa logika: Dodajemy kolumnę Team
            teams = [teams_data.get(driver['playerId'], "") for driver in drivers]  # Puste dla braku dopasowania
            team_name = ", ".join(teams)
            
            total_time_ms = line['timing']['totalTime']
            best_lap_ms = line['timing'].get('bestLap', 0)
            lap_count = line['timing'].get('lapCount', 0)

            # Użyj funkcji clean_text dla team_name lub driver_names_str
            driver_names_str = clean_text(driver_names_str)
            team_name = clean_text(team_name)

            if lap_count < min_laps_required:
                total_time_str = DNF_TEXT
                best_lap_str = DNF_TEXT
                points_awarded = 0
            else:
                if i == 0:
                    first_driver_time = total_time_ms
                    total_time_str = convert_time(total_time_ms)
                else:
                    if lap_count < first_driver_laps:
                        laps_difference = first_driver_laps - lap_count
                        total_time_str = f"+{laps_difference} okrążenie" if laps_difference == 1 else f"+{laps_difference} okrążenia"
                    else:
                        time_difference = total_time_ms - first_driver_time
                        total_time_str = f"+ {convert_time(time_difference)}"

                best_lap_str = convert_time(best_lap_ms)
                points_awarded = points[i] if i < len(points) else 1

            results.append([
                i + 1,
                driver_names_str,
                team_name,  # Dodajemy team do wyników
                total_time_str,
                best_lap_str,
                lap_count,
                points_awarded
            ])
            best_lap_times.append(best_lap_ms)

        # Nagłówki zaktualizowane o odpowiednie kodowanie Windows-1250 przy zapisie
        results.insert(0, ['Pozycja', 'Kierowca', 'Team', 'Łączny czas', 'Naj. okrążenie', 'Okrążenia', 'Punkty'])

        if best_lap_times:
            fastest_lap_time = min(best_lap_times)
            fastest_lap_time_converted = convert_time(fastest_lap_time)
        else:
            fastest_lap_time_converted = None

        # Zapis wyników do pliku CSV z kodowaniem Windows-1250
        with open(output_csv_file, mode='w', newline='', encoding='windows-1250') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(results)

        if not os.path.isfile(background_image):
            raise FileNotFoundError(f"Background image not found: {background_image}")

        bg_image = Image.open(background_image)
        draw = ImageDraw.Draw(bg_image)

        font_size = 47
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Could not load font at {font_path}. Using default font.")
            font = ImageFont.load_default()

        header_x_start = 20
        header_y_start = 145
        header_line_height = 40

        column_widths = [100, 400, 420, 400, 215, 215, 215]

        for j, header in enumerate(results[0]):
            x_position = header_x_start + sum(column_widths[:j]) + column_widths[j] // 2
            text_bbox = draw.textbbox((0, 0), header, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            draw.text((x_position - text_width // 2, header_y_start), str(header), fill="grey", font=font)

        title_text = track_name
        title_bbox = draw.textbbox((0, 0), title_text, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (bg_image.width - title_width) // 2
        title_y = header_y_start - header_line_height - 60

        draw.text((title_x, title_y), title_text, fill="black", font=font)

        result_x_start = 20
        result_y_start = header_y_start + header_line_height + 38
        result_line_height = 96

        for i, row in enumerate(results[1:], start=1):
            y_position = result_y_start + (i - 1) * result_line_height
            for j, cell in enumerate(row):
                x_position = result_x_start + sum(column_widths[:j]) + column_widths[j] // 2
                text_bbox = draw.textbbox((0, 0), str(cell), font=font)
                text_width = text_bbox[2] - text_bbox[0]
                color = DNF_COLOR if "DNF" in str(cell) else DEFAULT_COLOR
                draw.text((x_position - text_width // 2, y_position), str(cell), fill=color, font=font)

        # Zapisujemy obraz wyników do pliku PNG
        bg_image.save(output_image_file)
        print(f"Results saved to: {output_csv_file} and {output_image_file}")

    except Exception as e:
        print(f"Error processing file {json_file}: {e}")
