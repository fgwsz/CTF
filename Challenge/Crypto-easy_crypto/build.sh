#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

cd "$SCRIPT_DIR"
g++ -O2 -o solve solve.cpp
./solve
