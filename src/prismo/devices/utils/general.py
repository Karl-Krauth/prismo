import time
from ..microfluidic import Chip

def sleep(seconds):
    """Interruptable sleep."""
    for _ in range(int(seconds)):
        time.sleep(1)

def _check_valve_mapping(chip: Chip, valve: str):
    if valve not in chip._mapping:
        raise ValueError(f'Valve {valve} not found in chip mappings.')

def _timestamp():
    return time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time()))