from sklearn.ensemble import IsolationForest
import numpy as np
import matplotlib.pyplot as plt

# Genera dati demo
X = np.random.randn(200, 2)
X[:10] += 10  # Aggiungi outlier

clf = IsolationForest(contamination=0.05, random_state=42)
labels = clf.fit_predict(X)

plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='coolwarm')
plt.title("Isolation Forest Anomaly Detection")
plt.show()
