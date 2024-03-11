# rankine.py
#region Import
from steam import SteamTable
#endregion

#region Class
class RankineCycle:
    """
        Represents a Rankine cycle power generation system, allowing for
        the calculation of its efficiency and other key parameters. This
        class supports both saturated and superheated steam cycles.

        Attributes and Methods:
        - calculate_cycle: Performs the cycle calculations based on
          initial high pressure, low pressure, and optional high temperature.
        - print_summary: Outputs a summary of cycle performance metrics.
        """
    def __init__(self, p_high, p_low, t_high=None, name="Rankine Cycle"):
        """
                Initializes a RankineCycle object with the given parameters.

                Parameters:
                - p_high: High pressure of the cycle in kPa.
                - p_low: Low pressure of the cycle in kPa.
                - t_high: Optional high temperature for superheated cycles in Celsius.
                - name: Optional name for the cycle.
                """
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
        """
               Calculates the efficiency, work done by the turbine, work done by the
               pump, and heat added for the Rankine cycle. Adjusts calculations
               for superheated steam if a high temperature is specified.

               No parameters. Uses object attributes to perform calculations and
               updates the object's properties with the results.
               """
        if self.t_high:  # Superheated steam
            steam_props = self.steam_table.get_superheat_properties(self.p_high, self.t_high)
        else:  # Saturated steam
            steam_props = self.steam_table.get_sat_properties(self.p_high)

        h1 = steam_props['h']
        h2 = steam_props['hf']  # This now works for both cases
        self.turbine_work = h1 - h2
        self.pump_work = 15  # Placeholder for pump work calculation
        self.heat_added = h1 - steam_props['hf']
        self.efficiency = (self.turbine_work - self.pump_work) / self.heat_added

    def print_summary(self):
        """
                Prints a summary of the Rankine cycle's performance, including
                efficiency, turbine work, pump work, and heat added. This summary
                provides a quick overview of cycle effectiveness and key performance
                """
        print(f"Cycle Summary for: {self.name}")
        print(f"\tEfficiency: {self.efficiency * 100:.2f}%")
        print(f"\tTurbine Work: {self.turbine_work:.2f} kJ/kg")
        print(f"\tPump Work: {self.pump_work:.2f} kJ/kg")
        print(f"\tHeat Added: {self.heat_added:.2f} kJ/kg")
#endregion:
