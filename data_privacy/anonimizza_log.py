import re
import argparse

def anonimizza_log(input_file, output_file=None):
    """
    Anonimizza un file di log sostituendo:
    - Indirizzi IP con "IP_[ID]"
    - Nomi utente con "USER_[ID]"
    - Timestamp con "TIMESTAMP_REDACTED"
    - Percorsi sensibili con "PATH_REDACTED"

    Fix applicati rispetto alla versione precedente:
    - Mappe di consistenza per IP e utenti: lo stesso IP/utente riceve sempre
      lo stesso token nell'intero file (requisito GDPR per pseudonimizzazione
      coerente e per mantenere tracciabilità interna negli audit).
    - path_pattern reso più selettivo: richiede almeno due segmenti (/a/b)
      per evitare di oscurare token operativi brevi come /v1 o /api.

    Args:
        input_file (str): Percorso del file di log da anonimizzare.
        output_file (str, optional): Percorso del file di output.
                                     Se None, stampa a schermo.
    """

    # --- Mappe di consistenza ---
    ip_map: dict[str, str] = {}
    user_map: dict[str, str] = {}

    ip_counter = [1]
    user_counter = [1]

    # --- Pattern ---
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    user_pattern = re.compile(r'\buser\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    timestamp_pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\b')
    # Richiede almeno due segmenti di percorso per ridurre falsi positivi
    path_pattern = re.compile(r'(?:/[\w.-]+){2,}')

    def replace_ip(match):
        ip = match.group(0)
        if ip not in ip_map:
            ip_map[ip] = f"IP_{ip_counter[0]:03d}"
            ip_counter[0] += 1
        return ip_map[ip]

    def replace_user(match):
        username = match.group(1)
        if username not in user_map:
            user_map[username] = f"USER_{user_counter[0]:03d}"
            user_counter[0] += 1
        return f"user '{user_map[username]}'"

    def replace_timestamp(match):
        return "TIMESTAMP_REDACTED"

    def replace_path(match):
        return "PATH_REDACTED"

    with open(input_file, 'r') as f:
        log_lines = f.readlines()

    anonimized_lines = []
    for line in log_lines:
        line = ip_pattern.sub(replace_ip, line)
        line = user_pattern.sub(replace_user, line)
        line = timestamp_pattern.sub(replace_timestamp, line)
        line = path_pattern.sub(replace_path, line)
        anonimized_lines.append(line)

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
