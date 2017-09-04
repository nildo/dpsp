import csv
from pprint import pprint


def print_statistics(input_file_name):
    with open(input_file_name) as csvfile:
        reader = csv.DictReader(csvfile)

        general_counter = 0
        # ofdp_counter = 0
        ilp_counter = 0
        splitpath_counter = 0
        # ofdp3_counter = 0

        # splitpath_hops_histogram = {}
        # ofdp3_hops_histogram = {}

        splitpath_diff = []
        # ofdp3_diff = []

        for row in reader:
            # ofdp = row["ofdp"]
            ilp = row["ilp"]
            splitpath = row["splitpath"]
            # ofdp3 = row["ofdp3"]

            # hops_ofdp = row["hops_ofdp"]
            hops_ilp = row["hops_ilp"]
            hops_splitpath = row["hops_splitpath"]
            # hops_ofdp3 = row["hops_ofdp3"]

            # if ofdp != "None":
            #     ofdp = float(ofdp)
            if ilp != "None":
                ilp = float(ilp)
            if splitpath != "None":
                splitpath = float(splitpath)
            # if ofdp3 != "None":
            #     ofdp3 = float(ofdp3)

            general_counter += 1
            # if ofdp != "None":
            #     ofdp_counter += 1
            if ilp != "None":
                ilp_counter += 1
                if splitpath != "None":
                    if splitpath == ilp:
                        splitpath_counter += 1
                    # else:
                    #     if hops_splitpath in splitpath_hops_histogram:
                    #         splitpath_hops_histogram[hops_splitpath] += 1
                    #     else:
                    #         splitpath_hops_histogram[hops_splitpath] = 1
                    splitpath_diff.append((splitpath - ilp) / ilp)
                # if ofdp3 != "None":
                #     if ofdp3 == ilp:
                #         ofdp3_counter += 1
                #     else:
                #         if hops_ofdp3 in ofdp3_hops_histogram:
                #             ofdp3_hops_histogram[hops_ofdp3] += 1
                #         else:
                #             ofdp3_hops_histogram[hops_ofdp3] = 1
                #         ofdp3_diff.append((ofdp3 - ilp) / ilp)

    # print general_counter, ilp_counter, splitpath_counter, ofdp3_counter
    # print sum(splitpath_diff) / len(splitpath_diff) * 100, sum(ofdp3_diff) / len(ofdp3_diff) * 100
    # pprint(splitpath_hops_histogram)
    # pprint(ofdp3_hops_histogram)
    # print float(splitpath_counter) / ilp_counter * 100,
    # print float(ofdp3_counter) / ilp_counter * 100
    print general_counter, ilp_counter, splitpath_counter,
    print float(splitpath_counter) / ilp_counter * 100,
    if len(splitpath_diff) > 0:
        print sum(splitpath_diff) / len(splitpath_diff) * 100
    else:
        print 0

def main():
    # filenames = ["outputs/graph_weighted_100_495.csv",
    #              "outputs/graph_weighted_100_1485.csv",
    #              "outputs/graph_weighted_100_2475.csv",
    #              "outputs/graph_weighted_100_3465.csv",
    #              "outputs/graph_weighted_100_4455.csv"]
    filenames = ["outputs/digraph_weighted_100_1485_1.csv",
                "outputs/digraph_weighted_10_13_1.csv",
                "outputs/digraph_weighted_20_57_1.csv",
                "outputs/digraph_weighted_30_130_1.csv",
                "outputs/digraph_weighted_40_234_1.csv",
                "outputs/digraph_weighted_50_367_1.csv",
                "outputs/digraph_weighted_60_531_1.csv",
                "outputs/digraph_weighted_70_724_1.csv",
                "outputs/digraph_weighted_80_948_1.csv",
                "outputs/digraph_weighted_90_1201_1.csv"]
    for filename in filenames:
        print_statistics(filename)

if __name__ == "__main__":
    main()
