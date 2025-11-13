import pandas as pd
import matplotlib.pyplot as plt

# Load data from ngspice output
df = pd.read_csv("sim.csv")

# Convert time from seconds to milliseconds for readability
df["time_ms"] = df["time"] * 1000

# Compute instantaneous power
df["Pin"] = df["v(pin_node)"]
df["Pout"] = df["v(pout_node)"]

# --- Plot voltages ---
plt.figure(figsize=(8,5))
plt.plot(df["time_ms"], df["v(in)"], label="Input Voltage (V)")
plt.plot(df["time_ms"], df["v(out)"], label="Output Voltage (V)")
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.title("Boost Converter Voltages")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Plot powers ---
plt.figure(figsize=(8,5))
plt.plot(df["time_ms"], df["Pin"], label="Input Power (W)")
plt.plot(df["time_ms"], df["Pout"], label="Output Power (W)")
plt.xlabel("Time (ms)")
plt.ylabel("Power (W)")
plt.title("Instantaneous Power")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
