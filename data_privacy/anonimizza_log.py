import re
import argparse
from datetime import datetime

def anonimizza_log(input_file, output_file=None):
    """
    Anonimizza un file di log sostituendo:
    - Indirizzi IP con "IP_[ID]"
    - Nomi utente con "USER_[ID]"
    - Timestamp con "TIMESTAMP_REDACTED"
    - Percorsi sensibili con "PATH_REDACTED"

    Args:
        input_file (str): Percorso del file di log da anonimizzare.
        output_file (str, optional): Percorso del file di output. Se None, stampa a schermo.
    """

    # Inizializza contatori per IP e utenti
    ip_counter = 1
    user_counter = 1

    # Espressioni regolari per identificare i dati sensibili
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    user_pattern = re.compile(r'\buser\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    timestamp_pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\b')
    path_pattern = re.compile(r'\b(/[\w/.-]+)+')

    def replace_ip(match):
        nonlocal ip_counter
        replaced = f"IP_{ip_counter:03d}"
        ip_counter += 1
        return replaced

    def replace_user(match):
        nonlocal user_counter
        replaced = f"USER_{user_counter:03d}"
        user_counter += 1
        return f"user '{replaced}'"

    def replace_timestamp(match):
        return "TIMESTAMP_REDACTED"

    def replace_path(match):
        return "PATH_REDACTED"

    # Leggi il file di input
    with open(input_file, 'r') as f:
        log_lines = f.readlines()

    # Elabora ogni linea
    anonimized_lines = []
    for line in log_lines:
        line = ip_pattern.sub(replace_ip, line)
        line = user_pattern.sub(replace_user, line)
        line = timestamp_pattern.sub(replace_timestamp, line)
        line = path_pattern.sub(replace_path, line)
        anonimized_lines.append(line)

    # Scrivi l'output
    if output_file:
        with open(output_file, 'w') as f:
            f.writelines(anonimized_lines)
        print(f"Log anonimizzati salvati in: {output_file}")
    else:
        print("".join(anonimized_lines))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anonimizza file di log.")
    parser.add_argument("input_file", help="Percorso del file di log da anonimizzare.")
    parser.add_argument("--output", help="Percorso del file di output (opzionale).", default=None)
    args = parser.parse_args()

    anonimizza_log(args.input_file, args.output)
