#!/bin/bash
set -x # print each command before executing

rm *.png

# Counter examples for twofast+DPSP

# Different results found on instance  1158 6 7
# [['ilp', 6.0], ['twofast', 7.0]]
# Different results found on instance  2654 4 6
# [['ilp', 6.0], ['twofast', 7.0]]
# Different results found on instance  2977 3 4
# [['ilp', 8.0], ['twofast', None]]
# Different results found on instance  2997 3 4
# [['ilp', 8.0], ['twofast', None]]
# Different results found on instance  3007 3 4
# [['ilp', 8.0], ['twofast', None]]
# Different results found on instance  3014 3 4
# [['ilp', 8.0], ['twofast', None]]
# Different results found on instance  3249 2 4
# [['ilp', 6.0], ['twofast', 8.0]]
# Different results found on instance  3249 3 4
# [['ilp', 6.0], ['twofast', 8.0]]
# Different results found on instance  3258 2 4
# [['ilp', 6.0], ['twofast', 8.0]]
# Different results found on instance  3258 3 4
# [['ilp', 6.0], ['twofast', 8.0]]
# Different results found on instance  3267 3 4
# [['ilp', 6.0], ['twofast', 8.0]]
# Different results found on instance  3279 3 4
# [['ilp', 6.0], ['twofast', 8.0]]
# Different results found on instance  3319 3 4
# [['ilp', 6.0], ['twofast', 8.0]]


python main.py -i inputs/graphs$1 -a ilp-oddcycle -t 2977-3-4 -v -d -s # with $1 == 8
