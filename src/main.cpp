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
  if (ngSpice_Init(out_cb, stat_cb, exit_cb, data_cb, initdata_cb, bg_cb, nullptr) != 0) {
    std::cerr << "Failed to init ngspice.\n";
    return 1;
  }
  std::string netlist = (argc > 1) ? argv[1] : std::string("../netlists/dcdc_boost_basic.cir");
  std::string cmd = "source " + netlist;         // .control will run + wrdata + quit
  if (ngSpice_Command(const_cast<char*>(cmd.c_str())) != 0) {
    std::cerr << "Failed to source netlist at: " << netlist << "\n";
    return 1;
  }
  return 0;
}
