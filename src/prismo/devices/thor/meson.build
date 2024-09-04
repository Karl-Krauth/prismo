thor_dep = meson.get_compiler('cpp').find_library('TLUP_64', dirs: meson.current_source_dir())

py.extension_module('thor',
    'thor_lib.cpp',
    subdir: 'prismo/devices/thor',
    install: true,
    dependencies : [pybind11_dep, thor_dep],
)
