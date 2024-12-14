import ftplib
import json
import os
from utils_entities import constants

#import constants

def get_ftp_files():

    
    ftpDetails_path = os.path.join(os.path.curdir, "ftp", "ftpDetails.json")
    
    # Stwórz folder z plikami z FTP, jeśli nie istnieje
    newpath = constants.files_from_ftp
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Odczytaj plik JSON
    with open(ftpDetails_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # print(f"Odczytane dane z pliku ftpDetails.json")

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

        # Race
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
            print("No files with 'R' postifx") #Brak plików kończących się na literę 'R' do przetworzenia")



        # Qualify
        # Pobieraj tylko pliki kończące się na literę 'Q'
        files_with_Q = [file for file in files if file.endswith('Q.json')]
        
        if files_with_Q:
            for file in files_with_Q:
                local_file = os.path.join(newpath, file)
                # Przerwij pobieranie, jeśli plik już istnieje
                if os.path.exists(local_file):
                    continue
                else:
                    with open(local_file, 'wb') as f:
                        ftp.retrbinary("RETR " + file, f.write)
        else:
            print("No files with 'Q' postfix") #Brak plików kończących się na literę 'Q' do przetworzenia")
   
    else:
        print("No files to process") #Brak plików do przetworzenia")

    print(f"FTP Done") # Kończymy pracę")
    ftp.quit()
