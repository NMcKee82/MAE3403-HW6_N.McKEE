# rankine.py
from steam import SteamTable


class RankineCycle:
    def __init__(self, p_high, p_low, t_high=None, name="Rankine Cycle"):
        self.steam_table = SteamTable()
        self.p_high = p_high
        self.p_low = p_low
        self.t_high = t_high
        self.name = name
        self.efficiency = 0
        self.turbine_work = 0
        self.pump_work = 0
        self.heat_added = 0

    def calculate_cycle(self):
        # Simplified cycle calculation
        if self.t_high:
            steam_props = self.steam_table.get_superheat_properties(self.p_high, self.t_high)
            h1 = steam_props['h']
        else:
            steam_props = self.steam_table.get_sat_properties(self.p_high)
            h1 = steam_props['hg']  # Saturated vapor enthalpy

        # Assuming isentropic expansion and pump work
        self.turbine_work = h1 - steam_props['hf']  # Simplified calculation
        self.pump_work = 10  # Placeholder value
        self.heat_added = h1 - steam_props['hf']  # Assuming only heating
        self.efficiency = (self.turbine_work - self.pump_work) / self.heat_added

    def print_summary(self):
        print(f"Cycle Summary for: {self.name}")
        print(f"\tEfficiency: {self.efficiency * 100:.2f}%")
        print(f"\tTurbine Work: {self.turbine_work:.2f} kJ/kg")
        print(f"\tPump Work: {self.pump_work:.2f} kJ/kg")
        print(f"\tHeat Added: {self.heat_added:.2f} kJ/kg")
