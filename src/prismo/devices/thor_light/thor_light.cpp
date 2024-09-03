#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "TLUP.h"


std::mutex mutex;


std::vector<std::string> devices() {
    const std::lock_guard<std::mutex> lock(mutex);
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


unsigned int init(std::string port) {
    const std::lock_guard<std::mutex> lock(mutex);
    unsigned int device_id;
    ViStatus err = TLUP_init(port, VI_FALSE, VI_FALSE, &device_id);
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not initialize device. Error code: " + std::to_string(err)); 
    }

    return device_id;
}


void close(unsigned int device_id) {
    const std::lock_guard<std::mutex> lock(mutex);
    ViStatus err = TLUP_close(device_id);
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not close device. Error code: " + std::to_string(err)); 
    }
}


PYBIND11_MODULE(thor_light, m) {
    m.def("devices", &devices);
    m.def("init", &init);
    m.def("close", &close);
}
