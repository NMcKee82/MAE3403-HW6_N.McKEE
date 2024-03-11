# test_rankine.py
from rankine import RankineCycle

def main():
    cycle1 = RankineCycle(p_high=8000, p_low=10, name="Basic Saturated Steam Cycle")
    cycle1.calculate_cycle()
    cycle1.print_summary()

    cycle2 = RankineCycle(p_high=8000, p_low=10, t_high=500, name="Superheated Steam Cycle")
    cycle2.calculate_cycle()
    cycle2.print_summary()

if __name__ == "__main__":
    main()
