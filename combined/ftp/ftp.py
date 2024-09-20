import ftplib
import json
import os

# def find_project_root(start_path, target_dir_name="acc-race-results"):
#     current_path = start_path
#     while True:
#         if os.path.basename(current_path) == target_dir_name:
#             return current_path
#         parent_path = os.path.dirname(current_path)
#         if parent_path == current_path:
#             raise FileNotFoundError(f"Katalog {target_dir_name} nie został znaleziony w ścieżce: {start_path}")
#         current_path = parent_path

# Ustalanie katalogu głównego projektu
# project_root = find_project_root(os.path.abspath(__file__))

# Zakładamy, że plik FTP znajduje się w katalogu 'ftp' i nazywa się 'ftpDetails.json'


def get_ftp_files():

    
    ftpDetails_path = os.path.join(os.path.curdir, "ftp", "ftpDetails.json")
    
    # Stwórz folder z backupem z FTP, jeśli nie istnieje
    newpath = r'./fromFTP'
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Odczytaj plik JSON
    with open(ftpDetails_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(f"Odczytane dane z pliku ftpDetails.json")

    host = data['host']
    port = data['port']
    username = data['username']
    password = data['password']

    print(f"Łączę do FTP")

    ftp = ftplib.FTP()

    try:
        ftp.connect(host, port)
        ftp.login(username, password)
    except Exception as e:
        print(f"\n !!! Nie udało się połączyć z FTP: {e}\n\n")
        return

    print(f"FTP połączony. Odczytuję pliki z katalogu 'results'")

    ftp.cwd('results')

    try:
        files = [item for item, facts in ftp.mlsd()]
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print("Brak plików w katalogu")
        else:
            raise

    if files:
        # Pobieraj tylko pliki kończące się na literę 'R'
        files_with_R = [file for file in files if file.endswith('R.json')]
        
        if files_with_R:
            for file in files_with_R:
                local_file = os.path.join(newpath, file)
                # Przerwij pobieranie, jeśli plik już istnieje
                if os.path.exists(local_file):
                    continue
                else:
                    with open(local_file, 'wb') as f:
                        ftp.retrbinary("RETR " + file, f.write)
        else:
            print("Brak plików kończących się na literę 'R' do przetworzenia")
    else:
        print("Brak plików do przetworzenia")

    print(f"Kończymy pracę")
    ftp.quit()
