import pandas as pd
import matplotlib.pyplot as plt

# Read space-separated file with no header
df = pd.read_csv("sim.csv", delim_whitespace=True, header=None)

# Map columns: (time,value) pairs repeated per signal
Vstart = 1.5  # in milliseconds, adjust if needed
t     = df.iloc[:, 0]      # time (s)
vin   = df.iloc[:, 3]      # V(in)
vout  = df.iloc[:, 5]      # V(out)
iL    = df.iloc[:, 7]      # Inductor current
Pin   = df.iloc[:, 9]      # Input power (W)
Pout  = df.iloc[:, 11]     # Output power (W)

time_ms = t * 1000.0

# ---- Plot voltages ----
plt.figure(figsize=(8,5))
plt.plot(time_ms, vin,  label="Input Voltage (V)")
plt.plot(time_ms, vout, label="Output Voltage (V)")
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.title("Boost Converter Voltages")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.legend()
# Add vertical line showing electrolyser activation
plt.axvline(x=Vstart, color='red', linestyle='--', label='Electrolyser turns on')
plt.legend()
plt.show()


# ---- Plot powers ----
plt.figure(figsize=(8,5))
plt.plot(time_ms, Pin,  label="Input Power (W)")
plt.plot(time_ms, Pout, label="Output Power (W)")
plt.xlabel("Time (ms)")
plt.ylabel("Power (W)")
plt.title("Instantaneous Power")
plt.legend()
plt.grid(True)
plt.tight_layout()
# Add vertical line showing electrolyser activation
plt.axvline(x=Vstart, color='red', linestyle='--', label='Electrolyser turns on')
plt.legend()
plt.show()

# ---- Plot inductor current (optional) ----
plt.figure(figsize=(8,5))
plt.plot(time_ms, iL, label="Inductor Current (A)")
plt.xlabel("Time (ms)")
plt.ylabel("Current (A)")
plt.title("Inductor Current Waveform")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

