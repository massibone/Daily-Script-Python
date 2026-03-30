#!/usr/bin/env python3
"""
process_docs.py
Mini-pipeline: scansiona una cartella, estrae tabelle da PDF (e tenta da DOCX/MD),
pulisce e normalizza con Polars e scrive un CSV unificato.

"""

import sys
import os
from pathlib import Path
import tempfile
import logging
import polars as pl
import pandas as pd

# Estrazione PDF
import camelot
import tabula
import pdfplumber

# DOCX/MD
import docx
import pypandoc

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Configurazione utente
INPUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "docs"
OUTPUT_CSV = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd() / "unified_tables.csv"
TEMP_DIR = Path(tempfile.gettempdir()) / "doc_tables_tmp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Mappatura/routine di normalizzazione (adattare)
# Regole: lowercase, rimuovi spazi esterni, sostituisci caratteri non alfanumerici con underscore
def normalize_colname(name: str) -> str:
    if name is None:
        return ""
    return (
        "".join(c if c.isalnum() else "_" for c in name)
        .strip("_")
        .lower()
    )

def try_camelot_extract(pdf_path: str):
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")  # lattice o stream se necessario
        logging.info(f"camelot: trovato {len(tables)} tabelle in {pdf_path}")
        return [t.df for t in tables]
    except Exception as e:
        logging.debug(f"camelot failed on {pdf_path}: {e}")
        return []

def try_tabula_extract(pdf_path: str):
    try:
        dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        logging.info(f"tabula: trovato {len(dfs)} tabelle in {pdf_path}")
        return dfs
    except Exception as e:
        logging.debug(f"tabula failed on {pdf_path}: {e}")
        return []

def try_pdfplumber_extract(pdf_path: str):
    out = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for p in pdf.pages:
                tbls = p.extract_tables()
                for t in tbls:
                    # t è lista di righe; converti in pandas DF
                    df = pd.DataFrame(t[1:], columns=t[0]) if len(t) > 1 else pd.DataFrame(t)
                    out.append(df)
        logging.info(f"pdfplumber: trovato {len(out)} tabelle in {pdf_path}")
    except Exception as e:
        logging.debug(f"pdfplumber failed on {pdf_path}: {e}")
    return out

def extract_tables_from_pdf(path: Path):
    # Ordine: camelot -> tabula -> pdfplumber
    dfs = []
    dfs += try_camelot_extract(str(path))
    if not dfs:
        dfs += try_tabula_extract(str(path))
    if not dfs:
        dfs += try_pdfplumber_extract(str(path))
    # Convertire tutti in pandas.DataFrame coerente
    normalized = []
    for d in dfs:
        if isinstance(d, pl.DataFrame):
            d = d.to_pandas()
        elif isinstance(d, list):
            d = pd.DataFrame(d)
        normalized.append(d)
    return normalized

def extract_tables_from_docx(path: Path):
    docs = []
    try:
        doc = docx.Document(str(path))
        for tbl in doc.tables:
            data = []
            keys = None
            for i, row in enumerate(tbl.rows):
                text = [cell.text.strip() for cell in row.cells]
                if i == 0:
                    keys = text
                else:
                    data.append(text)
            if keys:
                docs.append(pd.DataFrame(data, columns=keys))
            else:
                docs.append(pd.DataFrame(data))
        logging.info(f"docx: trovato {len(docs)} tabelle in {path}")
    except Exception as e:
        logging.debug(f"docx failed on {path}: {e}")
    return docs

def extract_tables_from_markdown(path: Path):
    # Usa pandoc per convertire MD in HTML poi parse tabelle semplici via pandas.read_html
    out = []
    try:
        html = pypandoc.convert_file(str(path), "html")
        dfs = pd.read_html(html)
        out.extend(dfs)
        logging.info(f"md: trovato {len(dfs)} tabelle in {path}")
    except Exception as e:
        logging.debug(f"markdown extraction failed on {path}: {e}")
    return out

def clean_dataframe(df: pd.DataFrame, source_file: str) -> pl.DataFrame:
    # Rimuovi colonne vuote totali, strip stringhe, normalize colnames, infer types con polars
    df = df.copy()
    # Trim strings
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip().replace({"": None})
    # Drop fully-empty cols
    df.dropna(axis=1, how="all", inplace=True)
    # Normalize column names
    df.columns = [normalize_colname(str(c)) or f"col_{i}" for i, c in enumerate(df.columns)]
    # Add provenance
    df["_source_file"] = source_file
    # Convert to polars, infer dtypes
    pl_df = pl.from_pandas(df).with_columns([
        pl.col(c).cast(pl.Utf8) if pl.col(c).dtype == pl.Utf8 else pl.col(c)
        for c in pl.from_pandas(df).columns
    ])
    return pl_df

def unify_tables(dfs: list[pl.DataFrame]):
    if not dfs:
        return pl.DataFrame()
    # Compute superset of columns
    all_cols = []
    for df in dfs:
        for c in df.columns:
            if c not in all_cols:
                all_cols.append(c)
    # Align columns (missing filled with null)
    aligned = []
    for df in dfs:
        for c in all_cols:
            if c not in df.columns:
                df = df.with_columns(pl.lit(None).alias(c))
        # reorder
        df = df.select(all_cols)
        aligned.append(df)
    return pl.concat(aligned, how="vertical")

def process_folder(input_dir: Path):
    collected = []
    for path in sorted(input_dir.rglob("*")):
        if path.is_dir():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                pdf_tables = extract_tables_from_pdf(path)
                for t in pdf_tables:
                    if isinstance(t, pl.DataFrame):
                        df = t
                    else:
                        df = t
                    cleaned = clean_dataframe(df, str(path.name))
                    collected.append(cleaned)
            elif suffix in (".docx",):
                tbls = extract_tables_from_docx(path)
                for t in tbls:
                    cleaned = clean_dataframe(t, str(path.name))
                    collected.append(cleaned)
            elif suffix in (".md", ".markdown"):
                tbls = extract_tables_from_markdown(path)
                for t in tbls:
                    cleaned = clean_dataframe(t, str(path.name))
                    collected.append(cleaned)
            else:
                logging.debug(f"skipping {path}")
        except Exception as e:
            logging.warning(f"failed processing {path}: {e}")
    return collected

def main():
    logging.info(f"Scanning {INPUT_DIR} ...")
    collected = process_folder(INPUT_DIR)
    if not collected:
        logging.info("Nessuna tabella trovata.")
        return
    unified = unify_tables(collected)
    # Ordina colonne: sposta _source_file ultima
    cols = [c for c in unified.columns if c != "_source_file"] + (["_source_file"] if "_source_file" in unified.columns else [])
    unified = unified.select(cols)
    # Scrivi CSV con polars -> veloce e robusto
    logging.info(f"Scrittura CSV in {OUTPUT_CSV} con {unified.height} righe e {len(unified.columns)} colonne.")
    unified.write_csv(str(OUTPUT_CSV))
    logging.info("Completato.")

if __name__ == "__main__":
    main()
