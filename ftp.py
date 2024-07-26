import ftplib
import json
import os

# wymagany plik ftpDetails.json z host/port/username/password (utf-8)
ftpDetails = 'ftpDetails.json'

# stworz folder z backupem z FTP jesli nie istnieje
newpath = r'./ftpBackup' 
if not os.path.exists(newpath):
    os.makedirs(newpath)

with open(ftpDetails, 'r', encoding='utf-8') as file:
    data = json.load(file)

print(f"Odczytane dane z pliku ftpDetails.json")


host = data['host']
port = data['port']
username = data['username']
password = data['password']

print(f"Lacze do Ftp")

ftp = ftplib.FTP()

ftp.connect(host, port)
ftp.login(username, password)

print(f"FTP polaczony. Odczytuje pliki z katalogu results")

ftp.cwd('results')

try:
    files = [item for item, facts in ftp.mlsd()]
except ftplib.error_perm as resp:
    if str(resp) == "550 No files found":
        print("Brak plikow w katalogu")
    else:
        raise

if files:
    for file in files:    
        local_file = os.path.join(newpath, file) 
        #przerwij pobieranie jesli plik just istnieje
        if os.path.exists(local_file):
            continue
        else:
            with open(local_file, 'wb') as f:
                ftp.retrbinary("RETR " + file, f.write)
                f.close()
else:
    print("Brak plikow do przetworzenia")


print(f"Konczymy robote")
ftp.quit()
