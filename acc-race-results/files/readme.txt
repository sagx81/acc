1. Pobieram plik z FTP z nazwą zawierającą "R" w końcówce. Np: 240908_211253_R
2. Wrzucam plik do katalogu \\ApsDir\Input
3. Uruchamiam skrypt race-results. Skrypt pobiera:
input_dir = os.path.join(project_root, "acc", "input") - źródło pliku .json
output_dir = os.path.join(project_root, "acc", "output", "GT3 S2") - ścieżka do wyjścia plików .png oraz .csv z wynikami
background_image = os.path.join(project_root, "files", "background", "race results.png") - szata graficzna wyników
font_path = os.path.join(project_root, "files", "fonts", "BigShouldersDisplay-Bold.ttf") - czcionka użyta do generowania napisów
4. Plik wynikowy trafia, do "output", gdzie następnie uruchamiam skrypt KG_"dana seria".json. 
5. W katalogu output po pierwszym uruchomieniu skryptu tworzy się plik klasyfikacja_generalna, oraz "pliki przeprocesowane" - trzeba go kasować przed nowym użyciem, bo inaczej pominie ten plik. To taki chwilowy bezpiecznik.  
6. Skrypt pobiera dane z csv klasyfikacji generalnej oraz świeżego race-results, zapisanego w katalogu \\output\docelowa seria. 
7. Pliki csv z race-results wrzucam do Archiwum (bezpiecznik nr 2, gdybym coś spieprzył :) )
8. W katalogu \\output\docelowa seria\ mam pliki graficzne oraz csv. 