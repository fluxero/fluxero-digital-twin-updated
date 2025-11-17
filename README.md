🚀 Fluxero Digital Twin Engine
Second-Life Solar → Boost Converter → Electrolyser → KPIs for Unity Visualisation

This repository contains the backend simulation engine for Fluxero’s digital twin.
It models how second-life solar feeds a boost converter and a simplified electrolyser, then outputs hydrogen KPIs into a CSV file (UNITY_DATA.csv).

⚠️ Unity is not included in this repo.
Unity is a separate front-end that simply reads the CSV generated here.

🌞 What This Engine Does
PV Source → Boost Converter → DC Bus → Electrolyser → KPIs → (Unity Front-End)

It models:

Second-life PV voltage variation

Switching boost converter (MOSFET, diode, inductor)

PWM control (Ton/Tper)

Output capacitor and DC bus behaviour

Simplified electrolyser threshold + current draw

Power, efficiency, and hydrogen production estimation

It outputs:

sim.csv – raw ngspice waveforms

UNITY_DATA.csv – clean KPIs for Unity

📂 Repository Structure
spice/
├── netlists/
│   └── dcdc_boost_basic.cir
├── src/
│   └── main.cpp
├── build/
│   ├── spice_runner
│   ├── export_unity.py
│   ├── USER_INPUT.csv
│   └── UNITY_DATA.csv (auto-generated)
├── CMakeLists.txt
└── README.md

🔧 Build Instructions (C++ Runner)

In the build directory:

cd build
cmake ..
cmake --build .


This builds the spice_runner executable.

▶️ Running a Simulation
1. Edit user parameters

Edit:

build/USER_INPUT.csv


Example:

n_panels,1
Ton_us,12
Tper_us,20
Iset_A,5
Vmin_V,55
Rs_el_ohm,0.5
Cbus_uF,470

2. Run the simulation:
cd build
python3 export_unity.py

3. View the output:
cat UNITY_DATA.csv

📊 UNITY_DATA.csv Format

Unity reads a single row containing:

Column	Meaning
n_panels	Number of solar panels
vout_avg_V	Average DC bus voltage
vout_pp_V	Voltage ripple
Pin_avg_W	Input power from PV
Pout_avg_W	Power delivered to electrolyser
eff_pct	Converter efficiency
H2_kg_window	Hydrogen produced in the measured window
uptime_pct	% time electrolyser was active
sim_duration_s	Simulation duration

Unity uses these KPIs to animate tanks, gauges, and system behaviour.

🔄 Live Refresh Mode (for Unity)

To auto-refresh the KPIs every 5 seconds:

while true; do python3 export_unity.py; sleep 5; done

🧱 Project Status
Completed:

Boost converter SPICE model

C++ ngspice runner

Python KPI exporter

CSV pipeline for Unity integration

Next steps:

Add irradiance/location inputs

Use real panel datasheets

Improve electrolyser I–V behaviour

Add hydrogen storage + fuel cell modules

Upgrade CSV → WebSocket live streaming

Requirements

macOS/Linux

ngspice + libngspice

C++17 compiler

Python 3 (pandas, numpy)

Unity (separate front-end project)
