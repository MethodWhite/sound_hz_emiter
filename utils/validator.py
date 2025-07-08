from . import constants

def validate_frequency(value):
    try:
        freq = float(value)
        return constants.MIN_FREQUENCY <= freq <= constants.MAX_FREQUENCY
    except ValueError:
        return False

def validate_amplitude(value):
    try:
        amp = float(value)
        return constants.MIN_AMPLITUDE <= amp <= constants.MAX_AMPLITUDE
    except ValueError:
        return False