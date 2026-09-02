import re
import pandas as pd
from io import StringIO


def anonimizza_feedback(feedback_data):
    """
    Anonimizza una lista di feedback sostituendo dati personali con token pseudonimi.

    Fix applicati rispetto alla versione precedente:
    - I counter ora vengono incrementati DENTRO le closure (un token per ogni match,
      non uno per ogni feedback).
    - Mappe di consistenza: la stessa entità (nome, email, telefono) riceve sempre
      lo stesso token in tutti i feedback → pseudonimizzazione coerente (requisito GDPR).
    - Regex nomi resa più conservativa: esclude parole singole maiuscole per ridurre
      i falsi positivi su nomi di prodotti/marchi (es. AcmeCloud, Tel).
    """

    # --- Mappe di consistenza: entità → token ---
    # Garantiscono che la stessa stringa riceva sempre lo stesso ID
    nome_map: dict[str, str] = {}
    email_map: dict[str, str] = {}
    phone_map: dict[str, str] = {}

    customer_counter = [1]  # lista per mutabilità nelle closure
    email_counter = [1]
    phone_counter = [1]

    # --- Pattern ---
    # Richiede almeno due parole con iniziale maiuscola per ridurre falsi positivi
    # su nomi di prodotti o parole comuni maiuscole.
    nome_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b')
    email_pattern = re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b')
    telefono_pattern = re.compile(
        r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    )

    def sostituisci_nome(match):
        testo = match.group(0)
        if testo not in nome_map:
            nome_map[testo] = f"CUSTOMER_{customer_counter[0]:03d}"
            customer_counter[0] += 1
        return nome_map[testo]

    def sostituisci_email(match):
        testo = match.group(0)
        if testo not in email_map:
            email_map[testo] = f"EMAIL_{email_counter[0]:03d}@example.com"
            email_counter[0] += 1
        return email_map[testo]

    def sostituisci_telefono(match):
        testo = match.group(0)
        if testo not in phone_map:
            phone_map[testo] = f"PHONE_{phone_counter[0]:03d}"
            phone_counter[0] += 1
        return phone_map[testo]

    messaggi_elaborati = []
    for feedback in feedback_data:
        feedback_anon = nome_pattern.sub(sostituisci_nome, feedback)
        feedback_anon = email_pattern.sub(sostituisci_email, feedback_anon)
        feedback_anon = telefono_pattern.sub(sostituisci_telefono, feedback_anon)
        messaggi_elaborati.append(feedback_anon)

    return "\n---\n".join(messaggi_elaborati)


# --- Esempio di CSV di input ---
csv_esempio = """feedback
"Maria Rossi ha detto: 'AcmeCloud è fantastico, ma il supporto potrebbe essere più veloce.' Contatto: maria.rossi@example.com, Tel: +39 123 4567890"
"Luca Bianchi ha segnalato: 'Ho avuto problemi con AcmeSync, ma il team ha risolto tutto.' Contatto: luca.bianchi@example.com, Tel: 333 1234567"
"Feedback anonimo: 'Il prodotto AcmeDrive è eccellente, ma il prezzo è alto.'"
"Maria Rossi è tornata a scrivere: contatto maria.rossi@example.com"
"""

df = pd.read_csv(StringIO(csv_esempio))
feedback_data = df['feedback'].tolist()

risultato = anonimizza_feedback(feedback_data)
print(risultato)
