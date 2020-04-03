#!/bin/bash

set -e
set -x

pushd tools
python3 make_list_unique.py
popd

./jq_all_the_things.sh

diffs=`git status --porcelain | wc -l`

if ! [ $diffs -eq 0 ]; then
	echo "Please make sure you run ./jq_all_the_things.sh before commiting."
	exit 1
fi

# remove the exec flag on the json files
find -name "*.json" -exec chmod -x "{}" \;

diffs=`git status --porcelain | wc -l`

if ! [ $diffs -eq 0 ]; then
    echo "Please make sure you run remove the executable flag on the json files before commiting: find -name "*.json" -exec chmod -x \"{}\" \\;"
    exit 1
fi

# test filename
for dir in lists/*/*.json
do
    if [ `basename ${dir}` != "list.json" ]; then
        echo "Invalid filename (should be list.json): " ${dir}
        exit 1
    fi
done

for dir in lists/*/list.json
do
  echo -n "${dir}: "
  jsonschema -i ${dir} schema.json
  echo ''
done

