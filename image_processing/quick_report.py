#Analizza CSV foto (dimensioni, date), genera summary HTML. 

"""Genera report HTML da CSV foto con Pandas."""
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import plotly.express as px
import plotly.io as pio

def analyze_csv(csv_path: Path) -> Dict[str, Any]:
    """Analizza CSV foto: stats dimensioni, date, duplicati."""
    df = pd.read_csv(csv_path)
    return {
        'total_files': len(df),
        'duplicates': df.duplicated().sum(),
        'size_gb': df['size_mb'].sum() / 1024,
        'date_range': f"{df['date'].min()} → {df['date'].max()}"
    }

def generate_html_report(stats: Dict[str, Any], output: Path):
    """Salva stats come HTML interattivo."""
    fig = px.bar(x=list(stats.keys()), y=list(stats.values()))
    pio.write_html(fig, output)

if __name__ == "__main__":
    stats = analyze_csv(Path("foto_inventory.csv"))
    generate_html_report(stats, Path("report.html"))
    print(stats)

