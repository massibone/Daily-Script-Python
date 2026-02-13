# Ransomware Traffic Anomaly Detector

**Script per il rilevamento di anomalie nel traffico di rete finalizzato all’identificazione di potenziali attacchi ransomware tramite machine learning e analisi comportamentale.**

----

##  Descrizione

Questo script analizza i log di traffico di rete (in formato CSV) per identificare:
- **Anomalie statistiche** (es. picchi anomali di traffico) tramite Z-Score.
- **Connessioni sospette** verso IP noti per attività ransomware.

L’obiettivo è fornire un primo livello di allerta per potenziali attacchi informatici, integrando tecniche di analisi comportamentale e liste di indicatori di compromissione (IoC).

---

##  Requisiti

- Python 3.8+
- Librerie richieste:
  ```bash
  pip install pandas numpy scipy
