import unittest
from vendita_vini_memoizzazione import max_profit_from_wine_sales
from vendita_vini_ottimale import WineSalesOptimizer


class TestWineSales(unittest.TestCase):
    """Test cases per il problema della vendita dei vini."""
    
    def test_basic_example(self):
        """Test con l'esempio base."""
        prices = [2, 3, 5, 1, 4]
        result = max_profit_from_wine_sales(prices)
        self.assertEqual(result, 50)
    
    def test_single_wine(self):
        """Test con un solo vino."""
        prices = [5]
        result = max_profit_from_wine_sales(prices)
        self.assertEqual(result, 5)
    
    def test_two_wines(self):
        """Test con due vini."""
        prices = [1, 2]
        result = max_profit_from_wine_sales(prices)
        self.assertEqual(result, 4)  # Vendi a destra anno 1: 2, a sinistra anno 2: 2
    
    def test_ascending_prices(self):
        """Test con prezzi in ordine crescente."""
        prices = [1, 2, 3, 4, 5]
        result = max_profit_from_wine_sales(prices)
        self.assertGreater(result, 0)
    
    def test_descending_prices(self):
        """Test con prezzi in ordine decrescente."""
        prices = [5, 4, 3, 2, 1]
        result = max_profit_from_wine_sales(prices)
        self.assertGreater(result, 0)
    
    def test_equal_prices(self):
        """Test con prezzi uguali."""
        prices = [2, 2, 2, 2]
        result = max_profit_from_wine_sales(prices)
        expected = 2 * (1 + 2 + 3 + 4)  # 20
        self.assertEqual(result, expected)
    
    def test_optimizer_order(self):
        """Test della ricostruzione dell'ordine ottimale."""
        prices = [2, 3, 5, 1, 4]
        optimizer = WineSalesOptimizer(prices)
        max_profit = optimizer.calculate_max_profit()
        order = optimizer.get_optimal_order()
        
        self.assertEqual(len(order), len(prices))
        self.assertEqual(max_profit, 50)
        
        # Verifica che ogni anno sia presente
        years = [year for year, _, _, _ in order]
        self.assertEqual(years, list(range(1, len(prices) + 1)))


class TestEdgeCases(unittest.TestCase):
    """Test per casi edge."""
    
    def test_empty_list(self):
        """Test con lista vuota."""
        prices = []
        result = max_profit_from_wine_sales(prices)
        self.assertEqual(result, 0)
    
    def test_large_numbers(self):
        """Test con numeri grandi."""
        prices = [1000000, 2000000, 3000000]
        result = max_profit_from_wine_sales(prices)
        self.assertGreater(result, 0)
    
    def test_zero_prices(self):
        """Test con prezzi zero."""
        prices = [0, 0, 0]
        result = max_profit_from_wine_sales(prices)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
