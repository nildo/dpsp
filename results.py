import csv


def main():
    with open("results_2.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        general_counter = 0
        ofdp_counter = 0
        ilp_counter = 0
        splitpath_counter = 0
        ofdp3_counter = 0

        splitpath_diff = []
        ofdp3_diff = []

        for row in reader:
            ofdp = row["ofdp"]
            ilp = row["ilp"]
            splitpath = row["splitpath"]
            ofdp3 = row["ofdp3"]

            if ofdp != "None":
                ofdp = float(ofdp)
            if ilp != "None":
                ilp = float(ilp)
            if splitpath != "None":
                splitpath = float(splitpath)
            if ofdp3 != "None":
                ofdp3 = float(ofdp3)

            general_counter += 1
            if ofdp != "None":
                ofdp_counter += 1
            if ilp != "None":
                ilp_counter += 1
                if splitpath != "None":
                    if splitpath == ilp:
                        splitpath_counter += 1
                    else:
                        splitpath_diff.append((splitpath - ilp) / ilp)
                if ofdp3 != "None":
                    if ofdp3 == ilp:
                        ofdp3_counter += 1
                    else:
                        ofdp3_diff.append((ofdp3 - ilp) / ilp)

        print general_counter, ofdp_counter, ilp_counter, splitpath_counter, ofdp3_counter
        print sum(splitpath_diff) / len(splitpath_diff), sum(ofdp3_diff) / len(ofdp3_diff)




if __name__ == "__main__":
    main()
