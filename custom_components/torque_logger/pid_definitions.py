"""Known Torque PID fallbacks. Torque metadata takes precedence.

Standard short PIDs accept optional leading zeroes. Identity is retained in
models to preserve existing entity unique IDs and history.
Sources: Torque upload protocol and torque-satellite/doc/codes.in.
"""

PID_DEFINITIONS = {'2f': ('Fuel level', '%'), '5': ('Engine coolant temperature', '°C'), '33': ('Barometric pressure', 'kPa'), '46': ('Ambient air temperature', '°C'), 'b': ('Intake manifold pressure', 'kPa'), 'd': ('Vehicle speed', 'km/h'), 'f': ('Intake air temperature', '°C'), 'c': ('Engine RPM', 'rpm'), '4': ('Engine load', '%'), '10': ('Mass air flow', 'g/s'), '11': ('Throttle position', '%'), '42': ('Control module voltage', 'V'), '5c': ('Engine oil temperature', '°C'), 'ff120c': ('Vehicle distance (profile)', 'km'), 'ff123b': ('GPS bearing', '°'), 'ff125d': ('Fuel flow rate', 'L/h'), 'ff126a': ('Estimated range', 'km'), 'ff126b': ('Fuel remaining', 'L'), 'ff1001': ('GPS speed', 'km/h'), 'ff1005': ('GPS longitude', None), 'ff1006': ('GPS latitude', None), 'ff1007': ('GPS bearing (legacy)', '°'), 'ff1010': ('GPS altitude', 'm'), 'ff1206': ('Trip average fuel economy', 'km/L'), 'ff1208': ('Trip average fuel consumption', 'L/100 km'), 'ff1238': ('OBD adapter voltage', 'V'), 'ff1239': ('GPS accuracy', 'm'), 'ff1258': ('Average CO2 emissions', 'g/km'), 'ff1266': ('Trip duration', 's'), 'ff1267': ('Trip stationary duration', 's'), 'ff1268': ('Trip moving duration', 's'), 'ff1271': ('Trip fuel used', 'L'), 'ff5202': ('Long term average fuel economy', 'km/L'), 'ff5203': ('Long term average fuel consumption', 'L/100 km')}


def pid_definition(pid: str) -> tuple[str | None, str | None]:
    key = pid.lower()
    if len(key) <= 2:
        key = key.lstrip("0") or "0"
    return PID_DEFINITIONS.get(key, (None, None))


def apply_defaults(info) -> None:
    name, unit = pid_definition(info.pid)
    if name and (not info.name or info.name.lower().startswith("pid ")):
        info.name = name
    if info.unit is None and unit:
        info.unit = unit
