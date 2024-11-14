# Artificial-Engine-Sound-Synthesis
Something wrong... Not working now.
Implementation of Artificial Engine Sound Synthesis
Base on Min's "Artificial Engine Sound Synthesis Method for Modification of the Acoustic Characteristics of Electric Vehicles" (DOI : 10.1155/2018/5209207)


# Implementation
Engine sound consist of mechanical sound and combustion sound.

1. Mechanical Sound Synthesis:
    Sum harmonic components representing the engine’s mechanical sounds.
	Use the Fourier series to compute the magnitudes and phases of these components.
2.	Combustion Sound Synthesis:
	Generate random noise with a specific frequency envelope.
	Modulate this noise according to the mechanical sound’s amplitude.
3.	Combining Sounds:
	Combine the mechanical and combustion sounds to produce the final engine sound.