#!/usr/bin/python

import sys

def add_zero_features():
    in_filename = sys.argv[1]
    out_filename = sys.argv[1].split(".")[0] + "_all_features.txt"
    with open(in_filename) as in_file, open(out_filename, "w") as out_file:
        for line in in_file.readlines():
            line_split = line.split(" ")
            out_file.write(line_split[0] + " " + line_split[1])
            j = 2
            for i in range(1, 246):
                try:
                    if (j < len(line_split) and int(line_split[j].split(":")[0]) == i):
                        out_file.write(" " + line_split[j].split("\n")[0])
                        j += 1
                    else:
                        out_file.write(" " + str(i) + ":0")
                except:
                    print(j)
                    print(len(line_split))
                    return
            out_file.write("\n")

def main():
    print("Started formatter\n")
    add_zero_features()

if __name__== "__main__":
  main()

