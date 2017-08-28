import csv
from pprint import pprint


def main():
    with open("outputs/rand_100_30pc.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        general_counter = 0
        # ofdp_counter = 0
        ilp_counter = 0
        splitpath_counter = 0
        ofdp3_counter = 0

        splitpath_hops_histogram = {}
        ofdp3_hops_histogram = {}

        splitpath_diff = []
        ofdp3_diff = []

        for row in reader:
            # ofdp = row["ofdp"]
            ilp = row["ilp"]
            splitpath = row["splitpath"]
            ofdp3 = row["ofdp3"]

            # hops_ofdp = row["hops_ofdp"]
            hops_ilp = row["hops_ilp"]
            hops_splitpath = row["hops_splitpath"]
            hops_ofdp3 = row["hops_ofdp3"]

            # if ofdp != "None":
            #     ofdp = float(ofdp)
            if ilp != "None":
                ilp = float(ilp)
            if splitpath != "None":
                splitpath = float(splitpath)
            if ofdp3 != "None":
                ofdp3 = float(ofdp3)

            general_counter += 1
            # if ofdp != "None":
            #     ofdp_counter += 1
            if ilp != "None":
                ilp_counter += 1
                if splitpath != "None":
                    if splitpath == ilp:
                        splitpath_counter += 1
                    else:
                        if hops_splitpath in splitpath_hops_histogram:
                            splitpath_hops_histogram[hops_splitpath] += 1
                        else:
                            splitpath_hops_histogram[hops_splitpath] = 1
                        splitpath_diff.append((splitpath - ilp) / ilp)
                if ofdp3 != "None":
                    if ofdp3 == ilp:
                        ofdp3_counter += 1
                    else:
                        if hops_ofdp3 in ofdp3_hops_histogram:
                            ofdp3_hops_histogram[hops_ofdp3] += 1
                        else:
                            ofdp3_hops_histogram[hops_ofdp3] = 1
                        ofdp3_diff.append((ofdp3 - ilp) / ilp)

        print general_counter, ilp_counter, splitpath_counter, ofdp3_counter
        print sum(splitpath_diff) / len(splitpath_diff), sum(ofdp3_diff) / len(ofdp3_diff)
        pprint(splitpath_hops_histogram)
        pprint(ofdp3_hops_histogram)




if __name__ == "__main__":
    main()
