import csv
from pprint import pprint
from math import sqrt

def standard_deviation(lst):
    num_items = len(lst)
    mean = sum(lst) / num_items
    differences = [x - mean for x in lst]
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)
    variance = ssd / num_items
    sd = sqrt(variance)
    return sd

def print_statistics(input_file_name, output_file=None):
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
        print sum(splitpath_diff) / len(splitpath_diff) * 100,
    else:
        print 0,
    print standard_deviation(splitpath_diff)

def get_error_list(input_file_name):
    error_list = []
    with open(input_file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ilp = row["ilp"]
            splitpath = row["splitpath"]
            if ilp != "None" and splitpath != "None":
                ilp = float(ilp)
                splitpath = float(splitpath)
                error = (splitpath - ilp)/ilp
                error_list.append(error)
    return error_list

def model_evaluation(input_file_name, output_file=None):
    def to_float(s):
        if s == "None":
            return None
        return float(s)

    with open(input_file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        md_count = 0
        mg_count = 0
        di_count = 0
        gr_count = 0
        for row in reader:
            md = to_float(row["ilp"])
            mg = to_float(row["ilpmg"])
            di = to_float(row["ilpdi"])
            gr = to_float(row["ilpgr"])
            if md is not None:
                md_count += 1
                if mg is not None:
                    err = (mg - md) / md
                    output_file.write("Multigraph\t" + str(err) + "\n")
                    if err == 0:
                        md_count += 1
                # else:
                #     mg_count += 1
                if di is not None:
                    err = (di - md) / md
                    output_file.write("Digraph\t" + str(err) + "\n")
                    if err == 0:
                        md_count += 1
                # else:
                #     di_count += 1
                if gr is not None:
                    err = (gr - md) / md
                    output_file.write("Graph\t" + str(err) + "\n")
                    if err == 0:
                        md_count += 1
                # else:
                #     gr_count += 1
        print md_count, mg_count, di_count, gr_count
        print float(mg_count)/md_count, float(di_count)/md_count, float(gr_count)/md_count

def splitpath_evaluation(input_file_name, output_file=None):
    def to_float(s):
        if s == "None":
            return None
        return float(s)

    with open(input_file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        ilp_count = 0
        md_count = 0
        mg_count = 0
        di_count = 0
        gr_count = 0
        for row in reader:
            ilp = to_float(row["ilp"])
            # md = to_float(row["splitpath"])
            mg = to_float(row["splitpathmg"])
            di = to_float(row["splitpathdi"])
            gr = to_float(row["splitpathgr"])
            if ilp is not None:
                ilp_count += 1
                # if md is not None:
                #     err = (md - ilp) / ilp
                #     output_file.write("Multidigraph\t" + str(err) + "\n")
                #     if err == 0:
                #         md_count += 1
                if mg is not None:
                    err = (mg - ilp) / ilp
                    output_file.write("Multigraph\t" + str(err) + "\n")
                    if err == 0:
                        mg_count += 1
                # else:
                #     mg_count += 1
                if di is not None:
                    err = (di - ilp) / ilp
                    output_file.write("Digraph\t" + str(err) + "\n")
                    if err == 0:
                        di_count += 1
                # else:
                #     di_count += 1
                if gr is not None:
                    err = (gr - ilp) / ilp
                    output_file.write("Graph\t" + str(err) + "\n")
                    if err == 0:
                        gr_count += 1
                # else:
                #     gr_count += 1
        # print md_count, mg_count, di_count, gr_count
        # print float(mg_count)/md_count, float(di_count)/md_count, float(gr_count)/md_count
        print ilp_count, mg_count, di_count, gr_count
        # print float(md_count)/ilp_count
        print float(mg_count)/ilp_count, float(di_count)/ilp_count, float(gr_count)/ilp_count



def main():
    # filenames = ["outputs/graph_weighted_100_495.csv",
    #              "outputs/graph_weighted_100_1485.csv",
    #              "outputs/graph_weighted_100_2475.csv",
    #              "outputs/graph_weighted_100_3465.csv",
    #              "outputs/graph_weighted_100_4455.csv"]
    # filenames = ["outputs/digraph_weighted_10_13_1.csv",
    #             "outputs/digraph_weighted_20_57_1.csv",
    #             "outputs/digraph_weighted_30_130_1.csv",
    #             "outputs/digraph_weighted_40_234_1.csv",
    #             "outputs/digraph_weighted_50_367_1.csv",
    #             "outputs/digraph_weighted_60_531_1.csv",
    #             "outputs/digraph_weighted_70_724_1.csv",
    #             "outputs/digraph_weighted_80_948_1.csv",
    #             "outputs/digraph_weighted_90_1201_1.csv",
    #             "outputs/digraph_weighted_100_1485_1.csv"]
    # filenames = ["outputs/digraph_weighted_100_1485_1.csv",
    #             "outputs/digraph_weighted_100_2475_1.csv",
    #             "outputs/digraph_weighted_100_3465_1.csv",
    #             "outputs/digraph_weighted_100_4455_1.csv",
    #             "outputs/digraph_weighted_100_495_1.csv"]
    # labels = ["10%", "30%", "50%", "70%", "90%"]
    # labels = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
    filenames=["outputs/testbed-evaluation-sps.csv"]
    output_file = open("data-heuristic-evaluation-sps.tsv", "w")
    for i in range(len(filenames)):
        filename = filenames[i]
        # label = labels[i]
        # # print_statistics(filename, output_file)
        # error_list = get_error_list(filename)
        # for error in error_list:
        #     output_file.write("\"" + label + "\"\t" + str(error) + "\n")
        splitpath_evaluation(filename, output_file)

if __name__ == "__main__":
    main()
