- start aplikacji: 

python start.py
python3 start.py


Funkcjonalnosc:
- pobiera pliki z ftp (wymaga konfiguracji fptDetails w katalogu /ftp wedle instrukcji w katalogu /ftp)
- obrabia wyniki z ftp i wrzuca wyniki do output_phase1
- na obrobione wyniki naklada kary z pliku /penalties_apply/penalties.csv (na razie trzeba je uzupelniac recznie). 
- z przerobionych wynikow indywidualnych tworzona jest grafika z wynikami
- z przerobionych wynikow indywidualnych tworzona jest klasyfikacja generalna
- 