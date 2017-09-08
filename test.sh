#!/bin/bash
set -x # print each command before executing

rm *.png
# python main.py -i test$1_topology -p test$1_positions -a ofdp -v
# python main.py -i inputs/graphs$1 -a ilp-oddcycle
# python main.py -i inputs/graphs$1 -a ilp-dpsp -t 85-6-7 -v -d -s
# python main.py -i inputs/graphs$1 -a ilp-twofast -t 2193-1-4 -v -d -s
# python main.py -i inputs/graphs$1 -a ilp-twofast -t 61-0-7 -v -d -s
# python main.py -i inputs/graphs$1 -a ilp-twofast -t 155-0-2 -v -d -s
# python main.py -i inputs/graphs$1 -a ilp-oddcycle -t 3249-2-4 -v -d -s
# python main.py -i inputs/graphs$1 -a ilp-oddcycle -t 2660 -d
# python main.py -i inputs/graphs$1 -a ilp-oddcycle -t 2899-0-3 -v -d -s
# python main.py -i inputs/graphs$1 -a ilp-oddcycle -t 0-3-4 -v -d -s

# python main.py -i inputs/graphs$1 -a ilp-splitpath -t 155-0-7 -v -d
# python main.py -i inputs/graphs$1 -a ilp-splitpath

# python main.py -i topology -a ofdp-ilp-splitpath-ofdp3 -o results_4.csv

# python main.py -i inputs/graph_weighted_100_495 -a ofdp3 -t 0-1-27 -v -d
# python main.py -i inputs/graph_weighted_100_495 -a ofdp3 -t 0-1-27

# python main.py -i inputs/digraph_weighted_10_13_1 -a ilp-splitpath
# python main.py -i inputs/digraph_weighted_20_57_1 -a ilp-splitpath
# python main.py -i inputs/digraph_weighted_30_130_1 -a ilp-splitpath
# python main.py -i topology -a ilp-splitpath -o outputs/testbed-evaluation.csv
# python main.py -i topology -a ilp-splitpathmg-splitpathdi-splitpathgr -o outputs/testbed-evaluation-sps.csv
python main.py -i topology -a ilp-ilpmg-ilpdi-ilpgr -o outputs/model-evaluation-all-2.csv
