import pandas as pd

def genera_report_vendite(file_path, output_excel="report_vendite.xlsx"):
    df = pd.read_csv(file_path)
    report = df.groupby("Prodotto").agg({"Quantità": "sum", "Prezzo": "sum"}).reset_index()
    report.to_excel(output_excel, index=False)
    print(f"Report generato: {output_excel}")

# Esempio di utilizzo
file_csv = "vendite.csv"
genera_report_vendite(file_csv)
