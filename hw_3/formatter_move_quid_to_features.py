#!/usr/bin/python

import sys

def add_zero_features():
    in_filename = sys.argv[1]
    out_filename = sys.argv[1].split(".")[0] + "_qid_fixed.txt"
    with open(in_filename) as in_file, open(out_filename, "w") as out_file:
        for line in in_file.readlines():
            line_split = line.split("\n")[0].split(" # ")
            line_split_2 = line_split[0].split(" ")
            out_file.write(line_split_2[0] + " qid:" + line_split[1] + " ")
            out_file.write(" ".join(line_split_2[1:]))
            out_file.write("\n")

def main():
    print("Started formatter\n")
    add_zero_features()

if __name__== "__main__":
  main()

