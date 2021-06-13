#!/bin/bash
# Replace our addon version string in __init__.py with the one specified by
# the git tag we've been passed. There's probably an action to do this, but
# I sure couldn't find it. Kinda ugly, but it'll work.

if [ -z "$1" ]; then
    echo "usage: $0 <tag>"
    exit 1
fi

echo tag: $1
tag=$1

if ! echo $tag | grep -E -q '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "error: version tag must be in the form of 'v1.2.3'"
    exit 2
fi

verstring=$(echo $tag | sed -E 's/^v([0-9]+)\.([0-9]+)\.([0-9]+)$/\1, \2, \3/')

# sanity check -- make sure our string to be replaced is in the file
if ! grep -E -q '^[ ]+\"version\".*0, 0, 0.*# autoreplace' __init__.py; then
    echo "error: replacement string placeholder not found in __init__.py"
    exit 3
fi

# this command sucks
sed -E "s/^([ ]+)\"version\".* # autoreplace.*$/\1\"version\": ( ${verstring} ),  # autoreplace/" < __init__.py > ver.tmp


# sanity check -- make sure the original string is missing now
if grep -E -q '^[ ]+\"version\".*0, 0, 0.*# autoreplace' ver.tmp; then
    echo "error: still found original replacement placeholder in __init__.py"
    rm -f ver.tmp
    exit 3
fi

mv ver.tmp __init__.py
