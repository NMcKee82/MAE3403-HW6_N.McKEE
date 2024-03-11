from rankine import RankineCycle

# Define cycle parameters
p_high = 8000  # High pressure in kPa
p_low = 8      # Low pressure in kPa
t_high = None  # High temperature in °C for superheated steam

# Cycle 1: Saturated vapor entering turbine
cycle1 = RankineCycle(p_high, p_low)
cycle1.report()

# Cycle 2: Superheated steam into the turbine
t_high = 1.7 * 300  # Placeholder for T_sat corresponding to p_high
cycle2 = RankineCycle(p_high, p_low, t_high)
cycle2.report()
