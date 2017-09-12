# python main.py -i inputs/graph_weighted_100_495 -o outputs/graph_weighted_100_495.csv -a ilp-splitpath-ofdp3
# python main.py -i inputs/graph_weighted_100_1485 -o outputs/graph_weighted_100_1485.csv -a ilp-splitpath-ofdp3
# python main.py -i inputs/graph_weighted_100_2475 -o outputs/graph_weighted_100_2475.csv -a ilp-splitpath-ofdp3
# python main.py -i inputs/graph_weighted_100_3465 -o outputs/graph_weighted_100_3465.csv -a ilp-splitpath-ofdp3
# python main.py -i inputs/graph_weighted_100_4455 -o outputs/graph_weighted_100_4455.csv -a ilp-splitpath-ofdp3

for if in inputs/digraph_weighted_*_1;
do
  of=${if/inputs/outputs}.csv
  if [ ! -f "$of" ];
  then
    echo "Executing with -i $if -o $of"
    python main.py -i $if -o $of -a ilp-splitpath
  else
    echo "File $of already exists"
  fi
  # echo "\"$of\","
done
