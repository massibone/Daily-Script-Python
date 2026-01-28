import json
import csv
import re
from collections import defaultdict
import pandas as pd
from datetime import datetime

def leggi_file_testo(file_path):
    """Legge un file di testo e restituisce le righe come lista."""
    with open(file_path, 'r') as file:
        return file.readlines()

def leggi_file_csv(file_path):
    """Legge un file CSV e restituisce un DataFrame pandas."""
    return pd.read_csv(file_path)

def leggi_file_json(file_path):
    """Legge un file JSON e restituisce un dizionario o una lista."""
    with open(file_path, 'r') as file:
        return json.load(file)

def analizza_log_testo(righe, campo_chiave="Errore"):
    """Analizza un file di testo e conta le occorrenze di un campo specifico."""
    conteggi = defaultdict(int)
    for riga in righe:
        if campo_chiave in riga:
            match = re.search(rf"{campo_chiave}: (.+?)(?= -|$)", riga)
            if match:
                chiave = match.group(1)
                conteggi[chiave] += 1
    return conteggi

def analizza_log_csv(df, colonna="Tipo"):
    """Analizza un DataFrame e restituisce statistiche per una colonna."""
    return df[colonna].value_counts().to_dict()

def analizza_log_json(dati, chiave="tipo"):
    """Analizza un JSON e conta le occorrenze di una chiave specifica."""
    conteggi = defaultdict(int)
    if isinstance(dati, list):
        for entry in dati:
            if chiave in entry:
                conteggi[entry[chiave]] += 1
    return conteggi

def genera_report(conteggi, formato="csv", output_file="report"):
    """Genera un report in formato CSV o JSON."""
    if formato == "csv":
        with open(f"{output_file}.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Evento", "Conteggio"])
            for evento, conteggio in conteggi.items():
                writer.writerow([evento, conteggio])
    elif formato == "json":
        with open(f"{output_file}.json", 'w') as jsonfile:
            json.dump(conteggi, jsonfile, indent=4)
    print(f"Report generato: {output_file}.{formato}")

# Esempio di utilizzo
if __name__ == "__main__":
    # Scegli il formato del file di input
    formato_input = "testo"  # "testo", "csv", o "json"
    file_input = "log.txt"   # Sostituisci con il tuo file

    # Scegli il formato del report di output
    formato_output = "csv"   # "csv" o "json"
    file_output = "report_log"

    if formato_input == "testo":
        righe = leggi_file_testo(file_input)
        conteggi = analizza_log_testo(righe, campo_chiave="Errore")
    elif formato_input == "csv":
        df = leggi_file_csv(file_input)
        conteggi = analizza_log_csv(df, colonna="Tipo")
    elif formato_input == "json":
        dati = leggi_file_json(file_input)
        conteggi = analizza_log_json(dati, chiave="tipo")

    genera_report(conteggi, formato=formato_output, output_file=file_output)
