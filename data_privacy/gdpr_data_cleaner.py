import pandas as pd
import argparse
import re
from typing import List, Optional


def pulisci_dati_gdpr(
    input_file: str,
    output_file: Optional[str] = None,
    colonne_da_pulire: Optional[List[str]] = None,
    colonne_da_ignorare: Optional[List[str]] = None,
    id_nome: str = "CUSTOMER",
    id_email: str = "EMAIL",
    id_telefono: str = "PHONE",
    id_indirizzo: str = "ADDRESS"
) -> pd.DataFrame:
    """
    Pulisce un file CSV da dati personali per conformità GDPR.
    Sostituisce nomi, email, telefoni e indirizzi con token pseudonimi consistenti.

    Fix rispetto alla versione precedente:
    - Counter inizializzati a 0 e incrementati dentro la closure (era: partenza
      da 1 + incremento prima dell'uso → primo token era _002).
    - nonlocal counters rimosso: mutare un dict non richiede nonlocal.
    - Mappe di consistenza: la stessa entità riceve sempre lo stesso token
      (requisito GDPR per pseudonimizzazione coerente).
    - .astype(str) applicato una volta sola per colonna, prima di tutti i pattern.
    - Pattern indirizzo corretto per formato italiano reale:
      "Via Roma 1, 20121 Milano" invece del formato anglosassone.

    Args:
        input_file: Percorso del file CSV di input.
        output_file: Percorso del file CSV di output (opzionale).
        colonne_da_pulire: Lista di colonne da pulire. Se None, pulisce tutte
                           le colonne di tipo object.
        colonne_da_ignorare: Lista di colonne da NON pulire (es. 'id', 'prodotto').
        id_nome: Prefisso per nomi/cognomi (default: "CUSTOMER").
        id_email: Prefisso per email (default: "EMAIL").
        id_telefono: Prefisso per telefoni (default: "PHONE").
        id_indirizzo: Prefisso per indirizzi (default: "ADDRESS").

    Returns:
        DataFrame con dati anonimizzati.
    """
    df = pd.read_csv(input_file)

    if colonne_da_pulire is None:
        colonne_da_pulire = [col for col in df.columns if df[col].dtype == 'object']
    if colonne_da_ignorare:
        colonne_da_pulire = [col for col in colonne_da_pulire if col not in colonne_da_ignorare]

    # --- Mappe di consistenza: entità → token ---
    nome_map: dict[str, str] = {}
    email_map: dict[str, str] = {}
    telefono_map: dict[str, str] = {}
    indirizzo_map: dict[str, str] = {}

    # Counter inizializzati a 0: vengono incrementati PRIMA dell'assegnazione
    # così il primo token è sempre _001
    counters = {'nome': 0, 'email': 0, 'telefono': 0, 'indirizzo': 0}

    def sostituisci_nome_cognome(match):
        testo = match.group(0)
        if testo not in nome_map:
            counters['nome'] += 1
            nome_map[testo] = f"{id_nome}_{counters['nome']:03d}"
        return nome_map[testo]

    def sostituisci_email(match):
        testo = match.group(0)
        if testo not in email_map:
            counters['email'] += 1
            email_map[testo] = f"{id_email}_{counters['email']:03d}@example.com"
        return email_map[testo]

    def sostituisci_telefono(match):
        testo = match.group(0)
        if testo not in telefono_map:
            counters['telefono'] += 1
            telefono_map[testo] = f"{id_telefono}_{counters['telefono']:03d}"
        return telefono_map[testo]

    def sostituisci_indirizzo(match):
        testo = match.group(0)
        if testo not in indirizzo_map:
            counters['indirizzo'] += 1
            indirizzo_map[testo] = f"{id_indirizzo}_{counters['indirizzo']:03d}"
        return indirizzo_map[testo]

    # Pattern per identificare dati sensibili
    patterns = {
        'nome_cognome': re.compile(r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'),
        'email': re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b'),
        'telefono': re.compile(
            r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ),
        # Formato italiano: "Via Roma 1, 20121 Milano" oppure "Via Roma, 1 - 20121 Milano"
        'indirizzo': re.compile(
            r'\b(?:Via|Viale|Piazza|Corso|Largo|Vicolo)\s+[\w\s]+,?\s*\d{1,5}'
            r'(?:\s*[-,]\s*\d{5}\s+[\w\s]+)?',
            re.IGNORECASE
        )
    }

    for col in colonne_da_pulire:
        if col not in df.columns:
            continue

        # Converti a stringa una volta sola per tutta la colonna
        df[col] = df[col].astype(str)

        df[col] = df[col].apply(lambda x: patterns['nome_cognome'].sub(sostituisci_nome_cognome, x))
        df[col] = df[col].apply(lambda x: patterns['email'].sub(sostituisci_email, x))
        df[col] = df[col].apply(lambda x: patterns['telefono'].sub(sostituisci_telefono, x))
        df[col] = df[col].apply(lambda x: patterns['indirizzo'].sub(sostituisci_indirizzo, x))

    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Dati puliti salvati in: {output_file}")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pulizia dati personali per conformità GDPR.")
    parser.add_argument("input_file", help="Percorso del file CSV di input.")
    parser.add_argument("--output", help="Percorso del file CSV di output (opzionale).", default=None)
    parser.add_argument("--colonne", nargs='+', help="Colonne specifiche da pulire (opzionale).", default=None)
    parser.add_argument("--ignora", nargs='+', help="Colonne da ignorare (opzionale).", default=None)
    args = parser.parse_args()

    pulisci_dati_gdpr(
        input_file=args.input_file,
        output_file=args.output,
        colonne_da_pulire=args.colonne,
        colonne_da_ignorare=args.ignora
    )
