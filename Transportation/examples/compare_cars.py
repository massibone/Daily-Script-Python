'''
Esempio: Confronto tra diversi tipi di auto
'''
import sys
sys.path.append('..')

from vehicle_calculator import Car, ElectricCar, HybridCar, compare_vehicles

# Crea veicoli
benzina = Car(18, 50, 1.75, "Toyota", "Corolla")
elettrica = ElectricCar(16, 75, 0.25, "Tesla", "Model 3")
ibrida = HybridCar(25, 43, 1.75, 60, "Toyota", "Prius")

# Confronta
print(compare_vehicles([benzina, elettrica, ibrida]))
