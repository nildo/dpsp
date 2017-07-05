#!/bin/bash
set -x # print each command before executing

rm dpsp*.png
rm ofdp*.png
rm ilp*.png
# python main.py -i test$1_topology -p test$1_positions -a ofdp -v
# python main.py -i inputs/graphs$1 -a ilp-dpsp
# python main.py -i inputs/graphs$1 -a ilp-dpsp -t 2193
python main.py -i inputs/graphs$1 -a ilp-dpsp -t 2193-1-4 -v -d -s
