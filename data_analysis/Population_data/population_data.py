"""
population_data.py

Modulo semplice per accedere ai dati di popolazione.
"""

class PopulationData:
    """Gestisce i dati di popolazione."""
    
    def __init__(self, years, populations):
        """
        Inizializza con liste di anni e popolazioni.
        
        Args:
            years: Lista degli anni
            populations: Lista delle popolazioni
        """
        self.years = years
        self.populations = populations
    
    def get_population(self, year):
        """
        Ottiene la popolazione per un anno specifico.
        
        Args:
            year: L'anno di interesse
            
        Returns:
            float: La popolazione nell'anno
            
        Example:
            >>> data = PopulationData([2041, 2062], [9.09, 10.03])
            >>> data.get_population(2041)
            9.09
        """
        try:
            index = self.years.index(year)
            return self.populations[index]
        except ValueError:
            return f"Anno {year} non trovato"
    
    def get_growth_rate(self, year1, year2):
        """
        Calcola il tasso di crescita tra due anni.
        
        Args:
            year1: Anno di inizio
            year2: Anno di fine
            
        Returns:
            float: Tasso di crescita percentuale
        """
        pop1 = self.get_population(year1)
        pop2 = self.get_population(year2)
        
        growth = ((pop2 - pop1) / pop1) * 100
        return round(growth, 2)


# Esempio di utilizzo
if __name__ == "__main__":
    # Creare i dati
    data = PopulationData(
        years=[2020, 2030, 2041, 2050, 2062, 2070],
        populations=[7.5, 8.5, 9.09, 9.5, 10.03, 10.8]
    )
    
    # Usare la classe
    print(data.get_population(2041))        # 9.09
    print(data.get_population(2062))        # 10.03
    print(data.get_growth_rate(2041, 2062)) # 10.33
