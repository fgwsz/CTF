#!/bin/bash
root_path=$(dirname "$(readlink -f "$0")")
java -jar "$root_path/StegSolve-1.5-alpha1.jar"
