#!/bin/sh

SEEDS_PATH="./scripts/seeds"
PYTHON_FILES=$(ls $SEEDS_PATH/*.py 2>/dev/null)
if [ -z "$PYTHON_FILES" ]; then
    echo "No Python files found in $SEEDS_PATH"
    exit 1
fi
for seed in $PYTHON_FILES; do
    echo "Running $seed..."
    python "$seed"
    echo ''
done
