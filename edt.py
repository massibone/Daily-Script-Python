import requests

import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime
import re

class DataETL:
    """
    Snippet modulare per ETL (Extract, Transform, Load).
    
    Features:
    - Pulizia dati automatica
    - Gestione valori mancanti
    - Normalizzazione
    - Aggregazioni
    - Export multipli formati
    
    Example:
        >>> etl = DataETL()
        >>> df_clean = etl.clean_data(df)
        >>> df_normalized = etl.normalize_columns(df_clean, ['age', 'salary'])
        >>> etl.save_data(df_normalized, 'output.csv')
    """
    
    def __init__(self):
        self.stats = {'operations': 0, 'rows_processed': 0}
    
    def load_data(self, file_path: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        Carica dati da file (CSV, Excel, JSON).
        
        Args:
            file_path: Percorso file
            **kwargs: Parametri aggiuntivi per pandas read_*
        
        Returns:
            DataFrame o None
        """
        try:
            file_path = Path(file_path)
            
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path, **kwargs)
            elif file_path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, **kwargs)
            elif file_path.suffix == '.json':
                df = pd.read_json(file_path, **kwargs)
            elif file_path.suffix == '.parquet':
                df = pd.read_parquet(file_path, **kwargs)
            else:
                logger.error(f"Unsupported format: {file_path.suffix}")
                return None
            
            logger.info(f"✅ Loaded {len(df)} rows from {file_path.name}")
            self.stats['rows_processed'] += len(df)
            return df
            
        except Exception as e:
            logger.error(f"❌ Load error: {e}")
            return None
    
    def clean_data(self, df: pd.DataFrame, 
                   drop_duplicates: bool = True,
                   drop_empty_rows: bool = True,
                   strip_whitespace: bool = True) -> pd.DataFrame:
        """
        Pulizia base del DataFrame.
        
        Args:
            df: DataFrame da pulire
            drop_duplicates: Rimuovi righe duplicate
            drop_empty_rows: Rimuovi righe completamente vuote
            strip_whitespace: Rimuovi spazi da stringhe
        
        Returns:
            DataFrame pulito
        """
        df_clean = df.copy()
        original_rows = len(df_clean)
        
        # Rimuovi duplicati
        if drop_duplicates:
            df_clean = df_clean.drop_duplicates()
            logger.info(f"Removed {original_rows - len(df_clean)} duplicates")
        
        # Rimuovi righe completamente vuote
        if drop_empty_rows:
            df_clean = df_clean.dropna(how='all')
            logger.info(f"Removed {original_rows - len(df_clean)} empty rows")
        
        # Strip whitespace da colonne stringa
        if strip_whitespace:
            string_cols = df_clean.select_dtypes(include=['object']).columns
            for col in string_cols:
                df_clean[col] = df_clean[col].str.strip() if df_clean[col].dtype == 'object' else df_clean[col]
        
        self.stats['operations'] += 1
        logger.info(f"✅ Cleaned: {original_rows} → {len(df_clean)} rows")
        return df_clean
    
    def handle_missing(self, df: pd.DataFrame, 
                      strategy: str = 'mean',
                      columns: List[str] = None) -> pd.DataFrame:
        """
        Gestisce valori mancanti.
        
        Args:
            df: DataFrame
            strategy: 'mean', 'median', 'mode', 'drop', 'ffill', 'bfill'
            columns: Colonne specifiche (None = tutte numeriche)
        
        Returns:
            DataFrame con valori mancanti gestiti
        """
        df_filled = df.copy()
        
        if columns is None:
            columns = df_filled.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            missing_count = df_filled[col].isna().sum()
            if missing_count > 0:
                if strategy == 'mean':
                    df_filled[col].fillna(df_filled[col].mean(), inplace=True)
                elif strategy == 'median':
                    df_filled[col].fillna(df_filled[col].median(), inplace=True)
                elif strategy == 'mode':
                    df_filled[col].fillna(df_filled[col].mode()[0], inplace=True)
                elif strategy == 'drop':
                    df_filled = df_filled.dropna(subset=[col])
                elif strategy == 'ffill':
                    df_filled[col].fillna(method='ffill', inplace=True)
                elif strategy == 'bfill':
                    df_filled[col].fillna(method='bfill', inplace=True)
                
                logger.info(f"Filled {missing_count} missing values in {col} using {strategy}")
        
        self.stats['operations'] += 1
        return df_filled
    
    def normalize_columns(self, df: pd.DataFrame, 
                         columns: List[str],
                         method: str = 'minmax') -> pd.DataFrame:
        """
        Normalizza colonne numeriche.
        
        Args:
            df: DataFrame
            columns: Colonne da normalizzare
            method: 'minmax' (0-1) o 'zscore' (standardizzazione)
        
        Returns:
            DataFrame normalizzato
        """
        df_norm = df.copy()
        
        for col in columns:
            if col not in df_norm.columns:
                logger.warning(f"Column {col} not found")
                continue
            
            if method == 'minmax':
                # Min-Max scaling (0-1)
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            
            elif method == 'zscore':
                # Z-score standardization
                mean = df_norm[col].mean()
                std = df_norm[col].std()
                df_norm[col] = (df_norm[col] - mean) / std
            
            logger.info(f"Normalized {col} using {method}")
        
        self.stats['operations'] += 1
        return df_norm
    
    def aggregate_data(self, df: pd.DataFrame,
                      group_by: Union[str, List[str]],
                      agg_dict: Dict[str, Union[str, List[str]]]) -> pd.DataFrame:
        """
        Aggrega dati con groupby.
        
        Args:
            df: DataFrame
            group_by: Colonna/e per raggruppamento
            agg_dict: Dizionario {colonna: funzione_aggregazione}
        
        Returns:
            DataFrame aggregato
        
        Example:
            >>> agg = etl.aggregate_data(df, 'category', 
            ...     {'price': ['mean', 'sum'], 'quantity': 'count'})
        """
        try:
            df_agg = df.groupby(group_by).agg(agg_dict).reset_index()
            logger.info(f"✅ Aggregated to {len(df_agg)} groups")
            self.stats['operations'] += 1
            return df_agg
        except Exception as e:
            logger.error(f"❌ Aggregation error: {e}")
            return df
    
    def pivot_table(self, df: pd.DataFrame,
                   index: str,
                   columns: str,
                   values: str,
                   aggfunc: str = 'mean') -> pd.DataFrame:
        """
        Crea tabella pivot.
        
        Example:
            >>> pivot = etl.pivot_table(df, 
            ...     index='date', columns='product', values='sales')
        """
        try:
            pivot = pd.pivot_table(df, 
                                  index=index, 
                                  columns=columns, 
                                  values=values, 
                                  aggfunc=aggfunc)
            logger.info(f"✅ Created pivot table: {pivot.shape}")
            return pivot
        except Exception as e:
            logger.error(f"❌ Pivot error: {e}")
            return df
    
    def save_data(self, df: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        Salva DataFrame in vari formati.
        
        Args:
            df: DataFrame da salvare
            output_path: Percorso output
            **kwargs: Parametri per to_*
        
        Returns:
            bool: True se salvato con successo
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if output_file.suffix == '.csv':
                df.to_csv(output_file, index=False, **kwargs)
            elif output_file.suffix in ['.xlsx', '.xls']:
                df.to_excel(output_file, index=False, **kwargs)
            elif output_file.suffix == '.json':
                df.to_json(output_file, **kwargs)
            elif output_file.suffix == '.parquet':
                df.to_parquet(output_file, **kwargs)
            else:
                logger.error(f"Unsupported format: {output_file.suffix}")
                return False
            
            logger.info(f"✅ Saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Save error: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Ottieni statistiche operazioni"""
        return self.stats.copy()


class NumPyETL:
    """
    Snippet ETL con NumPy per operazioni numeriche veloci.
    
    Example:
        >>> etl = NumPyETL()
        >>> normalized = etl.normalize_array(data)
        >>> outliers = etl.detect_outliers(data)
    """
    
    @staticmethod
    def normalize_array(arr: np.ndarray, method: str = 'minmax') -> np.ndarray:
        """Normalizza array NumPy"""
        if method == 'minmax':
            return (arr - arr.min()) / (arr.max() - arr.min())
        elif method == 'zscore':
            return (arr - arr.mean()) / arr.std()
        return arr
    
    @staticmethod
    def detect_outliers(arr: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Rileva outlier usando z-score.
        
        Returns:
            Boolean array (True = outlier)
        """
        z_scores = np.abs((arr - arr.mean()) / arr.std())
        return z_scores > threshold
    
    @staticmethod
    def moving_average(arr: np.ndarray, window: int) -> np.ndarray:
        """Calcola media mobile"""
        return np.convolve(arr, np.ones(window)/window, mode='valid')
    
    @staticmethod
    def correlation_matrix(data: np.ndarray) -> np.ndarray:
        """Calcola matrice di correlazione"""
        return np.corrcoef(data.T)
