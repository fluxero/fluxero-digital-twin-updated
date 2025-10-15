#include <cstdio>
#include <iostream>
#include <string>

extern "C" {
  #include "ngspice/sharedspice.h"
}

/* Minimal callbacks required by the 7-arg ngSpice_Init API */
static int out_cb(char* msg, int, void*) { if (msg) std::fputs(msg, stdout); return 0; }
static int stat_cb(char*, int, void*) { return 0; }
static int exit_cb(int, bool, bool, int, void*) { return 0; }
static int data_cb(pvecvaluesall, int, int, void*) { return 0; }
static int initdata_cb(pvecinfoall, int, void*) { return 0; }
static int bg_cb(bool, int, void*) { return 0; }

int main(int argc, char** argv) {
  // Homebrew ngspice: returns 0 on success
  int rc = ngSpice_Init(out_cb, stat_cb, exit_cb, data_cb, initdata_cb, bg_cb, nullptr);
  if (rc != 0) {
    std::cerr << "Failed to init ngspice. rc=" << rc << "\n";
    return 1;
  }

  // Netlist path: default for running from /build, or take arg
  std::string netlist = (argc > 1) ? argv[1] : std::string("../netlists/dcdc_boost_basic.cir");

  std::string cmd = "source " + netlist;
  if (ngSpice_Command(const_cast<char*>(cmd.c_str())) != 0) {
    std::cerr << "Failed to source netlist at: " << netlist << "\n";
    return 1;
  }

  // Optional: override .param from CLI, e.g. Ton=10u Rload_val=100
for (int i = 2; i < argc; ++i) {
  std::string arg = argv[i];          // e.g. "Ton=10u"
  auto eq = arg.find('=');
  if (eq != std::string::npos) {
    std::string name = arg.substr(0, eq);
    std::string val  = arg.substr(eq + 1);
    std::string cmd  = "alterparam " + name + " = " + val;
    ngSpice_Command(const_cast<char*>(cmd.c_str()));
  }
}

  if (ngSpice_Command((char*)"run") != 0) {
    std::cerr << "Failed to run simulation.\n";
    return 1;
  }

  // Print single averaged number for clean output
  ngSpice_Command((char*)"meas tran vout_avg AVG v(out) from=4.8m to=5m");
  ngSpice_Command((char*)"print vout_avg");

  ngSpice_Command((char*)"quit");
  return 0;
}
