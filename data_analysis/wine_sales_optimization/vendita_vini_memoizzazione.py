"""
Soluzione di memoizzazione base per il problema della vendita dei vini.

Strategia:
- Vendere prima i vini con prezzo iniziale più basso
- Conservare i vini costosi per gli anni futuri quando valgono di più

Complessità:
- Temporale: O(N²)
- Spaziale: O(N²)
"""

from typing import List


def max_profit_from_wine_sales(prices: List[int]) -> int:
    """
    Calcola il profitto massimo dalla vendita di vini.
    
    Args:
        prices: Lista dei prezzi iniziali dei vini
        
    Returns:
        Profitto massimo ottenibile
    """
    N = len(prices)
    if N == 0:
        return 0
    
    cache = [[-1] * N for _ in range(N)]
    
    def profit(be: int, en: int) -> int:
        """
        Calcola il profitto massimo per i vini nell'intervallo [be, en].
        
        Args:
            be: Indice del primo vino disponibile (begin)
            en: Indice dell'ultimo vino disponibile (end)
            
        Returns:
            Profitto massimo per questo intervallo
        """
        if be > en:
            return 0
        
        # Ritorna il valore in cache se già calcolato
        if cache[be][en] != -1:
            return cache[be][en]
        
        # Calcola l'anno corrente
        # numero di vini rimanenti = en - be + 1
        # anno = N - (vini rimanenti) + 1
        year = N - (en - be + 1) + 1
        
        # Scegli di vendere il vino a sinistra o a destra
        cache[be][en] = max(
            year * prices[be] + profit(be + 1, en),
            year * prices[en] + profit(be, en - 1)
        )
        
        return cache[be][en]
    
    return profit(0, N - 1)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        [2, 3, 5, 1, 4],
        [1, 2, 3, 4, 5],
        [5],
        [10, 20],
        [1, 1, 1, 1]
    ]
    
    for prezzi in test_cases:
        risultato = max_profit_from_wine_sales(prezzi)
        print(f"Prezzi: {prezzi}")
        print(f"Profitto massimo: {risultato}\n")
