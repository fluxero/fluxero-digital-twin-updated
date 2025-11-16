#include <cstdio>
#include <iostream>
#include <string>

extern "C" {
  #include "ngspice/sharedspice.h"
}

static int out_cb(char* msg, int, void*) { if (msg) std::fputs(msg, stdout); return 0; }
static int stat_cb(char*, int, void*) { return 0; }
static int exit_cb(int, bool, bool, int, void*) { return 0; }
static int data_cb(pvecvaluesall, int, int, void*) { return 0; }
static int initdata_cb(pvecinfoall, int, void*) { return 0; }
static int bg_cb(bool, int, void*) { return 0; }

int main(int argc, char** argv) {
  // Initialise embedded ngspice
  if (ngSpice_Init(out_cb, stat_cb, exit_cb, data_cb, initdata_cb, bg_cb, nullptr) != 0) {
    std::cerr << "Failed to init ngspice.\n";
    return 1;
  }

  // 1) Choose netlist: argv[1] if provided, else default
  std::string netlist = (argc > 1)
      ? argv[1]
      : std::string("../netlists/dcdc_boost_basic.cir");

  // 2) Load the netlist
  std::string cmd = "source " + netlist;
  if (ngSpice_Command(const_cast<char*>(cmd.c_str())) != 0) {
    std::cerr << "Failed to source netlist at: " << netlist << "\n";
    return 1;
  }

  // 3) Apply parameter overrides from argv[2..]
  //    e.g. argv[2] = "Ton=15u" -> "alterparam Ton=15u"
  for (int i = 2; i < argc; ++i) {
    std::string alter = "alterparam " + std::string(argv[i]);
    ngSpice_Command(const_cast<char*>(alter.c_str()));
  }

  // 4) Run the simulation and write sim.csv
  ngSpice_Command(const_cast<char*>("run"));
  ngSpice_Command(const_cast<char*>(
      "wrdata sim.csv time v(in) v(out) i(L1) pin_node pout_node"));

  return 0;
}


