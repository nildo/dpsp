#!/bin/bash

rm dpsp*.png
python main.py -i test$1_topology -p test$1_positions -a dpsp
