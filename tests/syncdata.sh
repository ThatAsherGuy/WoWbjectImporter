#!/bin/bash
# if needed you can add a `--bwlimit=X` where X is in kBps
# remove --delete if you have some custom local data you want to keep
#
# This should really only be run from the WoWbject 'tests' directory

if [ ! -d "test_data" ]; then
    echo "ERROR: 'test_data' subdirectory doesn't exist, cwd wrong?"
    exit 1
fi

rsync --recursive --links --safe-links --times \
    --verbose --progress --stats \
    --delete --delete-after \
    --compress \
    --backup --backup-dir=../test_data_old/ \
    v.lupine.org::wowbject_test_data/ test_data/
