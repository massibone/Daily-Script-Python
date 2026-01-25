import re
import json
import pandas as pd
from datetime import datetime

def filtra_log_per_data(file_path, formato, data_inizio=None, data_fine=None):
    if formato == "testo":
        return filtra_testo_per_data(file_path, data_inizio, data_fine)
    elif formato == "csv":
        return filtra_csv_per_data(file_path, data_inizio, data_fine)
    elif formato == "json":
        return filtra_json_per_data(file_path, data_inizio, data_fine)

def filtra_testo_per_data(file_path, data_inizio, data_fine):
    log_filtrato = []
    with open(file_path, 'r') as file:
        for linea in file:
            # Estrai la data (es. "2026-01-20 10:00:00")
            match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", linea)
            if match:
                data_log = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                if (data_inizio is None or data_log >= data_inizio) and (data_fine is None or data_log <= data_fine):
                    log_filtrato.append(linea.strip())
    return log_filtrato

def filtra_csv_per_data(file_path, data_inizio, data_fine):
    df = pd.read_csv(file_path)
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"])
        if data_inizio:
            df = df[df["Data"] >= data_inizio]
        if data_fine:
            df = df[df["Data"] <= data_fine]
    return df.to_dict("records")

def filtra_json_per_data(file_path, data_inizio, data_fine):
    with open(file_path, 'r') as file:
        dati = json.load(file)
    log_filtrato = []
    for entry in dati:
        if "data" in entry:
            data_log = datetime.strptime(entry["data"], "%Y-%m-%d %H:%M:%S")
            if (data_inizio is None or data_log >= data_inizio) and (data_fine is None or data_log <= data_fine):
                log_filtrato.append(entry)
    return log_filtrato

def genera_report(dati, formato="csv", output_file="report_filtrato"):
    if formato == "csv":
        if isinstance(dati, list) and isinstance(dati[0], str):
            # Se i dati sono righe di testo, scrivile direttamente
            with open(f"{output_file}.csv", 'w') as f:
                f.write("\n".join(dati))
        else:
            # Se i dati sono un dizionario o una lista di dizionari, usa pandas
            df = pd.DataFrame(dati)
            df.to_csv(f"{output_file}.csv", index=False)
    elif formato == "json":
        with open(f"{output_file}.json", 'w') as f:
            json.dump(dati, f, indent=4, default=str)
    print(f"Report generato: {output_file}.{formato}")

# Esempio di utilizzo
if __name__ == "__main__":
    file_input = "log.txt"  # Sostituisci con il tuo file
    formato_input = "testo"  # "testo", "csv", o "json"
    data_inizio = datetime.strptime("2026-01-20 00:00:00", "%Y-%m-%d %H:%M:%S")
    data_fine = datetime.strptime("2026-01-20 23:59:59", "%Y-%m-%d %H:%M:%S")

    dati_filtrati = filtra_log_per_data(file_input, formato_input, data_inizio, data_fine)
    genera_report(dati_filtrati, formato="csv", output_file="report_filtrato_per_data")
----------------
filter_log_by_ip.py 
# filter_log_by_ip.py
import re
import json
import pandas as pd

def filtra_log_per_ip(file_path, formato, ip_list):
    if formato == "testo":
        return filtra_testo_per_ip(file_path, ip_list)
    elif formato == "csv":
        return filtra_csv_per_ip(file_path, ip_list)
    elif formato == "json":
        return filtra_json_per_ip(file_path, ip_list)

def filtra_testo_per_ip(file_path, ip_list):
    log_filtrato = []
    with open(file_path, 'r') as file:
        for linea in file:
            for ip in ip_list:
                if f"IP: {ip}" in linea:
                    log_filtrato.append(linea.strip())
                    break
    return log_filtrato

def filtra_csv_per_ip(file_path, ip_list):
    df = pd.read_csv(file_path)
    if "IP" in df.columns:
        df = df[df["IP"].isin(ip_list)]
    return df.to_dict("records")

def filtra_json_per_ip(file_path, ip_list):
    with open(file_path, 'r') as file:
        dati = json.load(file)
    log_filtrato = []
    for entry in dati:
        if "IP" in entry and entry["IP"] in ip_list:
            log_filtrato.append(entry)
    return log_filtrato

def genera_report(dati, formato="csv", output_file="report_filtrato"):
    if formato == "csv":
        if isinstance(dati, list) and isinstance(dati[0], str):
            with open(f"{output_file}.csv", 'w') as f:
                f.write("\n".join(dati))
        else:
            df = pd.DataFrame(dati)
            df.to_csv(f"{output_file}.csv", index=False)
    elif formato == "json":
        with open(f"{output_file}.json", 'w') as f:
            json.dump(dati, f, indent=4, default=str)
    print(f"Report generato: {output_file}.{formato}")

# Esempio di utilizzo
if __name__ == "__main__":
    file_input = "log.txt"  # Sostituisci con il tuo file
    formato_input = "testo"  # "testo", "csv", o "json"
    ip_list = ["192.168.1.1", "192.168.1.2"]  # Lista di IP da filtrare

    dati_filtrati = filtra_log_per_ip(file_input, formato_input, ip_list)
    genera_report(dati_filtrati, formato="csv", output_file="report_filtrato_per_ip")

