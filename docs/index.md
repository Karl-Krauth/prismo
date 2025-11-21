# Prismo
Prismo is a Python library that makes microscopy easy. It allows you to specify your experiments
in a succinct yet explicit manner, while transparently automating data management and visualization.
Prismo's focus on fast feedback means that you can immediately see when an experiment goes wrong
and course correct early.

## Setup

To install prismo simply run
```
pip install prismo
```
TODO: Add some stuff about micromanager dependency here.

## Usage
Here

```py
import prismo as pm

# Configure the devices. Here we only setup a demo camera and xy stage.
config = {
    "camera": {
        "device": "demo-camera"
    },
    "filter": {
        "filter": "demo-stage"
    }
}
# Load the devices and make a controller object.
c = pm.load(config)

# Display live updates from the camera.
pm.live(c)
# Move the stage right forever.
while True:
    c.wait()
    c.x += 1000
```
Note that image acquisition operations in prismo are nonblocking which means that `pm.live` will
immediately return and you'll be able to see the stage position updating from the live window.

## Magnify
Prismo's sibling library is Magnify. Magnify is a library for analyzing microscopy images. While
neither library depends on the other, Magnify was built with Prismo's file output format in mind.
You can even use Magnify to analyze your data in the middle of a prismo run. For more
details you can visit [Magnify's documentation page](https://github.com/FordyceLab/magnify/tree/gh-pages).
