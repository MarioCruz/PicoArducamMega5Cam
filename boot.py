# Boot configuration
import machine
import gc

# Set CPU frequency
machine.freq(240000000)

# Collect garbage
gc.collect()
