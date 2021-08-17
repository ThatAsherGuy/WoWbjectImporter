#!/bin/bash
# You can really only use this if you're Alinsa
rsync -e "/c/portable/cwrsync/bin/ssh.exe -T -x" \
    --recursive --links --safe-links --times \
    --verbose --progress --stats \
    --delete --delete-during --delete-excluded \
    --exclude '*.blp' --exclude '*.wmo' \
    test_data/ v.lupine.org:/home/wowbject/test_data/
