project(
    'prismo',
    'cpp',
    version: '0.0.1',
    meson_version: '>= 1.1.0',
    default_options: [
        'cpp_std=c++20',
    ],
)

py = import('python').find_installation(pure: false)
pybind11_dep = dependency('pybind11')

subdir('src/prismo/devices')
install_subdir('src/prismo', install_dir: py.get_install_dir() / 'prismo', strip_directory: true)
