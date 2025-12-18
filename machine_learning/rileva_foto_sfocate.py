# Rileva foto "anomalie" (es. sfocate) da metadata (ISO/shutter troppo estremi). 

"""Rileva outlier foto da EXIF con Isolation Forest."""

from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
from typing import List, Tuple

def detect_photo_outliers(csv_path: Path) -> List[Tuple[str, float]]:
    """Trova foto outlier su ISO/shutter speed."""
    df = pd.read_csv(csv_path)[['iso', 'shutter_speed']]
    df_numeric = df.select_dtypes(include=[np.number]).fillna(0)
    
    model = IsolationForest(contamination=0.1, random_state=42)
    anomalies = model.fit_predict(df_numeric)
    
    return [(row['filename'], score) 
            for idx, row in df.iterrows() 
            if anomalies[idx] == -1]

if __name__ == "__main__":
    outliers = detect_photo_outliers(Path("exif_data.csv"))
    print(f"Trovate {len(outliers)} foto anomale:", outliers[:5])

