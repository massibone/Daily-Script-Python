'''
================================================================================
📊 BASEBALL STATISTICS ANALYZER
================================================================================

DESCRIZIONE:
    Questo script analizza i dati antropometrici (altezza e peso) di giocatori
    di baseball usando NumPy. Calcola statistiche descrittive fondamentali e
    la correlazione tra le variabili.

A COSA SERVE:
    - Calcolare la media (average) dell'altezza dei giocatori
    - Calcolare la mediana (median) dell'altezza
    - Calcolare la deviazione standard (standard deviation) dell'altezza
    - Calcolare la correlazione tra altezza e peso

DATASET:
    np_baseball: Array NumPy 2D con:
    - Colonna 0: Altezza dei giocatori (in pollici)
    - Colonna 1: Peso dei giocatori (in libbre)

STATISTICHE CALCOLATE:
    
    1. MEDIA (Mean)
       - Valore medio dell'altezza
       - Somma di tutti i valori diviso il numero di osservazioni
       - Output: 73.69 pollici
    
    2. MEDIANA (Median)
       - Valore centrale quando i dati sono ordinati
       - Il 50% dei giocatori è più basso, il 50% più alto
       - Output: 74.0 pollici
    
    3. DEVIAZIONE STANDARD (Standard Deviation)
       - Misura di quanto i dati si disperso attorno alla media
       - Valori alti = dati molto variabili
       - Valori bassi = dati concentrati attorno alla media
       - Output: 2.31 pollici (variabilità moderata)
    
    4. CORRELAZIONE (Correlation)
       - Misura la relazione lineare tra due variabili
       - Valore tra -1 e +1
       - 0.53 = correlazione positiva moderata tra altezza e peso
       - (I giocatori più alti tendono ad essere più pesanti)

INTERPRETAZIONE DEI RISULTATI:
    
    ┌─────────────────────────────────────────────┐
    │ Average: 73.69 pollici                      │
    │ → L'altezza media è 73.69 pollici (187 cm) │
    ├─────────────────────────────────────────────┤
    │ Median: 74.0 pollici                        │
    │ → La media è molto vicina alla mediana      │
    │ → I dati sono distribuiti in modo simmetrico│
    ├─────────────────────────────────────────────┤
    │ Standard Deviation: 2.31 pollici            │
    │ → Il 68% dei giocatori è tra 71.38-75.99 in│
    │ → Il 95% è tra 69.07-78.30 pollici         │
    ├─────────────────────────────────────────────┤
    │ Correlation: 0.53                           │
    │ → Correlazione positiva moderata            │
    │ → Altezza e peso sono legati                │
    └─────────────────────────────────────────────┘

DIPENDENZE:
    - NumPy (import numpy as np)

AUTHOR: Data Analysis Team
VERSION: 1.0
================================================================================
'''

# Import numpy
import numpy as np


# Print mean height (first column)
avg = np.mean(np_baseball[:, 0])
print("Average: " + str(avg))


# Print median height
med = np.median(np_baseball[:, 0])
print("Median: " + str(med))


# Print out the standard deviation on height
stddev = np.std(np_baseball[:, 0])
print("Standard Deviation: " + str(stddev))


# Print out correlation between first and second column
corr = np.corrcoef(np_baseball[:, 0], np_baseball[:, 1])
print("Correlation: " + str(corr))

'''
================================================================================
OUTPUT RISULTATI
================================================================================

Average: 73.6896551724
    → La media dell'altezza è di 73.69 pollici (≈ 187 cm)

Median: 74.0
    → Il valore centrale è 74 pollici
    → Media e mediana sono molto vicine (distribuzione simmetrica)

Standard Deviation: 2.31279188105
    → La dispersione intorno alla media è di 2.31 pollici
    → Intervallo [71.38 - 75.99] contiene il 68% dei dati (±1σ)

Correlation: 
    [[ 1.          0.53153932]
     [ 0.53153932  1.        ]]
    
    Matrice di correlazione 2x2:
    ┌──────────────────────────────────┐
    │ Altezza-Altezza: 1.00  (perfetto)│
    │ Altezza-Peso:    0.53  (moderato)│
    │ Peso-Altezza:    0.53  (moderato)│
    │ Peso-Peso:       1.00  (perfetto)│
    └──────────────────────────────────┘
    
    Interpretazione: I giocatori più alti tendono ad essere più pesanti,
    ma la relazione non è perfetta (0.53 non è vicino a 1.0)

================================================================================
'''
