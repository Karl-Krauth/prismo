project(
    'prismo',
    version: '0.0.1',
    meson_version: '>= 1.1.0',
    default_options: [
        'cpp_std=c++20',
    ],
)

py = import('python').find_installation(pure: false)

cpp_dep = dependency('cpp', required: false)
if cpp_dep.found()
    # Only try to build the devices subdir if we have a c++ compiler.
    pybind11_dep = dependency('pybind11')
    cpp = meson.get_compiler('cpp')
    subdir('src/prismo/devices')
endif

install_subdir('src/prismo', install_dir: py.get_install_dir() / 'prismo', strip_directory: true)
