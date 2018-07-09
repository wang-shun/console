#!/bin/bash

DIFFS="$(git diff --name-status --no-renames HEAD^..HEAD | grep -v -E "^D" | grep -v -E "/migrations/.*\.py" | grep -E "\.py$"|cut -f 2)"
LINT="$(which flake8)"
OPTS="--config=.flake8"
ERRNO=0

if [[ -n ${DIFFS} ]]; then
    echo "checking these file(s):"
    for filename in ${DIFFS}; do
        echo "${filename}"
    done
    ${LINT} ${OPTS} ${DIFFS}
    ERRNO=$?
else
    echo "ignore this commit"
fi

exit ${ERRNO}
