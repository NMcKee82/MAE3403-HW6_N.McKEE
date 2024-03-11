from steam import SteamProperties


class RankineCycle:
    def __init__(self, p_high, p_low, t_high=None):
        self.p_high = p_high
        self.p_low = p_low
        self.t_high = t_high
        self.efficiency = 0
        self.calculate_cycle()

    def calculate_cycle(self):
        # Simplified cycle calculation assuming ideal conditions and placeholder values
        if self.t_high:
            # Use superheated steam properties
            properties_high = SteamProperties.get_superheated_properties(self.p_high, self.t_high)
        else:
            # Use saturated steam properties
            properties_high = SteamProperties.get_saturated_properties(self.p_high)

        # Assume isentropic turbine and pump work, and calculate efficiency (placeholder logic)
        self.efficiency = 0.4  # Placeholder value

    def report(self):
        print(f"Rankine Cycle Efficiency: {self.efficiency * 100:.2f}%")
