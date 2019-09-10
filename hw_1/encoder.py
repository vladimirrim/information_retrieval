import base64
import re
from urllib.parse import urljoin
from urllib.parse import urlparse
from itertools import chain
from multiprocessing.pool import Pool

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set()
from collections import defaultdict
from bs4 import BeautifulSoup as Soup
from tqdm import tqdm

class Document:
    def __init__(self, docURL):
        self.docURL = docURL
        self.wordsCount = 0
        self.bytesCount = 0
        self.textToHTMLRatio = 0
        self.hrefs = list()


def processFile(i):
    prefix = '../byweb_for_course/byweb.'
    suffix = '.xml'
    filename = prefix + str(i) + suffix
    with open(filename, 'rb') as f:
        decoded = f.read().decode('cp1251')
        soup = Soup(decoded, 'xml')
        docs = []
        for doc in tqdm(soup.find_all('document')):
            try:
                url = base64.b64decode(doc.docURL.text).decode('cp1251')
                document = Document(url)
                content = base64.b64decode(doc.content.text).decode('cp1251')
                htmlSize = len(content.encode('utf-8'))
                contentSoup = Soup(content, 'lxml')
                augmentGraph(document, contentSoup, url)
                s = getContent(contentSoup)
                docs.append(gatherStats(document, s, htmlSize))
            except Exception as e:
                print(e)
        return docs


def augmentGraph(document, contentSoup, url):
    for next in contentSoup.find_all('a'):
        if 'href' in next.attrs:
            document.hrefs.append(urljoin(url, next['href']))


def getContent(contentSoup):
    s = contentSoup.get_text(" ")
    s = re.sub("(<!--.*?-->)", "", s, flags=re.DOTALL)
    return re.sub("(//<!\\[CDATA.*?]>)", "", s, flags=re.DOTALL)


def gatherStats(doc, s, htmlSize):
    wordsCount = len(s.split())
    bytesCount = len(s.encode('utf-8'))
    doc.wordsCount = wordsCount
    doc.bytesCount = bytesCount
    doc.textToHTMLRatio = bytesCount / htmlSize
    return doc


def plotStats(stats, filename):
    sns.distplot(stats)
    plt.savefig(filename)
    plt.close()


def writeGraphToFile(graph, file_suffix=''):
    with open("./graph{}.csv".format(file_suffix), "w") as f:
        for site, hrefs in graph.items():
            for href in hrefs:
                f.write(site)
                f.write(';')
                f.write(href)
                f.write('\n')


def url_to_domain(url):
    """
    Example:
    'http://abc.hostname.com/somethings/anything/' -> hostname.com
    """
    return '.'.join(urlparse(url).netloc.split('.')[-2:])


def reduce_to_sites_graph(graph):
    sites_graph = {}
    for site_url, hrefs in graph.items():
        site_url = url_to_domain(site_url)
        sites_graph[site_url] = list(map(lambda e: url_to_domain(e), hrefs))
    return sites_graph


def write_sites_graph(graph):
    """
    This function collapses all nodes that belong to one web-site into one node.
    And returns the graph that consists of web-sites as nodes and shows connections between web-sites.
    """
    sites_graph = reduce_to_sites_graph(graph)
    writeGraphToFile(sites_graph, "_sites")


if __name__ == '__main__':
    with Pool(5) as p:
        docs = p.map(processFile, range(10))
        docs = list(chain(*docs))
    graph = defaultdict(list)
    for doc in docs:
        for href in doc.hrefs:
            graph[doc.docURL].append(href)
    print('Documents Count: ' + str(len(docs)))
    print('Mean Words Count: ' + str(np.mean([doc.wordsCount for doc in docs])))
    print('Mean Bytes Count: ' + str(np.mean([doc.bytesCount for doc in docs])))
    print('Mean Text to Html Ratio: ' + str(np.mean([doc.textToHTMLRatio for doc in docs])))
    plotStats([doc.wordsCount for doc in docs], 'wordsCount.png')
    plotStats([doc.bytesCount for doc in docs], 'bytesCount.png')
    writeGraphToFile(graph)
    write_sites_graph(graph)
