import re
from collections import defaultdict

def analizza_log(file_path):
    errori = defaultdict(int)
    with open(file_path, 'r') as file:
        for linea in file:
            if "ERROR" in linea:
                match = re.search(r"ERROR: (.+?)(?= -|$)", linea)
                if match:
                    errore = match.group(1)
                    errori[errore] += 1
    return errori

def genera_report(errori):
    with open("report_errori.txt", "w") as report:
        report.write("=== REPORT ERRORI ===\n")
        for errore, conteggio in errori.items():
            report.write(f"{errore}: {conteggio}\n")

# Esempio di utilizzo
file_log = "esempio.log"
errori = analizza_log(file_log)
genera_report(errori)
print("Report generato con successo!")
-------
genera_report_csv.py
import pandas as pd

def genera_report_csv(file_path):
    df = pd.read_csv(file_path)
    report = {
        "Numero di record": len(df),
        "Media": df.mean(numeric_only=True).to_dict(),
        "Somma": df.sum(numeric_only=True).to_dict()
    }
    return report

# Esempio di utilizzo
file_csv = "dati.csv"
report = genera_report_csv(file_csv)
print("Report generato:")
print(report)
