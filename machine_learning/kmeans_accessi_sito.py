import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def preprocess_data(df):
    """
    Converte le colonne date/ora in numeri per K-Means
    """
    # Converte la data in timestamp numerico
    df['data_accesso'] = pd.to_datetime(df['data_accesso'], errors='coerce')
    df['data_num'] = df['data_accesso'].map(pd.Timestamp.timestamp)

    # Converte ora in minuti dall'inizio della giornata
    df['ora_accesso'] = pd.to_datetime(df['ora_accesso'], format='%H:%M', errors='coerce')
    df['ora_minuti'] = df['ora_accesso'].dt.hour * 60 + df['ora_accesso'].dt.minute

    # Manteniamo solo le colonne numeriche per K-Means
    X = df[['data_num', 'ora_minuti']].dropna()
    return X, df

def main():
    # Carica il dataset
    df = pd.read_csv('accessi_sito_web.csv')

    # Preprocessa i dati
    X, df_clean = preprocess_data(df)

    # Crea e addestra il modello K-Means
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(X)

    # Assegna i cluster
    df_clean['cluster'] = kmeans.predict(X)

    # Visualizza i cluster
    plt.figure(figsize=(8,6))
    plt.scatter(X['data_num'], X['ora_minuti'], c=df_clean['cluster'], cmap='viridis')
    plt.xlabel('Data (timestamp)')
    plt.ylabel('Ora (minuti)')
    plt.title('Clustering K-Means Accessi Sito Web')
    plt.show()

if __name__ == "__main__":
    main()

