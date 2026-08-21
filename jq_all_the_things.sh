#!/bin/bash
set -eux
set -o pipefail

# Seeds sponge, from moreutils
(
    trap 'kill 0' SIGINT

    for dir in lists/*/list.json
    do
        jq -S . "$dir" | sponge "$dir" &
    done
    
    jq -S . schema.json | sponge schema.json &
)

wait
