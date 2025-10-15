# electronics/spice

DC/DC boost demo via libngspice.

## Build
cd packages/electronics/spice/build
cmake ..
cmake --build .

## Run
./spice_runner
# or (from build/)
./spice_runner ../netlists/dcdc_boost_basic.cir

## Output
Prints: vout_avg (~42 V from 30 V in).
