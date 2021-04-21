# WoWBjectifier: A World of Warcraft Model Importer

TL;DR: This Blender add-on + WoW.Export = Streamlined material assignment with kinda-accurate texture blending and animated UVs.

## Installing

This add-on relies on an external python module called `kaitastruct`, which it uses to read additional data from .m2 files. In most situations it should automatically install the module with `pip` — the functions for that are in `/kaitai/m2_handler.py` — but there'll likely be a few edge cases where it'll need to be installed manually.

Beyond that, though, it should install like any other Blender add-on. Click on Edit→Preferences, navigate to the Add-ons tab, click the Install button on the top-right figure out where you've put `WoWbjectifier.zip`, select it, and mash the Install Add-on button.

## Using

WoWBjectifier is built to work with WoW.Export, and it reads both the JSON files that WoW.Export produces and the raw m2 files that it can export. This add-on works best if both of those files are in the same folder as the model you import.

Like most Blender importers, you'll find the WoWbjectifier import operator in the File→Import menu. Click it, and it'll pop up a file browser that looks something like this:

[Image Here]

Select the `.obj` file you want to import, pick what base shader configuration you want to use, click import, and you're good to go. Sorta.

WoWBjectifier relies on name matching to find the files it needs to import assets correctly. This means that the JSON, mtl, and m2 files that go with a particular `.obj` **need to have matching names.**

The add-on will figure out which textures it should use, how they're combined, and if/how they use animated UVs based on what's in these files. It will even search for a `/textures` sub-directory and find the textures it needs in there if they aren't in the same directory as the `.obj` file you're importing, by reading these files. You just need to make sure the names match.

## Options and Preferences

[words here]
