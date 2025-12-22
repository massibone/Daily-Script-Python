“Script per rilevamento anomalie nel traffico di rete, finalizzato all’identificazione di potenziali attacchi ransomware mediante machine learning e analisi comportamentale.” 
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Esempio di funzione per caricare e analizzare log di traffico (CSV)
def load_traffic_data(filepath):
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Errore nel caricamento del file: {e}")
        return None

# Funzione per rilevare anomalie usando Z-Score
def detect_anomalies_zscore(data, column, threshold=3):
    z_scores = np.abs(stats.zscore(data[column]))
    anomalies = data[z_scores > threshold]
    return anomalies

