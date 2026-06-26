
# PDF/A Converter (PyMuPDF)
## Cos’è
Script Python che converte un PDF in **PDF/A-1, PDF/A-2 o PDF/A-3** usando **PyMuPDF**.
## Spiegazione
PDF “normale” (ISO: no)
Un PDF classico può essere creato in modi molto diversi e spesso fa affidamento sul fatto che il lettore abbia:
gli stessi font,
le stesse risorse esterne,
gli stessi riferimenti a colori/gestione colore,
rendering coerente nel tempo.
In pratica: oggi si vede bene, ma tra anni potrebbe non essere identico o riproducibile.
PDF/A (archiviazione a lungo termine)
PDF/A è una famiglia di standard pensata per archiviazione a lungo termine. Impone restrizioni tipo:
niente elementi “non affidabili” per il futuro (es. alcuni contenuti dinamici o riferimenti esterni non consentiti),
self-contained: le risorse necessarie devono essere dentro o in modo gestibile,
gestione colore più rigorosa (conversioni e profili ICC appropriati),
requisiti su metadati/struttura per rendere la resa più stabile.
Risultato: un PDF/A dovrebbe essere più “riproducibile” nel tempo rispetto a un PDF qualunque.
PDF/A-1, PDF/A-2, PDF/A-3: differenze principali
Le versioni aumentano la capacità/compatibilità, mantenendo l’obiettivo di archiviazione.
PDF/A-1
È la base “più restrittiva” e storicamente più comune.
Non include alcune funzionalità moderne come nei livelli successivi (in particolare su formati di contenuto incorporato “rende” più complessi).
In genere è il livello più “sicuro” per conformità, ma può essere più limitante.
PDF/A-2
Aggiunge soprattutto miglioramenti per la gestione colore e per l’affidabilità della stampa/riproduzione.
È spesso scelto quando serve una resa colore più robusta rispetto a PDF/A-1, rimanendo comunque per archiviazione.
PDF/A-3
È pensato per aggiungere la possibilità di archiviare anche file o contenuti “extramedia” (es. documenti XML, allegati, ecc.) oltre al “solo” contenuto PDF, mantenendo la parte PDF principale conforme.
Quindi: più flessibile per archiviare documenti con allegati “interni”, pur restando PDF/A.
Cosa significa (1/2/3)
Se vuoi massima compatibilità e “semplicità” di conformità: PDF/A-1.
Se la priorità è la resa colore più affidabile: spesso PDF/A-2.
Se devi archiviare anche allegati/extra contenuti dentro al file: PDF/A-3.

## Requisiti
- Python 3.x
- `pymupdf`
Installa dipendenze:

pip install pymupdf
## Uso

python pdfa\_convert.py input.pdf output.pdfa [1|2|3]
Se ometti [1|2|3], usa PDF/A-1.
level accetta solo:
1 → PDF/A-1
2 → PDF/A-2
3 → PDF/A-3

## Esempi

python pdfa\_convert.py input.pdf output\_pa1.pdf 1
python pdfa\_convert.py input.pdf output\_pa2.pdf 2
python pdfa\_convert.py input.pdf output\_pa3.pdf 3

