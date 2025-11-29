
import pandas as pd
import numpy as np
import logging
import joblib
from typing import Union, List, Dict

# Configurazione del logger
# Un buon logging è fondamentale per gli script da eseguire quotidianamente
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Configura un handler per stampare su console
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class MLPredictor:
    """
    Snippet modulare per ML base con scikit-learn.

    Features:
    - Classificazione (Random Forest, Logistic Regression)
    - Regressione (Linear, Ridge)
    - Valutazione modelli
    - Cross-validation
    - Feature importance

    Example:

    >>> # Esempio di utilizzo (necessita dati X_train, y_train, ecc.)
    >>> # predictor = MLPredictor(task='classification')
    >>> # predictor.train(X_train, y_train)
    >>> # predictions = predictor.predict(X_test)
    >>> # metrics = predictor.evaluate(X_test, y_test)
    """
