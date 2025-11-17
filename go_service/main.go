package main

/*
#cgo CFLAGS: -I.
#include "sim_shim.h"
*/
import "C"

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
)

// Go struct to hold the response we send back
type SimResponse struct {
	VoutAvgV     float64 `json:"vout_avg_V"`
	VoutPpV      float64 `json:"vout_pp_V"`
	PinAvgW      float64 `json:"Pin_avg_W"`
	PoutAvgW     float64 `json:"Pout_avg_W"`
	EffPct       float64 `json:"eff_pct"`
	H2KgWindow   float64 `json:"H2_kg_window"`
	UptimePct    float64 `json:"uptime_pct"`
	SimDurationS float64 `json:"sim_duration_s"`
}

// helper: read a float from the query string with a default
func getFloat(r *http.Request, name string, def float64) float64 {
	val := r.URL.Query().Get(name)
	if val == "" {
		return def
	}
	f, err := strconv.ParseFloat(val, 64)
	if err != nil {
		return def
	}
	return f
}

// helper: read an int from the query string with a default
func getInt(r *http.Request, name string, def int) int {
	val := r.URL.Query().Get(name)
	if val == "" {
		return def
	}
	i, err := strconv.Atoi(val)
	if err != nil {
		return def
	}
	return i
}

func simulateHandler(w http.ResponseWriter, r *http.Request) {
	// 1) Read inputs from query params (or use defaults)
	nPanels := getInt(r, "n_panels", 1)
	TonUs   := getFloat(r, "Ton_us", 12.0)
	TperUs  := getFloat(r, "Tper_us", 20.0)
	IsetA   := getFloat(r, "Iset_A", 5.0)
	VminV   := getFloat(r, "Vmin_V", 55.0)
	RsEl    := getFloat(r, "Rs_el_ohm", 0.5)
	CbusUF  := getFloat(r, "Cbus_uF", 470.0)

	log.Printf("simulate: n_panels=%d Ton=%.2f Tper=%.2f Iset=%.2f Vmin=%.2f Rs_el=%.2f Cbus=%.2f",
		nPanels, TonUs, TperUs, IsetA, VminV, RsEl, CbusUF)

	// 2) Call the C shim
	var res C.SimResult
	rc := C.run_simulation(
		C.int(nPanels),
		C.double(TonUs),
		C.double(TperUs),
		C.double(IsetA),
		C.double(VminV),
		C.double(RsEl),
		C.double(CbusUF),
		&res,
	)
	if rc != 0 {
		http.Error(w, fmt.Sprintf("run_simulation failed with code %d", int(rc)), http.StatusInternalServerError)
		return
	}

	// 3) Build response struct
	resp := SimResponse{
		VoutAvgV:     float64(res.vout_avg_V),
		VoutPpV:      float64(res.vout_pp_V),
		PinAvgW:      float64(res.Pin_avg_W),
		PoutAvgW:     float64(res.Pout_avg_W),
		EffPct:       float64(res.eff_pct),
		H2KgWindow:   float64(res.H2_kg_window),
		UptimePct:    float64(res.uptime_pct),
		SimDurationS: float64(res.sim_duration_s),
	}

	// 4) Send JSON back
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/simulate", simulateHandler)
	log.Println("Go sim service listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

