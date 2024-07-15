#!/bin/bash

# this parameter only impacts STD MEDIAN SUM and AVG queries
higher_than_zero="False"

for dataset in "PCD MTD"
do
	python3 compute_aggregates.py "$dataset" "$higher_than_zero"
	echo "Done for $dataset $higher_than_zero"
done

