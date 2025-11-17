#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sim_shim.h"

// Helper to trim newline at end of string
static void trim_newline(char *s) {
    if (!s) return;
    size_t len = strlen(s);
    if (len > 0 && (s[len-1] == '\n' || s[len-1] == '\r')) {
        s[len-1] = '\0';
    }
}

int run_simulation(
    int    n_panels,
    double Ton_us,
    double Tper_us,
    double Iset_A,
    double Vmin_V,
    double Rs_el_ohm,
    double Cbus_uF,
    SimResult* out
) {
    if (out == NULL) {
        return -1;
    }

    // 1) Write USER_INPUT.csv into the build/ folder
    FILE *f = fopen("build/USER_INPUT.csv", "w");
    if (!f) {
        perror("fopen USER_INPUT.csv");
        return -2;
    }

    fprintf(f, "n_panels,%d\n", n_panels);
    fprintf(f, "Ton_us,%.6g\n", Ton_us);
    fprintf(f, "Tper_us,%.6g\n", Tper_us);
    fprintf(f, "Iset_A,%.6g\n", Iset_A);
    fprintf(f, "Vmin_V,%.6g\n", Vmin_V);
    fprintf(f, "Rs_el_ohm,%.6g\n", Rs_el_ohm);
    fprintf(f, "Cbus_uF,%.6g\n", Cbus_uF);
    fclose(f);

    // 2) Run your existing Python exporter in the build/ folder
    //    This will run ngspice and write UNITY_DATA.csv
    int ret = system("cd build && python3 export_unity.py");
    if (ret != 0) {
        fprintf(stderr, "export_unity.py failed with code %d\n", ret);
        return -3;
    }

    // 3) Open UNITY_DATA.csv and parse the second line
    FILE *u = fopen("build/UNITY_DATA.csv", "r");
    if (!u) {
        perror("fopen UNITY_DATA.csv");
        return -4;
    }

    char line[512];

    // Skip header
    if (!fgets(line, sizeof(line), u)) {
        fclose(u);
        return -5;
    }

    // Read data row
    if (!fgets(line, sizeof(line), u)) {
        fclose(u);
        return -6;
    }
    fclose(u);
    trim_newline(line);

    // 4) Parse CSV columns
    // n_panels,vout_avg_V,vout_pp_V,Pin_avg_W,Pout_avg_W,eff_pct,H2_kg_window,uptime_pct,sim_duration_s
    char *token = strtok(line, ",");
    int col = 0;
    while (token != NULL) {
        switch (col) {
            case 1: out->vout_avg_V      = atof(token); break;
            case 2: out->vout_pp_V       = atof(token); break;
            case 3: out->Pin_avg_W       = atof(token); break;
            case 4: out->Pout_avg_W      = atof(token); break;
            case 5: out->eff_pct         = atof(token); break;
            case 6: out->H2_kg_window    = atof(token); break;
            case 7: out->uptime_pct      = atof(token); break;
            case 8: out->sim_duration_s  = atof(token); break;
            default: break; // col 0 is n_panels, we already know that
        }
        token = strtok(NULL, ",");
        col++;
    }

    return 0; // success
}
