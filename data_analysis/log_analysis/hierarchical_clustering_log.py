import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import numpy as np

# Funzione per generare dati di log di sistema di esempio
def generate_sample_log_data(num_samples=100):
    timestamps = pd.to_datetime(np.random.randint(1672531200, 1704067200, num_samples), unit='s') # Dal 2023 al 2024
    events = np.random.choice(['login_success', 'login_failed', 'file_access', 'system_error', 'network_activity'], num_samples)
    
    # Converti timestamp in un formato numerico per il clustering (es. timestamp Unix)
    numeric_timestamps = timestamps.astype(int) // 10**9
    
    # Codifica gli eventi in formato numerico (One-Hot Encoding o Label Encoding)
    # Per semplicità, useremo Label Encoding qui, ma One-Hot sarebbe più robusto per eventi categorici
    event_mapping = {event: i for i, event in enumerate(np.unique(events))}
    numeric_events = np.array([event_mapping[event] for event in events])
    
    return pd.DataFrame({'timestamp': numeric_timestamps, 'evento': numeric_events, 'original_event': events})

# Carica il dataset o genera dati di esempio se il file non esiste
try:
    data = pd.read_csv('log_sistema.csv')
    # Assicurati che le colonne siano numeriche per il clustering
    # Se 'timestamp' è una stringa, convertila in numerico (es. Unix timestamp)
    if pd.api.types.is_string_dtype(data['timestamp']):
        data['timestamp'] = pd.to_datetime(data['timestamp']).astype(int) // 10**9
    # Se 'evento' è una stringa, convertila in numerico
    if pd.api.types.is_string_dtype(data['evento']):
        event_mapping = {event: i for i, event in enumerate(data['evento'].unique())}
        data['evento'] = data['evento'].map(event_mapping)
except FileNotFoundError:
    print("File 'log_sistema.csv' non trovato. Generazione di dati di esempio...")
    data = generate_sample_log_data()

# Seleziona le colonne di interesse per il clustering
X = data[['timestamp', 'evento']]

# Crea un oggetto AgglomerativeClustering
# n_clusters può essere determinato con metodi come il dendrogramma o il coefficiente di silhouette
# Per questo esempio, lo impostiamo a 5 come richiesto nell'esempio originale
cluster = AgglomerativeClustering(n_clusters=5, metric='euclidean', linkage='ward')

# Addestra il modello sui dati
cluster.fit(X)

# Aggiungi le etichette dei cluster al DataFrame originale
data['cluster_label'] = cluster.labels_

# Visualizza i cluster
plt.figure(figsize=(10, 7))
scatter = plt.scatter(data['timestamp'], data['evento'], c=data['cluster_label'], cmap='viridis', s=50, alpha=0.7)
plt.title('Clustering Gerarchico dei Log di Sistema')
plt.xlabel('Timestamp (numerico)')
plt.ylabel('Evento (codificato numericamente)')
plt.colorbar(scatter, label='Etichetta Cluster')

# Aggiungi una legenda per gli eventi originali se sono stati generati
if 'original_event' in data.columns:
    # Questo è un po' più complesso per una legenda pulita con scatter, ma possiamo mostrare i punti colorati
    # Alternativa: creare un mapping inverso per la colorbar se gli eventi sono pochi
    pass # Per ora, la colorbar mostra solo le etichette numeriche dei cluster

plt.grid(True)
plt.show()

print("Clustering gerarchico completato. I cluster sono stati visualizzati.")
print("Prime 5 righe del dataset con le etichette dei cluster:")
print(data.head())
