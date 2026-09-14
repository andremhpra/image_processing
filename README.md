# Pengolahan Citra Digital (D)

A Python project covering "Operasi Titik", "Operasi Geometri", "Operasi Multi
Citra", and "Operasi Global" from an Pengolahan Citra course.

Only supports `.bmp` and `.png` files based on the `imagelib` module.

## Usage

The operations can only be accessed by a Tkinter GUI for ease of use.
Before being able to run any of the project's modules, run:

```
pip install -e .
```

After that, you can launch the GUI by typing the following command (at `image_processing` directory):

```
gui
```

Pick an operation from the dropdown, click "Load..." or "Load from sample..." to pick one of the images bundled under `samples/`
for each input image slot it asks for (1 for single-image operations, 2 for blending/motion detection/logic operations).
Then click "Run" to preview the result and "Save result..." to write it out as `.bmp` or `.png`.

Clicking "Describe image..." opens any `.bmp`/`.png` file and reports its color depth,
resolution, and per-pixel values in a new window.

# Samples

`samples/` is the folder that will be opened when "Load from sample..." is pressed.
Should contain `.bmp/.png` files, other image formats are currently unsupported by the `imagelib` module.

This is so anyone that has cloned this project would already have images to work with,
especially for operations that requires specific kinds of images.
e.g. motion detection, where the same object should be in the image

## Adding Operations

Each operation group is its own module under `src/`, with one file per
technique re-exported from that module's `__init__.py`. If the new
operation belongs to an existing group, add a file under that group's
folder and export it from the `__init__.py`; if it starts a new group,
create a new module the same way, one file per technique.

After that, register the module to `src/gui/registry.py`,
which would automatically add it as an option at the dropdown,
with matching image input slots and parameter fields.
