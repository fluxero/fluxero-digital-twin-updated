import csv, subprocess, sys
from pathlib import Path
import pandas as pd
import numpy as np

# ----------- parse USER_INPUT.csv (simple key,value) -----------
def read_user_input(csv_path: Path) -> dict:
    cfg = {}
    if not csv_path.exists():
        return cfg
    with csv_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",", 1)]
            if len(parts) == 2:
                cfg[parts[0]] = parts[1]
    return cfg

# ----------- parse ngspice wrdata (handles 11 or 12 cols) ----------
# wrdata line in your netlist:
#   wrdata sim.csv time v(in) v(out) i(L1) pin_node pout_node
# Some ngspice builds write 11 columns (values at 2,4,6,8,10),
# others write 12 columns (values at 3,5,7,9,11). We auto-detect.
def parse_wrdata_pairs(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, sep=r"\s+", header=None)
    ncol = raw.shape[1]
    if ncol < 11:
        raise RuntimeError(f"Unexpected sim.csv shape ({ncol} cols). Need >= 11.")

    # default assume 11-col layout
    t_idx, vin_i, vout_i, iL1_i, pin_i, pout_i = 0, 2, 4, 6, 8, 10

    # heuristic for 12-col: values at 3/5/7/9/11 if those look more like volts than col2
    if ncol >= 12:
        sample = raw.head(5)
        c2_abs = sample.iloc[:, 2].abs().mean()
        c3_abs = sample.iloc[:, 3].abs().mean()
        if c3_abs > c2_abs * 5:  # col3 likely holds v(in) values
            vin_i, vout_i, iL1_i, pin_i, pout_i = 3, 5, 7, 9, 11

    t      = raw.iloc[:, t_idx].values
    vin    = raw.iloc[:, vin_i].values
    vout   = raw.iloc[:, vout_i].values
    iL1    = raw.iloc[:, iL1_i].values
    Pin_W  = raw.iloc[:, pin_i].values
    Pout_W = raw.iloc[:, pout_i].values

    df = pd.DataFrame({
        "time_s": t,
        "vin": vin,
        "vout": vout,
        "iL1": iL1,
        "Pin_W": Pin_W,
        "Pout_W": Pout_W
    }).dropna(subset=["time_s"]).sort_values("time_s").reset_index(drop=True)

    df["dt"] = df["time_s"].diff().fillna(0.0).clip(lower=0.0)
    return df

def window_tail(df: pd.DataFrame, tail_s: float = 0.0002) -> pd.DataFrame:
    if df.empty:
        return df
    t_end = df["time_s"].iloc[-1]
    return df[df["time_s"] >= (t_end - tail_s)].copy()

def compute_metrics(df: pd.DataFrame, kwh_per_kg=52.0, p_min_w=5.0, ripple_max=0.10):
    if df.empty:
        return dict(vout_avg=0.0, vout_pp=0.0, Pin_avg=0.0, Pout_avg=0.0,
                    eff_pct=0.0, H2_kg=0.0, uptime_pct=0.0)

    # look at last 0.2 ms (like your .meas window)
    win_df = window_tail(df, 0.0002)
    if win_df.empty:
        win_df = df

    vout_avg = float(win_df["vout"].mean())
    vout_pp  = float(win_df["vout"].max() - win_df["vout"].min())
    Pin_avg  = float(win_df["Pin_W"].mean())
    Pout_avg = float(win_df["Pout_W"].mean())
    eff_pct  = 100.0 * Pout_avg / Pin_avg if Pin_avg > 1e-12 else 0.0

    # simple ON gate using ripple + minimum power
    win = max(5, int(len(win_df) * 0.002))
    roll_max  = win_df["vout"].rolling(win, min_periods=1).max()
    roll_min  = win_df["vout"].rolling(win, min_periods=1).min()
    roll_mean = win_df["vout"].rolling(win, min_periods=1).mean().replace(0, np.nan)
    ripple_frac = ((roll_max - roll_min) / roll_mean).fillna(0.0)

    on_mask = (win_df["Pout_W"] >= p_min_w) & (ripple_frac <= ripple_max)
    uptime_pct = 100.0 * float(on_mask.mean()) if len(win_df) else 0.0

    # rough H2 estimate (W -> kg/s): kg/s = P / (kWh/kg * 3600)
    kg_s = np.where(on_mask, win_df["Pout_W"] / (kwh_per_kg * 3600.0), 0.0)
    H2_kg = float((kg_s * win_df["dt"]).sum())

    return dict(vout_avg=vout_avg, vout_pp=vout_pp, Pin_avg=Pin_avg, Pout_avg=Pout_avg,
                eff_pct=eff_pct, H2_kg=H2_kg, uptime_pct=uptime_pct)

def main():
    # Always resolve paths relative to this script
    script_dir = Path(__file__).resolve().parent
    runner   = script_dir / "spice_runner"
    netlist  = (script_dir.parent / "netlists" / "dcdc_boost_basic.cir").resolve()
    sim_csv  = script_dir / "sim.csv"
    unity_csv = script_dir / "UNITY_DATA.csv"
    user_csv  = script_dir / "USER_INPUT.csv"

    if not runner.exists():
        print(f"spice_runner not found at: {runner}\nBuild it here (cmake .. && cmake --build .)")
        sys.exit(1)
    if not netlist.exists():
        print(f"Netlist not found at: {netlist}")
        sys.exit(1)

    # read knobs (optional)
    cfg = read_user_input(user_csv)
    overrides = []
    def add_param(k_csv, k_param, suffix=""):
        if k_csv in cfg:
            overrides.append(f"{k_param}={cfg[k_csv]}{suffix}")
    add_param("Ton_us",   "Ton",   "u")
    add_param("Tper_us",  "Tper",  "u")
    add_param("Iset_A",   "Iset")
    add_param("Vmin_V",   "Vmin")
    add_param("Rs_el_ohm","Rs_el")
    add_param("Cbus_uF",  "Cbus",  "u")

    # run the sim (the netlist .control will run + wrdata sim.csv + quit)
    cmd = [str(runner), str(netlist)] + overrides
    subprocess.run(cmd)   # don't use check=True because ngspice quit can return non-zero

    if not sim_csv.exists():
        print(f"sim.csv not created at: {sim_csv}")
        print("Check your netlist .control includes: wrdata sim.csv time v(in) v(out) i(L1) pin_node pout_node")
        sys.exit(1)

    # parse + compute metrics
    df = parse_wrdata_pairs(sim_csv)
    metrics = compute_metrics(df)

    # panels multiplier for Unity (kept simple)
    n_panels = int(cfg.get("n_panels", "1"))
    sim_dur  = float(df["time_s"].iloc[-1]) if len(df) else 0.0

    with unity_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_panels","vout_avg_V","vout_pp_V","Pin_avg_W","Pout_avg_W",
                    "eff_pct","H2_kg_window","uptime_pct","sim_duration_s"])
        w.writerow([
            n_panels,
            round(metrics["vout_avg"],3),
            round(metrics["vout_pp"],3),
            round(metrics["Pin_avg"],3),
            round(metrics["Pout_avg"],3),
            round(metrics["eff_pct"],2),
            round(metrics["H2_kg"],9),
            round(metrics["uptime_pct"],1),
            round(sim_dur,6),
        ])
    print("Wrote UNITY_DATA.csv")

if __name__ == "__main__":
    main()

