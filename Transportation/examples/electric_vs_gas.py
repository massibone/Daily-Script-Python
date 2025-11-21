'''
Esempio: Analisi economica elettrico vs benzina su 10 anni
'''
import sys
sys.path.append('..')

from vehicle_calculator import Car, ElectricCar

print("=" * 70)
print("ANALISI ECONOMICA: ELETTRICO vs BENZINA (10 anni, 15.000 km/anno)")
print("=" * 70)

# Auto benzina
gas_car = Car(
    fuel_efficiency=16,
    fuel_capacity=50,
    fuel_cost=1.80,
    brand="Volkswagen",
    model="Golf"
)

# Auto elettrica
electric_car = ElectricCar(
    fuel_efficiency=17,
    battery_capacity=60,
    fuel_cost=0.25,
    brand="Volkswagen",
    model="ID.3"
)

km_per_year = 15000
years = 10
total_km = km_per_year * years

print(f"\nDistanza totale: {total_km:,} km in {years} anni\n")

# Calcolo costi
gas_cost = gas_car.cost_per_km() * total_km
electric_cost = electric_car.cost_per_km() * total_km

print(f"💰 COSTI CARBURANTE:")
print(f"   Benzina:  {gas_cost:>10,.2f} €")
print(f"   Elettrica: {electric_cost:>10,.2f} €")
print(f"   Risparmio: {gas_cost - electric_cost:>10,.2f} € ✅")

# Calcolo emissioni
gas_emissions = (gas_car.emissions_per_km() * total_km) / 1000  # in kg
electric_emissions = (electric_car.emissions_per_km() * total_km) / 1000

print(f"\n🌱 EMISSIONI CO₂:")
print(f"   Benzina:   {gas_emissions:>10,.1f} kg")
print(f"   Elettrica:  {electric_emissions:>10,.1f} kg")
print(f"   Riduzione: {gas_emissions - electric_emissions:>10,.1f} kg ✅")

print("\n" + "=" * 70)
