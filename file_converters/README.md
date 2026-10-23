# 🔄 Base64 File Converter

Convertitore bidirezionale Base64 ↔ File con GUI e CLI.


## 🎯 Caratteristiche

- ✅ Converti Base64 in PDF, JPEG, PNG, GIF
- ✅ Converti file in Base64
- ✅ Auto-rilevamento tipo file
- ✅ Supporto JSON (compatibile Postman)
- ✅ GUI intuitiva (tkinter)
- ✅ CLI potente
- ✅ Validazione e logging completi

## 📦 Installazione
```bash
# Nessuna dipendenza esterna!
# Solo Python 3.7+ standard library
```

## 🚀 Uso Rapido

### GUI (Interfaccia Grafica)
```bash
python base64_converter.py --gui
```

### CLI Esempi
```bash
# Base64 → PDF
python base64_converter.py input.txt output.pdf

# File → Base64
python base64_converter.py --encode documento.pdf base64.txt

# JSON Postman → PDF
python base64_converter.py --json risposta.json --key "documento" --output doc.pdf

# Con metadati JSON
python base64_converter.py --encode foto.jpg --include-json output.json
```

### Come Libreria
```python
from base64_converter import Base64Converter

converter = Base64Converter()
converter.decode_from_file("input.txt", "output.pdf")
```

## 📄 Formato JSON Postman
```json
{
  "documento": "JVBERi0xLjQKJeLjz9MKMSAwIG9iag...",
  "tipo": "pdf",
  "nome": "fattura.pdf"
}
```

## 📝 Formati Supportati

| Formato | Estensione | MIME Type |
|---------|------------|-----------|
| PDF | .pdf | application/pdf |
| JPEG | .jpg, .jpeg | image/jpeg |
| PNG | .png | image/png |
| GIF | .gif | image/gif |
| ZIP | .zip | application/zip |

## 🔍 Auto-Rilevamento

Il programma riconosce automaticamente il tipo di file analizzando i "magic numbers" del Base64:
- `JVBERi0` → PDF
- `/9j/` → JPEG
- `iVBORw0KGgo` → PNG
- `R0lGOD` → GIF

## 📊 Logging

Tutte le operazioni vengono registrate in `converter.log`
