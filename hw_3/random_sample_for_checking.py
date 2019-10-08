#!/usr/bin/python

import sys
import random

def random_sample_for_checking():
    in_filename = sys.argv[1]
    out_filename = sys.argv[1].split(".")[0] + "_checking.txt"
    if len(sys.argv) > 2:
        n = int(sys.argv[2])
    else:
        n = 10000
    with open(in_filename) as in_file, open(out_filename, "w") as out_file:
        lines = in_file.readlines()
        random.Random(3264).shuffle(lines)
        out_file.write("".join(lines[:n]))
        

def main():
    print("Started sampling\n")
    random_sample_for_checking()

if __name__== "__main__":
  main()

