#!/bin/bash

set -e
set -x

for dir in lists/*/list.json
do
    cat ${dir} | jq . | tee ${dir}
done
