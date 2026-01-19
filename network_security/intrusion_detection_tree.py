# Decision Tree per rilevare intrusioni di rete
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# Carica il dataset
data = pd.read_csv('intrusioni_rete.csv')

# Controlla che le colonne esistano
required_columns = ['src_ip', 'dst_ip', 'protocollo', 'intrusione']
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"Colonna mancante nel dataset: {col}")

# Seleziona le feature e la variabile target
X = data[['src_ip', 'dst_ip', 'protocollo']]
y = data['intrusione']

# Codifica le variabili categoriche (IP e protocollo) in numerico
X_encoded = pd.get_dummies(X, columns=['src_ip', 'dst_ip', 'protocollo'])

# Dividi il dataset in training e test set
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)

# Crea e addestra il modello Decision Tree
dt = DecisionTreeClassifier(max_depth=5, random_state=42)
dt.fit(X_train, y_train)

# Predici i valori per i dati di test
y_pred = dt.predict(X_test)

# Calcola l'accuracy e mostra un report più completo
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
print("\nClassification Report:\n", classification_report(y_test, y_pred))



