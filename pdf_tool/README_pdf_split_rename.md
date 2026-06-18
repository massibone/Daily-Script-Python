# PDF Split Rename

Tool Python per dividere PDF multipagina in file singoli e rinominare l'output in batch con **PyMuPDF**.

## Cosa fa
- Legge tutti i PDF in una cartella.
- Divide ogni PDF in file da una pagina.
- Salva i file con un nome coerente e pulito.
- Evita conflitti di nome aggiungendo un suffisso progressivo quando serve.

## Caso d'uso
Utile per archivi documentali, back-office, pratiche amministrative o cartelle condivise dove serve separare velocemente PDF multipagina e ottenere file nominati in modo ordinato.

## Requisiti
```bash
pip install pymupdf
```

## Script consigliato
Se lo metti dentro `Daily-Script-Python/pdf_tool/`, il nome più chiaro è:

```text
split_rename_pdf.py
```
## Utilizzo
Esempio base:

```bash
python split_rename_pdf.py ./pdf_files
```

Con cartella di output personalizzata:

```bash
python split_rename_pdf.py ./pdf_files -o ./split_output
```

Con pattern personalizzato:

```bash
python split_rename_pdf.py ./pdf_files -o ./split_output -p "{stem}-p{page}-of-{total}"
```

## Placeholder disponibili
- `{stem}`: nome file sorgente in formato pulito
- `{original}`: nome file sorgente originale
- `{page}`: numero pagina
- `{total}`: numero totale pagine

## Output esempio
Da:

```text
fatture-marzo.pdf
```

Ottieni:

```text
fatture-marzo-page-1.pdf
fatture-marzo-page-2.pdf
fatture-marzo-page-3.pdf
