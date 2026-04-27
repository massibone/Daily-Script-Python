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
    Sostituisce nomi, cognomi, email, telefoni e indirizzi con identificatori generici.

    Args:
        input_file: Percorso del file CSV di input.
        output_file: Percorso del file CSV di output (opzionale).
        colonne_da_pulire: Lista di colonne da pulire. Se None, pulisce tutte le colonne di tipo stringa.
        colonne_da_ignorare: Lista di colonne da NON pulire (es. 'id', 'prodotto').
        id_nome: Prefisso per nomi/cognomi (default: "CUSTOMER").
        id_email: Prefisso per email (default: "EMAIL").
        id_telefono: Prefisso per telefoni (default: "PHONE").
        id_indirizzo: Prefisso per indirizzi (default: "ADDRESS").

    Returns:
        DataFrame con dati anonimizzati.
    """
    # Leggi il file CSV
    df = pd.read_csv(input_file)

    # Se non specificato, pulisci tutte le colonne di tipo stringa (escludendo quelle da ignorare)
    if colonne_da_pulire is None:
        colonne_da_pulire = [col for col in df.columns if df[col].dtype == 'object']
    if colonne_da_ignorare:
        colonne_da_pulire = [col for col in colonne_da_pulire if col not in colonne_da_ignorare]

    # Inizializza contatori
    counters = {
        'nome': 1,
        'email': 1,
        'telefono': 1,
        'indirizzo': 1
    }

    # Funzioni di sostituzione
    def sostituisci_nome_cognome(match):
        nonlocal counters
        counters['nome'] += 1
        return f"{id_nome}_{counters['nome']:03d}"

    def sostituisci_email(match):
        nonlocal counters
        counters['email'] += 1
        return f"{id_email}_{counters['email']:03d}@example.com"

    def sostituisci_telefono(match):
        nonlocal counters
        counters['telefono'] += 1
        return f"{id_telefono}_{counters['telefono']:03d}"

    def sostituisci_indirizzo(match):
        nonlocal counters
        counters['indirizzo'] += 1
        return f"{id_indirizzo}_{counters['indirizzo']:03d}"

    # Pattern per identificare dati sensibili
    patterns = {
        'nome_cognome': re.compile(r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'),
        'email': re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b'),
        'telefono': re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
        'indirizzo': re.compile(r'\b\d{1,5}\s+[\w\s]+,\s*[\w\s]+,\s*\w{2,5}\s*\d{5}\b')  # Es. "Via Roma 1, Milano, MI 20121"
    }

    # Elabora ogni colonna specificata
    for col in colonne_da_pulire:
        if col in df.columns:
            # Sostituisci nomi e cognomi
            df[col] = df[col].astype(str).apply(
                lambda x: patterns['nome_cognome'].sub(sostituisci_nome_cognome, x)
            )
            # Sostituisci email
            df[col] = df[col].apply(
                lambda x: patterns['email'].sub(sostituisci_email, x)
            )
            # Sostituisci telefoni
            df[col] = df[col].apply(
                lambda x: patterns['telefono'].sub(sostituisci_telefono, x)
            )
            # Sostituisci indirizzi
            df[col] = df[col].apply(
                lambda x: patterns['indirizzo'].sub(sostituisci_indirizzo, x)
            )

    # Salva il risultato
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
