#!/bin/bash

set -e
set -x

# Seeds sponge, from moreutils

for dir in lists/*/list.json
do
    cat ${dir} | jq -S . | sponge ${dir}
done

cat schema.json | jq -S . | sponge schema.json
