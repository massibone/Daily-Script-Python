
# Classe Python modulare per caricare e processare dati CSV
class CSVProcessor:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_data(self):
        import pandas as pd
        self.data = pd.read_csv(self.filepath)
        return self.data

    def clean_data(self):
        self.data.dropna(inplace=True)
        return self.data

    def summary(self):
        return self.data.describe() 

