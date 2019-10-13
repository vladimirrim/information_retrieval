#!/usr/bin/python

import sys

def add_ranking():
    test_filename = sys.argv[1]
    ranking_filename = sys.argv[2]
    test_with_ranking_filename = test_filename + ".final_ranking_" + ranking_filename[2:].split("_")[0]
    print(test_filename)
    print(ranking_filename)
    print(test_with_ranking_filename)
    with open(test_filename) as test_file, open(ranking_filename) as ranking_file, open(test_with_ranking_filename, "w") as test_with_ranking_file:
        test_lines = test_file.readlines()
        ranking_lines = ranking_file.readlines()
        rank_by_line = {}
        for line in ranking_lines:
            split = line.split(" ")
            rank_by_line[split[2].split("=")[1]] = split[3]
        for i, line in enumerate(test_lines):
            new_line = rank_by_line[str(i)] + line[2:]
            test_with_ranking_file.write(new_line)


def main():
    print("Started adding ranking...")
    add_ranking()

if __name__== "__main__":
  main()

