#!/usr/bin/python

import sys

def add_line_comment():
    test_filename = sys.argv[1]
    line_comment_filename = test_filename + ".added_line_comment"
    with open(test_filename) as test_file, open(line_comment_filename, "w") as line_comment_file:
        test_lines = test_file.readlines()
        for i, line in enumerate(test_lines):
            new_line = line.split("\n")[0] + " #line=" + str(i) + "\n"
            line_comment_file.write(new_line)


def main():
    print("Started adding...")
    add_line_comment()

if __name__== "__main__":
  main()

