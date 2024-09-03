#include <stdexcept>
#include <ranges>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "TLUP.h"


std::vector<std::string> devices() {
    ViStatus err;
    ViUInt32 num_rsrc;
    err = TLUP_findRsrc(0, &num_rsrc);
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not find devices. Error code: " + std::to_string(err)); 
    }

    std::vector<std::string> names;
    for (int i=0; i < num_rsrc; ++i) {
	ViChar name[512];
	err = TLUP_getRsrcName(0, i, name);
	if (err != VI_SUCCESS) {
            throw std::runtime_error("Could not get device name. Error code: " + std::to_string(err));
	}
        names.push_back(name);
    }

    return names;
}

PYBIND11_MODULE(thor_light, m) {
    m.def("devices", &devices);
    m.def("subtract", [](int i, int j) { return i + j; });
}
