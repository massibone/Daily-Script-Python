

### 1. `anonimizza_feedback.py`
**Descrizione:**
Anonimizza i feedback dei clienti sostituendo nomi, email e numeri di telefono con identificatori generici (es. `CUSTOMER_001`, `EMAIL_001@example.com`, `PHONE_001`). I nomi dei prodotti vengono lasciati intatti.

**Formato Input:**
- Un file CSV con una colonna `feedback` contenente i messaggi da elaborare.

**Formato Output:**
- I messaggi anonimizzati, separati da `---`.

**Esempio di Input (`feedback_esempio.csv`):**
```csv
feedback
"Maria Rossi ha detto: 'AcmeCloud è fantastico, ma il supporto potrebbe essere più veloce.' Contatto: maria.rossi@example.com, Tel: +39 123 4567890"
"Luca Bianchi ha segnalato: 'Ho avuto problemi con AcmeSync, ma il team ha risolto tutto.' Contatto: luca.bianchi@example.com, Tel: 333 1234567"
"Feedback anonimo: 'Il prodotto AcmeDrive è eccellente, ma il prezzo è alto.'"

Istruzioni per l'uso
Modifica i parametri nei blocchi if __name__ == "__main__"::
file_input: il percorso del tuo file di log.
formato_input: "testo", "csv", o "json".
data_inizio e data_fine: per il filtro per data.
ip_list: per il filtro per IP.
