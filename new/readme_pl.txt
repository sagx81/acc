- wymagania:
python3 -m pip install requests
python3 -m pip install Pillow
python3 -m pip install PyQt5


- start aplikacji: 

cd .../new
python start.py
python3 start.py


new/penalties.csv - kary

Funkcjonalnosc:
- pobiera pliki z ftp (wymaga konfiguracji fptDetails w katalogu /ftp wedle instrukcji w katalogu /ftp)
- obrabia wyniki z ftp i wrzuca wyniki do output_phase1
- na obrobione wyniki naklada kary z pliku /penalties_apply/penalties.csv (na razie trzeba je uzupelniac recznie). 
- z przerobionych wynikow indywidualnych tworzona jest grafika z wynikami
- z przerobionych wynikow indywidualnych tworzona jest klasyfikacja generalna
- 