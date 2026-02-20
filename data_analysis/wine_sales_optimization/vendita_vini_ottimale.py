"""
Ordine ottimale di vendita.

Include:
- Calcolo del profitto massimo
- Ricostruzione dell'ordine di vendita ottimale
- Visualizzazione dettagliata dei passaggi

Complessità:
- Temporale: O(N²)
- Spaziale: O(N²)
"""

from typing import List, Tuple


class WineSalesOptimizer:
    """Classe per risolvere il problema della vendita dei vini."""
    
    def __init__(self, prices: List[int]):
        """
        Inizializza l'ottimizzatore.
        
        Args:
            prices: Lista dei prezzi iniziali dei vini
        """
        self.prices = prices
        self.N = len(prices)
        self.cache = [[-1] * self.N for _ in range(self.N)]
        self.choices = [[None] * self.N for _ in range(self.N)]
    
    def calculate_max_profit(self) -> int:
        """
        Calcola il profitto massimo e riempie la cache.
        
        Returns:
            Profitto massimo ottenibile
        """
        return self._profit(0, self.N - 1, 1)
    
    def _profit(self, left: int, right: int, year: int) -> int:
        """
        Calcola il profitto massimo ricorsivamente.
        
        Args:
            left: Indice del vino più a sinistra
            right: Indice del vino più a destra
            year: Anno corrente
            
        Returns:
            Profitto massimo per questa configurazione
        """
        if left > right:
            return 0
        
        if self.cache[left][right] != -1:
            return self.cache[left][right]
        
        # Profitto se vendiamo a sinistra
        profit_left = (
            year * self.prices[left] + 
            self._profit(left + 1, right, year + 1)
        )
        
        # Profitto se vendiamo a destra
        profit_right = (
            year * self.prices[right] + 
            self._profit(left, right - 1, year + 1)
        )
        
        # Salva la scelta migliore
        if profit_left >= profit_right:
            self.choices[left][right] = 'LEFT'
            self.cache[left][right] = profit_left
        else:
            self.choices[left][right] = 'RIGHT'
            self.cache[left][right] = profit_right
        
        return self.cache[left][right]
    
    def get_optimal_order(self) -> List[Tuple[int, str, int, int]]:
        """
        Ricostruisce l'ordine ottimale di vendita.
        
        Returns:
            Lista di tuple (anno, posizione, prezzo_iniziale, guadagno)
        """
        order = []
        left, right = 0, self.N - 1
        
        for year in range(1, self.N + 1):
            if left > right:
                break
            
            if self.choices[left][right] == 'LEFT':
                gain = year * self.prices[left]
                order.append((year, 'LEFT', self.prices[left], gain))
                left += 1
            else:
                gain = year * self.prices[right]
                order.append((year, 'RIGHT', self.prices[right], gain))
                right -= 1
        
        return order
    
    def print_summary(self) -> None:
        """Stampa un riassunto completo della soluzione."""
        max_profit = self.calculate_max_profit()
        optimal_order = self.get_optimal_order()
        
        print("=" * 70)
        print("🍷 WINE SALES OPTIMIZATION REPORT")
        print("=" * 70)
        print(f"\nPrezzi iniziali: {self.prices}")
        print(f"Numero di vini: {self.N}")
        print(f"\n{'ANNO':<6}{'POSIZIONE':<12}{'PREZZO INIT':<15}{'GUADAGNO':<12}{'TOTALE':<12}")
        print("-" * 70)
        
        total_profit = 0
        for year, position, price, gain in optimal_order:
            total_profit += gain
            print(
                f"{year:<6}{position:<12}{price:<15}{gain:<12}{total_profit:<12}"
            )
        
        print("-" * 70)
        print(f"PROFITTO MASSIMO: {max_profit} 💰")
        print("=" * 70 + "\n")


# Funzioni di utilità
def max_profit_from_wine_sales(prices: List[int]) -> int:
    """Funzione wrapper per compatibilità."""
    optimizer = WineSalesOptimizer(prices)
    return optimizer.calculate_max_profit()


def show_optimal_order(prices: List[int]) -> None:
    """Mostra l'ordine ottimale di vendita con dettagli."""
    optimizer = WineSalesOptimizer(prices)
    optimizer.print_summary()


if __name__ == "__main__":
    # Esempio di utilizzo
    prezzi = [2, 3, 5, 1, 4]
    show_optimal_order(prezzi)
    
    # Test aggiuntivi
    print("\n" + "=" * 70)
    print("TEST AGGIUNTIVI")
    print("=" * 70 + "\n")
    
    test_cases = [
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [10],
        [1, 1, 1, 1]
    ]
    
    for test in test_cases:
        show_optimal_order(test)
