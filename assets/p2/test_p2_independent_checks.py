"""Independent numerical checks for the preliminary HDA-1 / P2 sizing.

These are regression checks for the explicitly stated screening assumptions;
they do not replace a code calculation or product validation.
"""
import math


def close(actual, expected, rel=0.005):
    assert math.isclose(actual, expected, rel_tol=rel), (actual, expected)


def test_top_driven_shaft_screening():
    d, L, F, T, E = 0.020, 0.120, 250.0, 24.0, 193e9
    I = math.pi * d**4 / 64
    moment = F * L
    sigma = 32 * moment / (math.pi * d**3)
    tau = 16 * T / (math.pi * d**3)
    vm = math.hypot(sigma, math.sqrt(3) * tau)
    deflection = F * L**3 / (3 * E * I)
    close(moment, 30.0)
    close(sigma / 1e6, 38.20)
    close(tau / 1e6, 15.28)
    close(vm / 1e6, 46.47)
    close(deflection * 1000, 0.095)
    assert 170e6 / vm > 3.6


def test_drive_and_bearing_screening():
    peak_torque, rpm = 24.0, 120.0
    power = 2 * math.pi * rpm / 60 * peak_torque
    close(power, 301.59)
    max_torque_450w = 450.0 / (2 * math.pi * rpm / 60)
    close(max_torque_450w, 35.81)
    l10_h = ((7000.0 / 500.0) ** 3 * 1e6) / (60 * 360.0)
    close(l10_h, 127037.0)


def test_air_charge_and_lock_loads():
    volume_l, atm_kpa, flow_nl_min = 3.6, 101.325, 6.0
    added_nl_20 = volume_l * 20.0 / atm_kpa
    close(added_nl_20, 0.7108)
    close(added_nl_20 / flow_nl_min * 60, 7.108)
    area = math.pi * 0.210**2 / 4
    close(area * 1e4, 346.36)
    total_60 = 60e3 * area + 1000.0
    close(total_60 / 8, 384.77)
    total_325 = 325e3 * area + 1000.0
    close(total_325 / 8, 1532.09)


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
            print('PASS', name)
