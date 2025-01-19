1. Dodaj kary do pliku penalties.csv (id kierowcy z rezultatow/wyscigu a nie nickname z discord: czasami sie roznia)
2. Odpal penalties-apply.py   

Opis:
Skrypt przejdzie po katalogu output/liga(seria) i podejmie kazdy plik .csv. Gdy znajdzie w 'penalties.csv' pasujacy typ:
serii, sezon, tor, wyscig to zaaplikuje kary na dostepnym pliku wynikow. 

Robi kopie pliku wejsciowego (na wszelki wypadek jakby trzeba bylo wrocic do oryginalnych wynikow)
Nadpisuje plik 'wejsciowy' aby byl uwzgledniony w KG (klasyfikacja generalna)

TODO:
- do zastanowienia czy nie dodac dodatkowej flagi w pliku wejsciowym z karami (penalties.csv) w ktorym oznaczymy 'przeprocesowane' kary 
    aby juz ich nie podejmowac (mozna byloby trzymac cala historie kar w penalties.csv) - potem mozna ciekawe statystyki z tego wyciagnac :)