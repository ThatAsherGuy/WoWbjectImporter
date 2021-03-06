# WoWbject Importer Lousy Testing Framework

## Setting Up

You will need a local install of python 3.6 (or newer), though it's probably
possible to use Blender's python as well if you really want to.

The `blender` executable must be in your path.

For output render comparisons, you will need to install [GraphicsMagick](https://sourceforge.net/projects/graphicsmagick/files/graphicsmagick-binaries/). The `gm` binary must be in your path.

You will need pytest and the pytest_dependency module. Install via `pip3 install pytest pytest_dependency`.


## Tests

Two main tests currently:

* *test_render:* Imports an obj exported from wow.export (with associated textures and metadata) and renders to an output file (output files go into the `render_results` directory)
* *test_render_check:* Compares the results of renders to a previously rendered corpus of images (stored in the `render_references` directory), and generates a numeric value based on the scale of differences found. Right now, this test fails if there are any differences whatsoever between the test and reference images.


## Layout

There are four main subdirectories:

* *test_data:*  The "input" test data. This directory consists of data exported from wow.export. There is a lot of data here. There is a `syncdata.sh` script in the tests directory that will download the data from Alinsa, since there's no way to do an automated export from wow.export. You will need `rsync` installed somewhere in your path.
* *render_references:* The corpus of "correct" renders for testing against. You can create your own by running the normal render test, and then `cp render_results/* render_references/`, if you think your current output is correct (i.e. prior to refactoring), or ask Alinsa for a copy of hers. Note that reference images created on a different computer may not be pixel-for-pixel identical to renders created locally, even if the render is correct
* *render_results:* The output images from the `test_render` check. These are what the current version of the code WoWbject code is producing
* *render_diffs:* When there are differences between the render_references and render_results images for a test, an image is written here, with the differing pixels highlighted in red. Ideally the diff would actually be an xor of the two images (which would just be 100% black for no differences), but GraphicsMagick doesn't support that(!?)

In addition, there is:

* *testlist.csv:* A CSV with test categorization, specific models to import, and various flags relating to importing those models. This format will get more useful in the future, once support for setting camera location and such is added.


## Running

Make sure you're in the `tests` directory, and run `pytest`. That's basically it. The full test suite takes a while. Sorry.

You can run a subset of tests by requesting certain tests via markers or by name. You can get a complete list of markers via `pytest --markers`, but the WoWbject-specific markers are:

* **m2:** Tests that work with m2 files
* **wmo:** Tests that work with wmo files
* **top10:** Run the "top 10" tests of each category, for quick testing. (The "top" tests are generally for the shaders that are used in the highest number of models)
* **top10m2** and **top10wmo**: The "top 10" tests for these specific categories
* **fancy:** Tests that render cool-looking things, meant to test nothing but the user's eyeballs (if these things don't look cool to you, please validate your eyeballs)
* **bug:** Validation for known bugs/problems; tests are named after the github issue they track
* **superfast:** Intended as an extremely fast test suite to verify very basic functionality, (super)fast

You can further (or alternately) run a subset of tests with `pytest -k <string>`, where only tests matching `<string>` will be run. When combined, only tests matching *both* of the `-m` and `-k` arguments will be run.
