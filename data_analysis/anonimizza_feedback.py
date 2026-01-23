import re
import pandas as pd
from io import StringIO

def anonimizza_feedback(feedback_data):
    # Inizializza gli ID per clienti, email e telefoni
    customer_id = 1
    email_id = 1
    phone_id = 1

    # Espressioni regolari per identificare nomi, email e telefoni
    nome_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b')
    email_pattern = re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b')
    telefono_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

    messaggi_elaborati = []

    for feedback in feedback_data:
        # Sostituisci i nomi
        def sostituisci_nome(match):
            nonlocal customer_id
            return f"CUSTOMER_{customer_id:03d}"

        feedback_anon = nome_pattern.sub(sostituisci_nome, feedback)
        customer_id += 1

        # Sostituisci le email
        def sostituisci_email(match):
            nonlocal email_id
            return f"EMAIL_{email_id:03d}@example.com"

        feedback_anon = email_pattern.sub(sostituisci_email, feedback_anon)
        email_id += 1

        # Sostituisci i telefoni
        def sostituisci_telefono(match):
            nonlocal phone_id
            return f"PHONE_{phone_id:03d}"

        feedback_anon = telefono_pattern.sub(sostituisci_telefono, feedback_anon)
        phone_id += 1

        messaggi_elaborati.append(feedback_anon)

    return "\n---\n".join(messaggi_elaborati)

# Esempio di CSV di input
csv_esempio = """feedback
"Maria Rossi ha detto: 'AcmeCloud è fantastico, ma il supporto potrebbe essere più veloce.' Contatto: maria.rossi@example.com, Tel: +39 123 4567890"
"Luca Bianchi ha segnalato: 'Ho avuto problemi con AcmeSync, ma il team ha risolto tutto.' Contatto: luca.bianchi@example.com, Tel: 333 1234567"
"Feedback anonimo: 'Il prodotto AcmeDrive è eccellente, ma il prezzo è alto.'"
"""

# Leggi il CSV di esempio
df = pd.read_csv(StringIO(csv_esempio))

# Estrai i feedback
feedback_data = df['feedback'].tolist()

# Elabora i feedback
messaggi_elaborati = anonimizza_feedback(feedback_data)

print(messaggi_elaborati)
