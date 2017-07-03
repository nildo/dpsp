#!/bin/bash
set -x # print each command before executing

rm dpsp*.png
rm ofdp*.png
# python main.py -i test$1_topology -p test$1_positions -a ofdp -v
python main.py -i inputs/graphs$1 -a dpsp -t 10-10 -v
