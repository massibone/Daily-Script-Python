 '''
L'obiettivo è esportare dei dati in diversi formati (PDF, CSV, JSON, XML, ecc.) a seconda della richiesta. 
'''
def export_data(data, format):
    if format == 'PDF':
        export_PDF(data)
    elif format == 'CSV':
        export_CSV(data)
    elif format == 'JSON':
        export_JSON(data)
    # E così via...
#esempio con registro

exporters = {
    'PDF': export_PDF,
    'CSV': export_CSV,
    'JSON': export_JSON
# qui puoi agg xml
}

def export_data(data, format):
    # Recupera la funzione dal Registro
    exporter = exporters.get(format) 
    if exporter:
        # Chiama dinamicamente la funzione
        exporter(data) 
    else:
        raise ValueError("Formato non supportato")
