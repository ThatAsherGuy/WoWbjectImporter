#!/bin/bash
rm -f test.log
blender --factory-startup --python wowbject_render.py --background >>test.log

# For some reason, graphicsmagick on macOS, when its output is redirected,
# generates an 'inappropriate ioctl' message, so we gotta filter that in
# the name of sanity.
if gm compare output2.png output.png -file diff.png -highlight-style assign -metric MAE -maximum-error 0.0 2>&1 >/dev/null  | sed 's/\[Inappropriate ioctl for device\].//' | grep 'image difference exceeds limit'; then
    echo "ERROR: Image compare failure"
    exit 1
fi
