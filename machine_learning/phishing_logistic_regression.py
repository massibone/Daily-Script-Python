phishing_logistic_regression.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Carica il dataset
# Assicurati che 'phishing.csv' sia nella stessa cartella dello script
data = pd.read_csv('phishing.csv')

# Controlla che le colonne esistano
required_columns = ['lunghezza_URL', 'presenza_keyword', 'phishing']
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"Colonna mancante nel dataset: {col}")

# Seleziona le feature e la variabile target
X = data[['lunghezza_URL', 'presenza_keyword']]
y = data['phishing']

# Dividi il dataset in training e test set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Crea e addestra il modello di regressione logistica
logreg = LogisticRegression(max_iter=1000)
logreg.fit(X_train, y_train)

# Predici i valori per i dati di test
y_pred = logreg.predict(X_test)

# Calcola l'accuracy e mostra un report più completo
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
print("\nClassification Report:\n", classification_report(y_test, y_pred))

