#include <mutex>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "TLUP.h"


std::mutex mutex;


std::vector<std::string> devices() {
    const std::lock_guard<std::mutex> lock(mutex);
    int err;
    unsigned int num_rsrc;
    err = TLUP_findRsrc(0, reinterpret_cast<ViPSession>(&num_rsrc));
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not find devices. Error code: " + std::to_string(err)); 
    }

    std::vector<std::string> names;
    for (int i = 0; i < num_rsrc; ++i) {
	ViChar name[512];
	err = TLUP_getRsrcName(0, i, name);
	if (err != VI_SUCCESS) {
            throw std::runtime_error("Could not get device name. Error code: " + std::to_string(err));
	}
        names.push_back(name);
    }

    return names;
}


unsigned int init_device(std::string port) {
    const std::lock_guard<std::mutex> lock(mutex);
    unsigned int device_id;
    int err = TLUP_init(port.data(), VI_FALSE, VI_FALSE, reinterpret_cast<ViPSession>(&device_id));
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not initialize device. Error code: " + std::to_string(err)); 
    }

    return device_id;
}


void close_device(int device_id) {
    const std::lock_guard<std::mutex> lock(mutex);
    int err = TLUP_close(device_id);
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not close device. Error code: " + std::to_string(err)); 
    }
}


std::tuple<std::string, std::string, double, double, double>
info(uint32_t device_id) {
    const std::lock_guard<std::mutex> lock(mutex);
    char name[256];
    char serial_num[256];
    ViReal64 ampere_limit, volt_limit, wavelength;
    int err = TLUP_getLedInfo(device_id, name, serial_num, &ampere_limit, &volt_limit, &wavelength);
    if (err != VI_SUCCESS) {
         throw std::runtime_error("Could not get device info. Error code: " + std::to_string(err)); 
    }

    return {name, serial_num, ampere_limit, volt_limit, wavelength};
}


PYBIND11_MODULE(thor_light, m) {
    m.def("devices", &devices);
    m.def("init", &init_device);
    m.def("close", &close_device);
    m.def("info", &info);
}
