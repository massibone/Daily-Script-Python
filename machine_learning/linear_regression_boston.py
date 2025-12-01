# linear_regression_boston.py

# Import librerie
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Carica dataset
boston = fetch_openml(name='boston', version=1, as_frame=True)
X, y = boston.data, boston.target

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crea e addestra il modello
model = LinearRegression()
model.fit(X_train, y_train)

# Predizioni e valutazione
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse:.2f}")

