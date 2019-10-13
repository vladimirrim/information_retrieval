#!/usr/bin/python

import sys
import os

from collections import defaultdict
import xmltodict
import json
from tqdm import tqdm


def get_doc_id_to_url():
    docs_id_url_file_name = "./pagerank.txt"
    id_to_url = defaultdict(str)

    with open(docs_id_url_file_name) as docs_id_url_file:
        for line in tqdm(docs_id_url_file):
            tokens = line.split(" ")
            id_to_url[tokens[0] + ".json"] = tokens[1]

    return id_to_url


def get_all_docs_for_train():
    docs_dir = "../lemmatized_titles_pr_len"
    print("Getting doc id to url...")
    id_to_url = get_doc_id_to_url()
    all_docs = defaultdict(dict)

    print("Walking in docs dir...")
    for _, _, files in os.walk(docs_dir):
        for doc_filename in tqdm(files):
            try:
                with open(docs_dir + "/" + doc_filename) as doc_file:
                    doc_id = doc_filename[4:]
                    doc_url = id_to_url[doc_id]
                    doc = json.load(doc_file)
                    doc_dict = defaultdict(str)
                    doc_dict["id"] = doc_id
                    doc_dict["url"] = doc_url
                    doc_dict["title"] = doc["title"]
                    doc_dict["pagerank"] = doc["pagerank"]
                    doc_dict["urllen"] = doc["urllen"]
                    doc_dict["doclen"] = doc["doclen"]
                    doc_dict["content"] = doc["content"]

                    all_docs[doc_url] = doc_dict
            except Exception as e:
                print(e)
    print(len(all_docs.items()))
    return all_docs


def get_all_docs_for_test():
    docs_dir = "../lemmatized_titles_pr_len"
    id_to_url = get_doc_id_to_url()
    all_docs = defaultdict(dict)

    for _, _, files in os.walk(docs_dir):
        for doc_filename in tqdm(files):
            try:
                with open(docs_dir + "/" + doc_filename) as doc_file:
                    doc_id = doc_filename[4:]
                    doc_url = id_to_url[doc_id]
                    doc = json.load(doc_file)

                    doc_dict = defaultdict(str)
                    doc_dict["id"] = doc_id
                    doc_dict["url"] = doc_url
                    doc_dict["title"] = doc["title"]
                    doc_dict["pagerank"] = doc["pagerank"]
                    doc_dict["urllen"] = doc["urllen"]
                    doc_dict["doclen"] = doc["doclen"]
                    doc_dict["content"] = doc["content"]

                    all_docs[doc_id] = doc_dict
            except Exception as e:
                print(e)
    return all_docs


def get_all_queries():
    queries_filename = "./web2008_adhoc.xml"
    all_queries = defaultdict(tuple)

    with open(queries_filename, encoding='cp1251') as queries_file:
        xml_dict = xmltodict.parse(queries_file.read())
        for task in tqdm(xml_dict['task-set']['task']):
            all_queries[task['@id']] = (task['@id'][3:], task['querytext'])

    return all_queries


def get_train_query_doc_pairs():
    relevant_table_filename = "./or_relevant-minus_table.xml"

    print("Getting all docs...")
    all_docs = get_all_docs_for_train()
    print("Getting all queries...")
    all_queries = get_all_queries()
    query_doc_pairs = []

    print("Calculating features...")
    with open(relevant_table_filename) as table_file:
        xml_dict = xmltodict.parse(table_file.read())

        for query_dict in tqdm(xml_dict['taskDocumentMatrix']['task']):
            try:
                query_id = query_dict['@id']
                query = all_queries[query_id]

                for doc_dict in query_dict['document']:
                    doc_url = doc_dict['@id']
                    relevance_str = doc_dict['@relevance']
                    relevance = 1 if relevance_str == "vital" else 0
                    doc = all_docs[doc_url]
                    query_doc_pairs.append((query, doc, relevance))
            except Exception as e:
                print(e)

    return query_doc_pairs


def get_test_query_doc_pairs():
    relevant_table_filename = "./relevant_table_2009.xml"

    all_docs = get_all_docs_for_test()
    all_queries = get_all_queries()
    query_doc_pairs = []

    with open(relevant_table_filename) as table_file:
        xml_dict = xmltodict.parse(table_file.read())

        for query_dict in tqdm(xml_dict['taskDocumentMatrix']['task']):
            try:
                query_id = query_dict['@id']
                query = all_queries[query_id]

                for doc_dict in query_dict['document']:
                    doc_id = doc_dict['@id'] + ".json"
                    relevance_str = doc_dict['@relevance']
                    relevance = 1 if relevance_str == "vital" else 0
                    doc = all_docs[doc_id]
                    print(doc)
                    query_doc_pairs.append((query, doc, relevance))
            except Exception as e:
                print(e)

    return query_doc_pairs


def build_features():
    query_doc_pairs = []

    print("Getting query doc pairs...")
    dataset_type = sys.argv[1]
    if dataset_type == "train":
        query_doc_pairs = get_train_query_doc_pairs()
    elif dataset_type == "test":
        query_doc_pairs = get_test_query_doc_pairs()

    out_filename = dataset_type + "_generated_features.txt"

    with open(out_filename, "w") as out_file:
        for query, doc, relevance in tqdm(query_doc_pairs):
            try:
                features = []
                # calculate new_feature_value
                # features.append(new_feature_value)
                features.append(len(query[1]))
                features.append(doc["urllen"])
                features.append(doc["doclen"])
                features.append(doc["pagerank"])

                out_file.write(str(relevance) + " ")
                out_file.write("quid:" + query[0] + " ")
                for i, feature in enumerate(features, start=1):
                    out_file.write(str(i) + ":" + str(feature) + " ")
                out_file.write("\n")
            except Exception as e:
                continue
               #print("Exception: ")
              # print(e)


def main():
    print("Building features...")
    build_features()


if __name__ == "__main__":
    main()