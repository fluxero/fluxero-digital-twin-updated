#ifndef SIM_SHIM_H
#define SIM_SHIM_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double vout_avg_V;
    double vout_pp_V;
    double Pin_avg_W;
    double Pout_avg_W;
    double eff_pct;
    double H2_kg_window;
    double uptime_pct;
    double sim_duration_s;
} SimResult;

int run_simulation(
    int    n_panels,
    double Ton_us,
    double Tper_us,
    double Iset_A,
    double Vmin_V,
    double Rs_el_ohm,
    double Cbus_uF,
    SimResult* out
);

#ifdef __cplusplus
}
#endif

#endif // SIM_SHIM_H
