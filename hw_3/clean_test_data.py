#!/usr/bin/python

import sys

def clean_test_data():
    train_filename = sys.argv[1]
    test_filename = sys.argv[2]
    cleaned_test_filename = test_filename + ".cleaned"
    out_filename = sys.argv[1].split(".")[0] + "_all_features.txt"
    with open(train_filename) as train_file, open(test_filename) as test_file, open(cleaned_test_filename, "w") as cleaned_test_file:
        train_lines = set(" ".join(line.split(" ")[1:]) for line in train_file.readlines())
        test_lines = test_file.readlines()
        test_lines_set = set(" ".join(line.split(" ")[1:]) for line in test_lines)
        print("...")
        diff = test_lines_set - train_lines
        cleaned_lines = [line for line in test_lines if " ".join(line.split(" ")[1:]) in diff]
        print(f'Train lines set size: {len(train_lines)}')
        print(f'Test lines set size: {len(set(test_lines))}')
        print(f'Diff: {len(diff)}')
        print(f'Before: {len(test_lines)}')
        print(f'After: {len(cleaned_lines)}')
        for cleaned_line in cleaned_lines:
            cleaned_test_file.write(cleaned_line)


def main():
    print("Started cleaning...")
    clean_test_data()

if __name__== "__main__":
  main()

