import re
from collections import defaultdict
import pandas as pd

def analizza_log(file_path):
    accessi_per_ip = defaultdict(int)
    errori = []
    with open(file_path, 'r') as file:
        for linea in file:
            if "Errore:" in linea:
                errori.append(linea.strip())
            else:
                ip = re.search(r"IP: (\d+\.\d+\.\d+\.\d+)", linea)
                if ip:
                    accessi_per_ip[ip.group(1)] += 1
    return accessi_per_ip, errori

def genera_report(accessi_per_ip, errori, output_csv="report_accessi.csv"):
    df_accessi = pd.DataFrame(accessi_per_ip.items(), columns=["IP", "Accessi"])
    df_accessi.to_csv(output_csv, index=False)
    with open("report_errori.txt", "w") as f:
        f.write("\n".join(errori))
    print(f"Report generato: {output_csv} e report_errori.txt")

# Esempio di utilizzo
file_log = "accessi.log"
accessi, errori = analizza_log(file_log)
genera_report(accessi, errori)
