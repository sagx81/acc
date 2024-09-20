import os
import json
import pandas as pd
import glob

# Funkcja konwertująca czas w milisekundach do formatu mm:ss:ms
def convert_time(ms):
    total_sec = ms / 1000
    minutes = int(total_sec / 60)
    seconds = int(total_sec % 60)
    milliseconds = int(ms % 1000)
    return f" {minutes:02}:{int(seconds):02}:{int(milliseconds):03}"

# stworz folder z wynikami jesli nie istnieje
newpath = r'.\wyniki' 
if not os.path.exists(newpath):
    os.makedirs(newpath)

# Ścieżki do katalogów
input_dir = r"."
output_dir = r"./wyniki"
#output_file = os.path.join(output_dir, "wynik.csv")

# Punktacja za miejsca
points = [20, 16, 13, 11, 9, 7, 5, 4, 3, 2, 1, 1, 1, 1, 1]

print(f"Start")

# Przetwarzanie każdego pliku JSON w katalogu wejściowym
for json_file in glob.glob(os.path.join(input_dir, "*.json")):
    try:        
        print(json_file)

        with open(json_file, 'r', encoding='utf-16') as file:
            data = json.load(file)
            print(f"Processing file: {json_file}")
        
        print(f"file opened")
        
        output_file = os.path.join(output_dir,data['trackName']+"_"+data['sessionType']+"_"+str(data['sessionIndex'])+".csv")

        # Tworzenie listy wyników
        results = []
        for i, line in enumerate(data['sessionResult']['leaderBoardLines']):
            drivers = line['car']['drivers']
            driver_names = [driver['lastName'] for driver in drivers]
            driver_names_str = ", ".join(driver_names)
            total_time_ms = line['timing']['totalTime']
            #total_time_ms = line['timing']['driverTotalTimes'][0]
            best_lap_ms = line['timing']['bestLap']
            
            # Dodawanie danych do listy wyników
            results.append([
                i + 1,  # Pozycja (liczby naturalne, zaczynając od 1)
                driver_names_str,  # Kierowca
                convert_time(total_time_ms),  # Łączny czas
                convert_time(best_lap_ms),  # Najlepsze okrążenie
                points[i] if i < len(points) else 1  # Punkty
            ])
        
        # Sortowanie wyników według łącznego czasu
        results.sort(key=lambda x: x[0])
        
        # Tworzenie DataFrame i zapisywanie do CSV
        df = pd.DataFrame(results, columns=['Pozycja', 'Kierowca', 'Laczny czas', 'Najlepsze okrazenie', 'Punkty'])
        df.to_csv(output_file, index=False, encoding='utf-8')

        print(f"Ranking został zapisany do pliku: {output_file}")
        
        # Usuwanie przetworzonego pliku JSON
        #os.remove(json_file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {json_file}: {e}")
    except Exception as e:
        print(f"An error occurred processing file {json_file}: {e}")


