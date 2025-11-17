#include <stdio.h>
#include "sim_shim.h"

int main(void) {
    SimResult res;
    int rc = run_simulation(
        1,     // n_panels
        12.0,  // Ton_us
        20.0,  // Tper_us
        5.0,   // Iset_A
        55.0,  // Vmin_V
        0.5,   // Rs_el_ohm
        470.0, // Cbus_uF
        &res   // <--- this was missing
    );

    if (rc != 0) {
        printf("run_simulation failed with code %d\n", rc);
        return 1;
    }

    printf("vout_avg_V      = %.3f V\n",  res.vout_avg_V);
    printf("vout_pp_V       = %.3f V\n",  res.vout_pp_V);
    printf("Pin_avg_W       = %.3f W\n",  res.Pin_avg_W);
    printf("Pout_avg_W      = %.3f W\n",  res.Pout_avg_W);
    printf("eff_pct         = %.2f %%\n", res.eff_pct);
    printf("H2_kg_window    = %.9f kg\n", res.H2_kg_window);
    printf("uptime_pct      = %.1f %%\n", res.uptime_pct);
    printf("sim_duration_s  = %.6f s\n", res.sim_duration_s);

    return 0;
}


