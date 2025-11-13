import pandas as pd
import numpy as np
import sys
from pathlib import Path

# ---------- knobs (tweak later) ----------
KWH_PER_KG     = 52.0     # electrolyser specific energy (kWh/kg) – toy value
P_MIN_W        = 2.0      # min DC power to count electrolyser as ON
MAX_RIPPLE     = 0.10     # max allowed Vout ripple (fraction)
RIPPLE_WIN_FRAC= 0.002    # rolling window ~0.2% of samples for ripple
# ----------------------------------------

csv_path = Path("sim.csv")
if not csv_path.exists():
    print("sim.csv not found. Run the sim first: ./spice_runner")
    sys.exit(1)

# ngspice 'wrdata' pairs: time val time val ...
# Your wrdata: time v(in) v(out) pin_node pout_node
# Columns:
#  0: t(s)
#  1: t(v(in))  2: v(in)
#  3: t(v(out)) 4: v(out)
#  5: t(pin)    6: pin_node (W)
#  7: t(pout)   8: pout_node (W)
raw = pd.read_csv("sim.csv", sep=r"\s+", header=None)
ncol = raw.shape[1]
if ncol < 9:
    print(f"Unexpected sim.csv shape ({ncol} cols). "
          "Make sure wrdata line is: wrdata sim.csv time v(in) v(out) pin_node pout_node")
    sys.exit(1)

def col(idx, fill=0.0):
    if idx < ncol:
        return raw.iloc[:, idx].values
    return np.full(len(raw), fill)

t         = col(0)
vin       = col(2)
vout      = col(4)
pin_node  = col(6)   # already in Watts (from netlist helper)
pout_node = col(8)   # already in Watts

df = pd.DataFrame({
    "time_s": t,
    "vin": vin,
    "vout": vout,
    "Pin_W": pin_node,
    "Pout_W": pout_node
}).dropna(subset=["time_s"]).sort_values("time_s").reset_index(drop=True)

# Remove any NaN in powers and clip to >= 0
df[["Pin_W","Pout_W"]] = df[["Pin_W","Pout_W"]].fillna(0.0).clip(lower=0.0)

# dt for integration
df["dt"] = df["time_s"].diff().fillna(0.0).clip(lower=0.0)

# Ripple (rolling Vpp/Vmean on Vout)
win = max(5, int(len(df) * RIPPLE_WIN_FRAC))
roll_max  = df["vout"].rolling(win, min_periods=1).max()
roll_min  = df["vout"].rolling(win, min_periods=1).min()
roll_mean = df["vout"].rolling(win, min_periods=1).mean().replace(0, np.nan)
df["ripple_frac"] = ((roll_max - roll_min) / roll_mean).fillna(0.0)

# On/off gate: enough power and limited ripple
df["on"] = (df["Pout_W"] >= P_MIN_W) & (df["ripple_frac"] <= MAX_RIPPLE)

# Power -> hydrogen mass flow (kg/s) only while ON
# P[W] = (kg/s) * (kWh/kg) * 3600  =>  kg/s = P / (kWh/kg * 3600)
df["H2_kg_s"] = np.where(df["on"], df["Pout_W"] / (KWH_PER_KG * 3600.0), 0.0)
df["H2_kg"]   = (df["H2_kg_s"] * df["dt"]).cumsum()

# Rollups
sim_T  = float(df["time_s"].iloc[-1] if len(df) else 0.0)
h2_tot = float(df["H2_kg"].iloc[-1] if len(df) else 0.0)
uptime = 100.0 * float(df["on"].mean() if len(df) else 0.0)
p_avg  = float(df.loc[df["on"], "Pout_W"].mean() if df["on"].any() else 0.0)

print(f"H2 produced (this {sim_T:.3e}s sim): {h2_tot:.9f} kg")
print(f"Avg DC power while ON:                         {p_avg:.1f} W")
print(f"Electrolyser uptime:                           {uptime:.1f}%")

df.to_csv("h2_timeseries.csv", index=False)
print("Wrote h2_timeseries.csv")

