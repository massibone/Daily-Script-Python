Clustering Hierarchico su un dataset di log di sistema

import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt


# Carica il dataset
data = pd.read_csv('log_sistema.csv')


# Seleziona le colonne di interesse
X = data[['timestamp', 'evento']]


# Crea un oggetto AgglomerativeClustering
cluster = AgglomerativeClustering(n_clusters=5)


# Addestra il modello sui dati
cluster.fit(X)


# Visualizza i cluster
plt.scatter(X['timestamp'], X['evento'], c=cluster.labels_)
plt.show()


In questo esempio, il dataset contiene informazioni sui log di sistema, tra cui timestamp e tipo di evento. Il modello di clustering hierarchico viene utilizzato per raggruppare gli eventi in 5 cluster in base alle loro caratteristiche.
Esempio 5: SVM su un dataset di malware
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


# Carica il dataset
data = pd.read_csv('malware.csv')


# Seleziona le colonne di interesse
X = data[['lunghezza_file', 'numero_sezioni']]
y = data['malware']


# Dividi il dataset in training e test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Crea un oggetto SVC
svm = SVC()


# Addestra il modello sui dati di training
svm.fit(X_train, y_train)


# Predici i valori per i dati di test
y_pred = svm.predict(X_test)


# Calcola l'accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)


