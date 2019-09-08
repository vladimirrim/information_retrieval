import base64
import re

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set()
from collections import defaultdict
from bs4 import BeautifulSoup as Soup


class Document:
    def __init__(self, docURL):
        self.docURL = docURL
        self.wordsCount = 0
        self.bytesCount = 0
        self.textToHTMLRatio = 0


def processFile(filename):
    with open(filename, 'rb') as f:
        decoded = f.read().decode('cp1251')
        soup = Soup(decoded, 'xml')
        docs = []
        for doc in soup.find_all('document'):
            try:
                url = base64.b64decode(doc.docURL.text).decode('cp1251')
                document = Document(url)
                graph[url] = []
                content = base64.b64decode(doc.content.text).decode('cp1251')
                htmlSize = len(content.encode('utf-8'))
                contentSoup = Soup(content, 'lxml')
                augmentGraph(graph, contentSoup, url)
                s = getContent(contentSoup)
                docs.append(gatherStats(document, s, htmlSize))
            except Exception as e:
                print(e)
        return docs


def augmentGraph(graph, contentSoup, url):
    for next in contentSoup.find_all('a'):
        if 'href' in next.attrs and next['href'].startswith('http'):
            graph[url].append(next['href'])


def getContent(contentSoup):
    s = contentSoup.get_text()
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


if __name__ == '__main__':
    prefix = '../byweb_for_course/byweb.'
    suffix = '.xml'
    graph = defaultdict(list)
    docs = []
    for i in range(10):
        docs += processFile(prefix + str(i) + suffix)
    print('Documents Count: ' + str(len(docs)))
    print('Mean Words Count: ' + str(np.mean([doc.wordsCount for doc in docs])))
    print('Mean Bytes Count: ' + str(np.mean([doc.bytesCount for doc in docs])))
    print('Mean Text to Html Ratio: ' + str(np.mean([doc.textToHTMLRatio for doc in docs])))
    plotStats([doc.wordsCount for doc in docs], 'wordsCount.png')
    plotStats([doc.bytesCount for doc in docs], 'bytesCount.png')
