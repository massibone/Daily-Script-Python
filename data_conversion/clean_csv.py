# usage: python clean_csv.py input.csv output.csv --drop-na --dedupe --standardize-date date_column

"""
CSV cleaning utility tool
Funzioni:
 - rimuove duplicati
 - rimuove righe con valori mancanti
 - standardizza colonne data (ISO8601)
 - rinomina colonne in modo coerente
 - filtra colonne selezionate
"""

import argparse
import pandas as pd
import sys
from datetime import datetime


def standardize_date_column(df, column_name):
    """Converte date in formato ISO YYYY-MM-DD."""
    if column_name not in df.columns:
        print(f"[WARN] Colonna {column_name} non trovata")
        return df
    
    df[column_name] = pd.to_datetime(df[column_name], errors='coerce').dt.date
    print(f"[OK] Convertita colonna {column_name} in formato ISO")
    return df


def rename_columns(df):
    """Rende i nomi colonna uniformi: minuscolo + underscore."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    print("[OK] Colonne uniformate")
    return df


def clean_csv(input_file, output_file, drop_na=False, dedupe=False, date_columns=None, keep_columns=None):
    try:
        df = pd.read_csv(input_file)
        print(f"[INFO] Caricato: {input_file}  ({len(df)} righe)")
    except Exception as e:
        print(f"[ERRORE] Impossibile leggere il file CSV → {e}")
        sys.exit(1)

    df = rename_columns(df)

    if keep_columns:
        df = df[keep_columns]
        print(f"[OK] Mantenute solo colonne: {', '.join(keep_columns)}")

    if drop_na:
        before = len(df)
        df = df.dropna()
        print(f"[OK] Rimosse {before - len(df)} righe con valori mancanti")

    if dedupe:
        before = len(df)
        df = df.drop_duplicates()
        print(f"[OK] Rimossi {before - len(df)} duplicati")

    if date_columns:
        for col in date_columns:
            df = standardize_date_column(df, col)

    df.to_csv(output_file, index=False)
    print(f"[DONE] File pulito salvato → {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Tool rapido per pulizia CSV con pandas")
    parser.add_argument("input", help="File CSV in ingresso")
    parser.add_argument("output", help="File CSV pulito")

    parser.add_argument("--drop-na", action="store_true", help="Rimuove righe con valori nulli")
    parser.add_argument("--dedupe", action="store_true", help="Elimina duplicati")
    parser.add_argument("--date", nargs="+", default=None, help="Colonne da convertire in data standard")
    parser.add_argument("--keep", nargs="+", default=None, help="Mantieni solo le colonne indicate")

    args = parser.parse_args()

    clean_csv(
        args.input,
        args.output,
        drop_na=args.drop_na,
        dedupe=args.dedupe,
        date_columns=args.date,
        keep_columns=args.keep,
    )

if __name__ == "__main__":
    main()

