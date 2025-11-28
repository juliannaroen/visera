#!/bin/bash
# Run backend tests from project root
set -e

cd "$(dirname "$0")/../backend" || exit 1
pdm run test "$@"

