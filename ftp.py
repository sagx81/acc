import ftplib
import json
import glob

# wymagany plik ftpDetails.json z host/port/username/password (utf-8)
ftpDetails = 'ftpDetails.json'

with open(ftpDetails, 'r', encoding='utf-8') as file:
    data = json.load(file)

print(f"Processing file: {ftpDetails}")
        
host = data['host']
port = data['port']
username = data['username']
password = data['password']

print(f"FTP Details received, connecting...")

ftp = ftplib.FTP()

ftp.connect(host, port)
ftp.login(username, password)

items = ftp.dir('results')
ftp.quit()

print("items in the directory: ", items)

#ftp.dir() # detailed listing

