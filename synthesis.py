import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import random

def synthesize_mechanical_sound(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    mechanical_sound = np.zeros_like(t)
    harmonics = [1, 2, 3, 4, 5]  # Example harmonics
    
    for harmonic in harmonics:
        mechanical_sound += np.cos(2 * np.pi * harmonic * frequency * t)
    
    return mechanical_sound / len(harmonics)

def synthesize_combustion_sound(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    combustion_sound = np.random.normal(0, 1, len(t))
    envelope = np.exp(-3 * t)  # Example envelope
    
    return combustion_sound * envelope

def combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude):
    combined_sound = mechanical_sound + mechanical_amplitude * combustion_sound
    return combined_sound / np.max(np.abs(combined_sound))