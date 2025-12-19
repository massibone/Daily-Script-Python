
'''
Converte un file JSON in un file CSV utilizzando la libreria pandas.
Esempio d'uso (nel tuo script principale o nella console Python):
    import json2csv
    json2csv.convert("dati_input.json", "dati_output.csv")
'''

import pandas as pd
import os

def convert(json_file_path: str, csv_file_path: str):
    """
    Converte un file JSON specificato in un file CSV.

    Args:
        json_file_path (str): Il percorso del file JSON da leggere.
        csv_file_path (str): Il percorso del file CSV da scrivere.
    """
    if not os.path.exists(json_file_path):
        print(f"Errore: Il file JSON specificato non esiste: {json_file_path}")
        return

    try:
        # Legge il file JSON in un DataFrame di pandas.
        # Usa orient='records' per gestire i JSON con una lista di oggetti.
        # Se il JSON è una singola riga (es. un dizionario), potresti dover usare pd.Series
        # o adattare a seconda della struttura.
        df = pd.read_json(json_file_path, orient='records')

        # Scrive il DataFrame in un file CSV.
        # index=False evita che pandas scriva l'indice numerico come colonna nel CSV.
        df.to_csv(csv_file_path, index=False)

        print(f"✅ Conversione completata con successo!")
        print(f"Il file '{json_file_path}' è stato convertito in '{csv_file_path}'.")

    except ValueError as e:
        print(f"❌ Errore nella lettura/conversione del JSON. Verifica la struttura del file.")
        print(f"Dettagli: {e}")
    except Exception as e:
        print(f"❌ Si è verificato un errore inatteso: {e}")

# L'uso di questo blocco permette di eseguire il file direttamente
# per esempio come test o per un uso semplice da riga di comando.
if __name__ == "__main__":
    print("Per usare questa funzione, importala nel tuo script:")
    print("import json2csv")
    print("json2csv.convert('nome_file.json', 'output.csv')")

