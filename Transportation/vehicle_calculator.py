'''
Vehicle Calculator - Sistema per calcolo consumo, autonomia e proprietà veicoli

Questo modulo fornisce un framework orientato agli oggetti per modellare diversi
tipi di veicoli e calcolarne autonomia, consumi, costi e caratteristiche.

🚗 Tipi di veicolo supportati:
  • Car (Benzina/Diesel)
  • ElectricCar (Elettrica)
  • HybridCar (Ibrida)
  • Motorcycle (Moto)
  • Truck (Camion)

📊 Calcoli disponibili:
  • Autonomia massima (range)
  • Consumo per 100km
  • Costo per km
  • Emissioni CO₂
  • Tempo di rifornimento/ricarica
  • Analisi economica comparativa

🎯 Uso:
    car = Car(fuel_efficiency=15, fuel_capacity=50, fuel_cost=1.8)
    print(vehicle_analyzer(car))
    
    electric = ElectricCar(efficiency=18, battery_capacity=75, electricity_cost=0.25)
    print(vehicle_analyzer(electric))

📚 Background:
    - Fuel efficiency: km/litro per veicoli termici
    - Electric efficiency: kWh/100km per veicoli elettrici
    - Range: autonomia massima in km
    - CO₂ emissions: grammi di CO₂ per km

Autore: Based on FreeCodeCamp OOP Pattern
License: MIT
'''

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
import math


# ============================================================================
# Classe Base Astratta: Vehicle
# ============================================================================

class Vehicle(ABC):
    """
    Classe astratta base per tutti i veicoli.
    
    Attributes:
        type (str): Tipo di veicolo (definito nelle sottoclassi)
        fuel_type (str): Tipo di carburante (definito nelle sottoclassi)
        emission_factor (float): Fattore emissioni CO₂ g/km
    """
    type: str
    fuel_type: str
    emission_factor: float = 0  # g CO₂/km
    
    def __init__(self, fuel_efficiency: float, fuel_capacity: float, 
                 fuel_cost: float = 0, brand: str = "Generic", 
                 model: str = "Model"):
        """
        Inizializza un veicolo.
        
        Args:
            fuel_efficiency: Efficienza (km/l per termici, kWh/100km per elettrici)
            fuel_capacity: Capacità serbatoio (litri) o batteria (kWh)
            fuel_cost: Costo carburante per unità (€/l o €/kWh)
            brand: Marca del veicolo
            model: Modello del veicolo
        
        Raises:
            TypeError: Se i parametri non sono numerici
            ValueError: Se i valori sono negativi o zero
        """
        # Validazione input
        if not all(isinstance(arg, (int, float)) for arg in [fuel_efficiency, fuel_capacity, fuel_cost]):
            raise TypeError("Fuel efficiency, capacity and cost must be numeric")
        
        if fuel_efficiency <= 0 or fuel_capacity <= 0:
            raise ValueError("Fuel efficiency and capacity must be positive")
        
        if fuel_cost < 0:
            raise ValueError("Fuel cost cannot be negative")
        
        self.fuel_efficiency = fuel_efficiency
        self.fuel_capacity = fuel_capacity
        self.fuel_cost = fuel_cost
        self.brand = brand
        self.model = model
    
    def __init_subclass__(cls):
        """Validazione attributi di classe nelle sottoclassi"""
        if not hasattr(cls, "type"):
            raise AttributeError(
                f"Cannot create '{cls.__name__}' class: missing required attribute 'type'"
            )
        if not hasattr(cls, "fuel_type"):
            raise AttributeError(
                f"Cannot create '{cls.__name__}' class: missing required attribute 'fuel_type'"
            )
    
    def __str__(self):
        """Rappresentazione stringa del veicolo"""
        return f"{self.brand} {self.model} ({self.type})"
    
    def __repr__(self):
        """Rappresentazione per debugging"""
        return (f"{self.__class__.__name__}(fuel_efficiency={self.fuel_efficiency}, "
                f"fuel_capacity={self.fuel_capacity}, fuel_cost={self.fuel_cost})")
    
    @abstractmethod
    def range(self) -> float:
        """
        Calcola l'autonomia massima del veicolo.
        
        Returns:
            float: Autonomia in km
        """
        pass
    
    @abstractmethod
    def consumption_per_100km(self) -> float:
        """
        Calcola il consumo per 100 km.
        
        Returns:
            float: Consumo per 100km
        """
        pass
    
    @abstractmethod
    def cost_per_km(self) -> float:
        """
        Calcola il costo per km.
        
        Returns:
            float: Costo in € per km
        """
        pass
    
    @abstractmethod
    def emissions_per_km(self) -> float:
        """
        Calcola le emissioni di CO₂ per km.
        
        Returns:
            float: Emissioni in grammi CO₂ per km
        """
        pass
    
    def refuel_time(self, minutes: float = 5) -> float:
        """
        Tempo stimato per rifornimento completo.
        
        Args:
            minutes: Minuti per rifornimento (default: 5)
        
        Returns:
            float: Tempo in minuti
        """
        return minutes
    
    def analyze(self) -> Dict:
        """
        Analisi completa del veicolo.
        
        Returns:
            dict: Dizionario con tutte le metriche
        """
        return {
            'vehicle': str(self),
            'type': self.type,
            'fuel_type': self.fuel_type,
            'range_km': self.range(),
            'consumption_per_100km': self.consumption_per_100km(),
            'cost_per_km': self.cost_per_km(),
            'emissions_per_km': self.emissions_per_km(),
            'fuel_capacity': self.fuel_capacity,
            'refuel_time_min': self.refuel_time()
        }


# ============================================================================
# Veicoli a Combustione
# ============================================================================

class Car(Vehicle):
    """
    Auto a benzina o diesel.
    
    Examples:
        >>> car = Car(fuel_efficiency=15, fuel_capacity=50, fuel_cost=1.8)
        >>> car.range()
        750.0
        >>> car.cost_per_km()
        0.12
    """
    type = "Car"
    fuel_type = "Petrol/Diesel"
    emission_factor = 120  # g CO₂/km (media)
    
    def range(self) -> float:
        """Autonomia: km/l × litri"""
        return self.fuel_efficiency * self.fuel_capacity
    
    def consumption_per_100km(self) -> float:
        """Consumo: 100 / (km/l) = litri/100km"""
        return 100 / self.fuel_efficiency
    
    def cost_per_km(self) -> float:
        """Costo: (€/l) / (km/l) = €/km"""
        return self.fuel_cost / self.fuel_efficiency
    
    def emissions_per_km(self) -> float:
        """Emissioni basate su fattore medio"""
        return self.emission_factor
    
    def refuel_time(self, minutes: float = 5) -> float:
        """Tempo rifornimento: ~5 minuti"""
        return minutes


class Motorcycle(Vehicle):
    """
    Motocicletta a benzina.
    
    Più efficiente delle auto ma con serbatoio più piccolo.
    """
    type = "Motorcycle"
    fuel_type = "Petrol"
    emission_factor = 90  # g CO₂/km (più basso delle auto)
    
    def range(self) -> float:
        return self.fuel_efficiency * self.fuel_capacity
    
    def consumption_per_100km(self) -> float:
        return 100 / self.fuel_efficiency
    
    def cost_per_km(self) -> float:
        return self.fuel_cost / self.fuel_efficiency
    
    def emissions_per_km(self) -> float:
        return self.emission_factor
    
    def refuel_time(self, minutes: float = 3) -> float:
        """Rifornimento più veloce: ~3 minuti"""
        return minutes


class Truck(Vehicle):
    """
    Camion/furgone commerciale.
    
    Consumi elevati ma grande capacità.
    """
    type = "Truck"
    fuel_type = "Diesel"
    emission_factor = 180  # g CO₂/km (più alto)
    
    def range(self) -> float:
        return self.fuel_efficiency * self.fuel_capacity
    
    def consumption_per_100km(self) -> float:
        return 100 / self.fuel_efficiency
    
    def cost_per_km(self) -> float:
        return self.fuel_cost / self.fuel_efficiency
    
    def emissions_per_km(self) -> float:
        return self.emission_factor
    
    def refuel_time(self, minutes: float = 10) -> float:
        """Rifornimento più lento: ~10 minuti"""
        return minutes


# ============================================================================
# Veicoli Elettrici
# ============================================================================

class ElectricCar(Vehicle):
    """
    Auto elettrica.
    
    Note:
        fuel_efficiency rappresenta kWh/100km
        fuel_capacity rappresenta capacità batteria in kWh
    
    Examples:
        >>> ev = ElectricCar(efficiency=18, battery_capacity=75, electricity_cost=0.25)
        >>> ev.range()
        416.67
        >>> ev.emissions_per_km()
        0
    """
    type = "Electric Car"
    fuel_type = "Electric"
    emission_factor = 0  # Zero emissioni dirette
    
    def range(self) -> float:
        """
        Autonomia elettrica: (kWh disponibili / kWh per 100km) × 100
        """
        return (self.fuel_capacity / self.fuel_efficiency) * 100
    
    def consumption_per_100km(self) -> float:
        """Consumo: kWh/100km"""
        return self.fuel_efficiency
    
    def cost_per_km(self) -> float:
        """Costo: (€/kWh × kWh/100km) / 100 = €/km"""
        return (self.fuel_cost * self.fuel_efficiency) / 100
    
    def emissions_per_km(self) -> float:
        """Emissioni dirette zero (non considera produzione energia)"""
        return self.emission_factor
    
    def refuel_time(self, minutes: float = 30) -> float:
        """
        Tempo ricarica rapida: ~30 minuti (80%)
        Ricarica completa lenta: diverse ore
        """
        return minutes
    
    def charging_cost(self) -> float:
        """Costo ricarica completa"""
        return self.fuel_capacity * self.fuel_cost


# ============================================================================
# Veicoli Ibridi
# ============================================================================

class HybridCar(Vehicle):
    """
    Auto ibrida (benzina + elettrico).
    
    Combina efficienza elettrica con autonomia a benzina.
    """
    type = "Hybrid Car"
    fuel_type = "Petrol + Electric"
    emission_factor = 80  # g CO₂/km (ridotto rispetto a benzina)
    
    def __init__(self, fuel_efficiency: float, fuel_capacity: float, 
                 fuel_cost: float = 0, electric_range: float = 50,
                 brand: str = "Generic", model: str = "Hybrid"):
        """
        Args:
            electric_range: Autonomia in modalità elettrica pura (km)
        """
        super().__init__(fuel_efficiency, fuel_capacity, fuel_cost, brand, model)
        self.electric_range = electric_range
    
    def range(self) -> float:
        """Autonomia totale: elettrica + termica"""
        thermal_range = self.fuel_efficiency * self.fuel_capacity
        return self.electric_range + thermal_range
    
    def consumption_per_100km(self) -> float:
        """Consumo medio ponderato"""
        total_range = self.range()
        electric_portion = self.electric_range / total_range
        thermal_portion = 1 - electric_portion
        thermal_consumption = 100 / self.fuel_efficiency
        return thermal_consumption * thermal_portion
    
    def cost_per_km(self) -> float:
        """Costo medio considerando parte elettrica"""
        thermal_cost = self.fuel_cost / self.fuel_efficiency
        total_range = self.range()
        thermal_range = total_range - self.electric_range
        thermal_portion = thermal_range / total_range
        return thermal_cost * thermal_portion
    
    def emissions_per_km(self) -> float:
        """Emissioni ridotte dalla modalità elettrica"""
        return self.emission_factor
    
    def refuel_time(self, minutes: float = 5) -> float:
        return minutes


# ============================================================================
# Analizzatore Veicoli
# ============================================================================

def vehicle_analyzer(vehicle: Vehicle) -> str:
    """
    Analizza un veicolo e produce un report dettagliato.
    
    Args:
        vehicle: Istanza di un veicolo
    
    Returns:
        str: Report formattato
    
    Raises:
        TypeError: Se l'argomento non è un Vehicle
    
    Examples:
        >>> car = Car(15, 50, 1.8, "Toyota", "Corolla")
        >>> print(vehicle_analyzer(car))
    """
    if not isinstance(vehicle, Vehicle):
        raise TypeError("Argument must be a Vehicle object")
    
    # Header
    output = f'\n{vehicle.type:-^50}\n'
    output += f'{str(vehicle):^50}\n'
    output += f'{"-" * 50}\n\n'
    
    # Specifiche tecniche
    output += f'{"SPECIFICHE TECNICHE":-^50}\n\n'
    output += f'{"Tipo carburante:":<25} {vehicle.fuel_type:>24}\n'
    
    if isinstance(vehicle, ElectricCar):
        output += f'{"Capacità batteria:":<25} {vehicle.fuel_capacity:>20.1f} kWh\n'
        output += f'{"Consumo:":<25} {vehicle.consumption_per_100km():>17.1f} kWh/100km\n'
    else:
        output += f'{"Capacità serbatoio:":<25} {vehicle.fuel_capacity:>22.1f} L\n'
        output += f'{"Consumo:":<25} {vehicle.consumption_per_100km():>19.1f} L/100km\n'
    
    # Autonomia
    output += f'\n{"AUTONOMIA":-^50}\n\n'
    range_km = vehicle.range()
    output += f'{"Autonomia massima:":<25} {range_km:>21.1f} km\n'
    
    if isinstance(vehicle, HybridCar):
        output += f'{"- Modalità elettrica:":<25} {vehicle.electric_range:>21.1f} km\n'
        thermal = range_km - vehicle.electric_range
        output += f'{"- Modalità termica:":<25} {thermal:>21.1f} km\n'
    
    # Tempo rifornimento
    refuel_time = vehicle.refuel_time()
    if isinstance(vehicle, ElectricCar):
        output += f'{"Tempo ricarica (80%):":<25} {refuel_time:>19.0f} min\n'
    else:
        output += f'{"Tempo rifornimento:":<25} {refuel_time:>19.0f} min\n'
    
    # Costi
    output += f'\n{"COSTI":-^50}\n\n'
    cost_km = vehicle.cost_per_km()
    output += f'{"Costo per km:":<25} {cost_km:>23.3f} €\n'
    
    # Calcola costi per distanze comuni
    distances = [100, 500, 1000, 10000]
    for dist in distances:
        cost = cost_km * dist
        output += f'{"Costo per " + str(dist) + " km:":<25} {cost:>21.2f} €\n'
    
    # Costo rifornimento completo
    if isinstance(vehicle, ElectricCar):
        full_cost = vehicle.charging_cost()
        output += f'{"Costo ricarica completa:":<25} {full_cost:>21.2f} €\n'
    else:
        full_cost = vehicle.fuel_capacity * vehicle.fuel_cost
        output += f'{"Costo rifornimento pieno:":<25} {full_cost:>19.2f} €\n'
    
    # Emissioni
    output += f'\n{"EMISSIONI CO₂":-^50}\n\n'
    emissions = vehicle.emissions_per_km()
    output += f'{"Emissioni per km:":<25} {emissions:>19.0f} g CO₂\n'
    
    # Emissioni per distanze comuni
    for dist in [100, 1000, 10000]:
        total_emissions = (emissions * dist) / 1000  # converti in kg
        output += f'{"Emissioni per " + str(dist) + " km:":<25} {total_emissions:>18.1f} kg CO₂\n'
    
    # Classificazione ambientale
    output += f'\n{"Classe ambientale:":<25}'
    if emissions == 0:
        output += f'{"⭐⭐⭐⭐⭐ Zero Emissioni":>24}\n'
    elif emissions < 100:
        output += f'{"⭐⭐⭐⭐ Molto Bassa":>24}\n'
    elif emissions < 130:
        output += f'{"⭐⭐⭐ Media":>24}\n'
    elif emissions < 160:
        output += f'{"⭐⭐ Alta":>24}\n'
    else:
        output += f'{"⭐ Molto Alta":>24}\n'
    
    output += f'\n{"-" * 50}\n'
    
    return output


def compare_vehicles(vehicles: List[Vehicle]) -> str:
    """
    Confronta multipli veicoli.
    
    Args:
        vehicles: Lista di veicoli da confrontare
    
    Returns:
        str: Tabella comparativa
    """
    if not vehicles:
        return "Nessun veicolo da confrontare"
    
    output = f'\n{"CONFRONTO VEICOLI":=^80}\n\n'
    
    # Header tabella
    output += f'{"Veicolo":<20} {"Range (km)":<12} {"€/km":<10} {"CO₂ (g/km)":<12} {"€ pieno":<10}\n'
    output += f'{"-" * 80}\n'
    
    # Righe veicoli
    for v in vehicles:
        full_cost = v.fuel_capacity * v.fuel_cost
        output += f'{str(v):<20} {v.range():<12.0f} {v.cost_per_km():<10.3f} '
        output += f'{v.emissions_per_km():<12.0f} {full_cost:<10.2f}\n'
    
    output += f'{"-" * 80}\n'
    
    # Raccomandazioni
    output += f'\n{"RACCOMANDAZIONI":-^80}\n\n'
    
    min_cost = min(vehicles, key=lambda v: v.cost_per_km())
    output += f'💰 Più economico per km: {str(min_cost)}\n'
    
    max_range = max(vehicles, key=lambda v: v.range())
    output += f'🏁 Maggiore autonomia: {str(max_range)}\n'
    
    min_emissions = min(vehicles, key=lambda v: v.emissions_per_km())
    output += f'🌱 Minori emissioni: {str(min_emissions)}\n'
    
    output += f'\n{"=" * 80}\n'
    
    return output


# ============================================================================
# Demo ed Esempi
# ============================================================================

def run_examples():
    """Esegue esempi dimostrativi"""
    
    print("=" * 70)
    print("VEHICLE CALCULATOR - Analisi Consumo e Autonomia Veicoli")
    print("=" * 70)
    
    # Crea veicoli di esempio
    toyota_corolla = Car(
        fuel_efficiency=18,      # 18 km/l
        fuel_capacity=50,        # 50 litri
        fuel_cost=1.75,          # 1.75 €/l
        brand="Toyota",
        model="Corolla"
    )
    
    tesla_model3 = ElectricCar(
        fuel_efficiency=16,      # 16 kWh/100km
        fuel_capacity=75,        # 75 kWh
        fuel_cost=0.25,          # 0.25 €/kWh
        brand="Tesla",
        model="Model 3"
    )
    
    toyota_prius = HybridCar(
        fuel_efficiency=25,      # 25 km/l in modalità termica
        fuel_capacity=43,        # 43 litri
        fuel_cost=1.75,
        electric_range=60,       # 60 km elettrici
        brand="Toyota",
        model="Prius"
    )
    
    ducati_monster = Motorcycle(
        fuel_efficiency=22,      # 22 km/l
        fuel_capacity=15,        # 15 litri
        fuel_cost=1.85,          # 1.85 €/l
        brand="Ducati",
        model="Monster"
    )
    
    # Analisi singoli veicoli
    print(vehicle_analyzer(toyota_corolla))
    print(vehicle_analyzer(tesla_model3))
    print(vehicle_analyzer(toyota_prius))
    
    # Confronto
    vehicles = [toyota_corolla, tesla_model3, toyota_prius, ducati_monster]
    print(compare_vehicles(vehicles))


if __name__ == '__main__':
    run_examples()
