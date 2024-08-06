#!/bin/bash
cd ..
python3 -u data_generator/data_generator.py >> logs/data_generator_output.log &
