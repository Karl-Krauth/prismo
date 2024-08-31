project(
    'prismo',
    'cpp',
    version: '0.0.1',
    meson_version: '>= 1.1.0',
    default_options: [
        'cpp_std=c++11',
    ],
)

py = import('python').find_installation(pure: false)
pybind11_dep = dependency('pybind11')

py.extension_module('thor_light',
    'src/prismo/devices/thor_light/thor_light.cpp',
    subdir: 'prismo/devices/thor_light',
    install: true,
    dependencies : [pybind11_dep],
)

install_subdir('src/prismo', install_dir: py.get_install_dir() / 'prismo', strip_directory: true)
