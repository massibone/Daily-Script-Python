# Population Data

Modulo semplice per gestire dati di popolazione.

## Utilizzo

```python
from population_data import PopulationData

# Creare l'oggetto
data = PopulationData(
    years=[2041, 2062],
    populations=[9.09, 10.03]
)

# Ottenere popolazione
print(data.get_population(2041))  # 9.09

# Calcolare crescita
print(data.get_growth_rate(2041, 2062))  # 10.33%
Test
Copy
python test_population.py
