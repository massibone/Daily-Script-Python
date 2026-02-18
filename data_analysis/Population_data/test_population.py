"""Test semplici per population_data.py"""

from population_data import PopulationData

# Creare dati di test
data = PopulationData([2041, 2062], [9.09, 10.03])

# Test 1
assert data.get_population(2041) == 9.09
print("✓ Test 1 passed")

# Test 2
assert data.get_population(2062) == 10.03
print("✓ Test 2 passed")

# Test 3
growth = data.get_growth_rate(2041, 2062)
assert 10 < growth < 11
print(f"✓ Test 3 passed - Growth: {growth}%")

# Test 4 - Anno non trovato
result = data.get_population(2100)
assert "non trovato" in result
print("✓ Test 4 passed")

print("\n✅ Tutti i test passati!")
