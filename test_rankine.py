# test_rankine.py
from rankine import RankineCycle

def main():
    # Define cycle parameters and create RankineCycle instances
    cycle1 = RankineCycle(p_high=8000, p_low=8, t_high=None, name="Cycle 1: Saturated Vapor")
    cycle1.calculate_cycle()
    cycle1.print_summary()

    # Assuming a specific T_high based on the given p_high for superheated steam
    cycle2 = RankineCycle(p_high=8000, p_low=8, t_high=450, name="Cycle 2: Superheated Steam")
    cycle2.calculate_cycle()
    cycle2.print_summary()

if __name__ == "__main__":
    main()
