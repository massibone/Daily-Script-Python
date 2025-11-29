
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
ml_predictor.py 



    def __init__(self, task: str = 'classification', model_type: str = 'auto'):
        """
        Inizializza predictor.

        Args:
            task: 'classification' o 'regression'
            model_type: 'auto', 'random_forest', 'logistic', 'linear', 'ridge'
        """
        if task not in ['classification', 'regression']:
            raise ValueError("Task deve essere 'classification' o 'regression'")
        self.task = task
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.training_score = None

        self._initialize_model()

    def _initialize_model(self):
        """Inizializza modello ML"""
        try:
            # Importazioni locali per scikit-learn per gestire l'errore se non installato
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge

            if self.task == 'regression' and self.model_type in ['logistic']:
                 logger.warning(f"⚠️ Model type '{self.model_type}' non è ideale per la regressione. Utilizzo 'auto' (RandomForestRegressor).")
                 self.model_type = 'auto'

            if self.model_type in ['auto', 'random_forest']:
                if self.task == 'classification':
                    self.model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    self.model = RandomForestRegressor(n_estimators=100, random_state=42)

            elif self.model_type == 'logistic':
                # Max_iter aumentato per evitare problemi di convergenza
                self.model = LogisticRegression(max_iter=1000, random_state=42)

            elif self.model_type == 'linear':
                self.model = LinearRegression()

            elif self.model_type == 'ridge':
                # Aggiunto random_state per consistenza, anche se non sempre necessario per Ridge
                self.model = Ridge(alpha=1.0, random_state=42)

            else:
                 raise ValueError(f"Tipo di modello '{self.model_type}' non supportato.")

            logger.info(f"✅ Modello inizializzato: {self.model.__class__.__name__} per il task di {self.task}")

        except ImportError:
            logger.error("❌ La libreria scikit-learn non è installata. Esegui: pip install scikit-learn pandas numpy joblib")
            raise
        except ValueError as e:
            logger.error(f"❌ Errore di inizializzazione: {e}")
            raise

    def train(self, X: Union[pd.DataFrame, np.ndarray],
              y: Union[pd.Series, np.ndarray],
              feature_names: List[str] = None) -> 'MLPredictor':
        """
        Addestra il modello.

        Args:
            X: Features (matrice n_samples x n_features)
            y: Target (vettore n_samples)
            feature_names: Nomi features (opzionale)

        Returns:
            self (per method chaining)
        """
        if self.model is None:
            logger.error("❌ Modello non inizializzato.")
            raise AttributeError("Modello non inizializzato. Controlla _initialize_model.")

        try:
            # Gestione dei nomi delle feature
            if isinstance(X, pd.DataFrame):
                self.feature_names = X.columns.tolist()
                X_np = X.values
            elif feature_names:
                self.feature_names = feature_names
                X_np = X
            else:
                X_np = X

            if isinstance(y, pd.Series):
                y_np = y.values
            else:
                y_np = y

            # Verifica delle dimensioni
            if X_np.shape[0] != y_np.shape[0]:
                raise ValueError("Il numero di campioni in X e y non corrisponde.")

            # Training
            logger.info(f"🚀 Avvio addestramento su {X_np.shape[0]} campioni con {self.model.__class__.__name__}...")
            self.model.fit(X_np, y_np)

            # Score
            self.training_score = self.model.score(X_np, y_np)
            logger.info(f"✅ Addestramento completato. Training score: {self.training_score:.4f}")

            return self

        except Exception as e:
            logger.error(f"❌ Errore durante l'addestramento: {e}")
            raise

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Effettua predizioni.

        Args:
            X: Features

        Returns:
            Array di predizioni
        """
        if self.model is None or self.training_score is None:
            raise ValueError("Modello non addestrato. Richiama train() prima.")

        if isinstance(X, pd.DataFrame):
            X_np = X.values
        else:
            X_np = X

        predictions = self.model.predict(X_np)
        logger.info(f"✅ Generazione completata di {len(predictions)} predizioni.")
        return predictions

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Predici probabilità (solo classificazione).

        Returns:
            Array di probabilità
        """
        if self.task != 'classification':
            raise ValueError("Il metodo predict_proba è disponibile solo per i task di classificazione.")

        if not hasattr(self.model, 'predict_proba'):
             raise AttributeError(f"Il modello {self.model.__class__.__name__} non supporta predict_proba.")

        if isinstance(X, pd.DataFrame):
            X_np = X.values
        else:
            X_np = X

        return self.model.predict_proba(X_np)

    def evaluate(self, X: Union[pd.DataFrame, np.ndarray],
                 y: Union[pd.Series, np.ndarray]) -> Dict:
        """
        Valuta modello su test set.

        Returns:
            Dizionario con metriche
        """
        try:
            # Importazioni locali per metrics
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                mean_squared_error, r2_score, mean_absolute_error
            )

            if isinstance(X, pd.DataFrame):
                X_np = X.values
            else:
                X_np = X

            if isinstance(y, pd.Series):
                y_np = y.values
            else:
                y_np = y

            predictions = self.predict(X_np)

            if self.task == 'classification':
                metrics = {
                    'accuracy': accuracy_score(y_np, predictions),
                    # Uso di 'weighted' per bilanciare le classi
                    'precision': precision_score(y_np, predictions, average='weighted', zero_division=0),
                    'recall': recall_score(y_np, predictions, average='weighted', zero_division=0),
                    'f1_score': f1_score(y_np, predictions, average='weighted', zero_division=0)
                }
            else:  # regression
                mse = mean_squared_error(y_np, predictions)
                metrics = {
                    'mse': mse,
                    'rmse': np.sqrt(mse),
                    'mae': mean_absolute_error(y_np, predictions),
                    'r2_score': r2_score(y_np, predictions)
                }

            logger.info(f"✅ Metriche di valutazione: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"❌ Errore durante la valutazione: {e}")
            # Non rilanciare l'eccezione, ma restituisci un dizionario vuoto come fallback
            return {}

    def cross_validate(self, X: Union[pd.DataFrame, np.ndarray],
                       y: Union[pd.Series, np.ndarray],
                       cv: int = 5) -> Dict:
        """
        Cross-validation.

        Args:
            X: Features
            y: Target
            cv: Numero di fold

        Returns:
            Dizionario con score medi e std
        """
        if self.model is None:
            raise ValueError("Modello non inizializzato.")
        if cv < 2:
            raise ValueError("Il numero di fold (cv) deve essere almeno 2.")

        try:
            from sklearn.model_selection import cross_val_score

            if isinstance(X, pd.DataFrame):
                X_np = X.values
            else:
                X_np = X

            if isinstance(y, pd.Series):
                y_np = y.values
            else:
                y_np = y

            logger.info(f"🔄 Avvio Cross-Validation (CV={cv})...")
            scores = cross_val_score(self.model, X_np, y_np, cv=cv, n_jobs=-1) # n_jobs=-1 per parallelizzazione

            result = {
                'mean_score': scores.mean(),
                'std_score': scores.std(),
                'scores': scores.tolist()
            }

            logger.info(f"✅ CV Score Medio: {result['mean_score']:.4f} (+/- {result['std_score']:.4f})")
            return result

        except Exception as e:
            logger.error(f"❌ Errore durante la Cross-validation: {e}")
            return {}

    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """
        Ottieni feature importance (solo modelli basati su alberi o regressione lineare/ridge).

        Args:
            top_n: Numero top features da restituire

        Returns:
            DataFrame con feature e importance
        """
        importances = None
        
        # Random Forest supporta feature_importances_
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        # I modelli lineari supportano coef_
        elif hasattr(self.model, 'coef_'):
            # Usa il valore assoluto per misurare l'importanza
            importances = np.abs(self.model.coef_)
            if len(importances.shape) > 1: # Per LogisticRegression multi-classe
                importances = np.mean(importances, axis=0)
        else:
            logger.warning(f"⚠️ Il modello {self.model.__class__.__name__} non supporta il calcolo diretto dell'importanza delle feature (feature_importances_ o coef_).")
            return pd.DataFrame()
        
        if self.feature_names is None:
            logger.warning("⚠️ Nomi delle feature non disponibili. Assegno nomi generici.")
            feature_names = [f'feature_{i}' for i in range(len(importances))]
        else:
            feature_names = self.feature_names

        feature_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        })

        feature_df = feature_df.sort_values('importance', ascending=False).head(top_n).reset_index(drop=True)

        logger.info(f"✅ Top {top_n} feature più importanti:")
        for _, row in feature_df.iterrows():
            logger.info(f"   - {row['feature']}: {row['importance']:.4f}")

        return feature_df

    def save_model(self, filepath: str):
        """Salva modello e stato su disco usando joblib."""
        try:
            # Salvataggio di model, feature_names, task, training_score
            state = {
                'model': self.model,
                'feature_names': self.feature_names,
                'task': self.task,
                'training_score': self.training_score
            }
            joblib.dump(state, filepath)
            logger.info(f"💾 Modello e stato salvati in: {filepath}")
        except Exception as e:
            logger.error(f"❌ Errore durante il salvataggio del modello: {e}")
            raise

    @classmethod
    def load_model(cls, filepath: str) -> 'MLPredictor':
        """Carica modello e stato da disco."""
        try:
            state = joblib.load(filepath)
            
            # Creazione di una nuova istanza e assegnazione dello stato caricato
            # Si inizializza con i parametri del modello salvato se disponibili, altrimenti defaults
            predictor = cls(task=state.get('task', 'classification'), model_type='custom_loaded')
            
            predictor.model = state['model']
            predictor.feature_names = state.get('feature_names')
            predictor.task = state.get('task', predictor.task) # Sovrascrive task se presente
            predictor.training_score = state.get('training_score')
            
            logger.info(f"📥 Modello caricato da: {filepath}")
            return predictor
        except Exception as e:
            logger.error(f"❌ Errore durante il caricamento del modello: {e}")
            raise
