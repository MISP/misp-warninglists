#!/bin/bash
set -eux
set -o pipefail

# Seeds sponge, from moreutils
(
    trap 'kill 0' SIGINT

    for dir in lists/*/list.json
    do
        cat ${dir} | jq -S . | sponge ${dir} &
    done
    
    cat schema.json | jq -S . | sponge schema.json &
)

wait
