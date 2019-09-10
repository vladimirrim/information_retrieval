import base64
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import csv
from urllib.parse import urljoin
from itertools import chain
from multiprocessing.pool import Pool
from collections import defaultdict
from bs4 import BeautifulSoup as Soup
from pymystem3 import Mystem
from threading import Lock
from tqdm import tqdm

sns.set()


class DictionaryStat:
    def __init__(self):
        self.cf = 0
        self.df = 0


class Document:
    def __init__(self, docURL):
        self.docURL = docURL
        self.wordsCount = 0
        self.bytesCount = 0
        self.textToHTMLRatio = 0
        self.stopWordsCount = 0
        self.latWordsCount = 0
        self.wordsLenSum = 0
        self.hrefs = list()


def processFile(i, stopWords, dictionary):
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
                docs.append(gatherStats(document, s, htmlSize, stopWords, dictionary))
                break
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


def gatherStats(doc, s, htmlSize, stopWords, dictionary):
    wordsFull = s.split()
    m = Mystem()
    words = [l
             for w in wordsFull[:10]
             for l in m.lemmatize(w)]
    uniqueWords = np.unique(words)
    isInStopWords = lambda word: 1 if word in stopWords else 0

    wordsCount = len(words)
    bytesCount = len(s.encode('utf-8'))
    stopWordsCount = np.sum(np.apply_along_axis(isInStopWords, 0, words))
    latWordsCount = np.sum(np.apply_along_axis(isLat, 0, words))
    wordsLenSum = np.sum(np.apply_along_axis(len, 0, words))

    gatherStats.dictLock.acquire()
    for word in words:
        dictionary[word].cf += 1
    for word in uniqueWords:
        dictionary[word].df += 1
    gatherStats.dictLock.release()

    doc.wordsCount = wordsCount
    doc.bytesCount = bytesCount
    doc.textToHTMLRatio = bytesCount / htmlSize
    doc.stopWordsCount = stopWordsCount
    doc.latWordsCount = latWordsCount
    doc.wordsLenSum = wordsLenSum

    return doc


gatherStats.dictLock = Lock()


def isLat(word):
    englishCheck = re.compile(r'[a-z]')
    isMatch = englishCheck.match(word)

    return 1 if isMatch else 0


def plotStats(stats, filename):
    sns.distplot(stats)
    plt.savefig(filename)
    plt.close()


def readStopWords():
    words = set()

    with open("../../stopwords/russian") as f:
        reader = csv.reader(f)
        for row in reader:
            words.add(row[0])

    return words


def writeGraphToFile(graph):
    with open("./graph.csv", "w") as f:
        for site, hrefs in graph.items():
            for href in hrefs:
                f.write(site)
                f.write(';')
                f.write(href)
                f.write('\n')


dictionary = defaultdict(DictionaryStat)
stopWords = readStopWords()


def processFileBinded(i):
    return processFile(i, stopWords, dictionary)


if __name__ == '__main__':
    dictionary = defaultdict(DictionaryStat)
    stopWords = readStopWords()
    processFileBinded = lambda i: processFile(i, stopWords, dictionary)
    with Pool(5) as p:
        docs = p.map(processFileBinded, range(10))
        docs = list(chain(*docs))
    graph = defaultdict(list)
    for doc in docs:
        for href in doc.hrefs:
            graph[doc.docURL].append(href)

    docsCount = len(docs)
    wordsCount = np.sum([doc.wordsCount for doc in docs])
    print('Documents Count: ' + str(docsCount))
    print('Mean Words Count: ' + str(np.mean([doc.wordsCount for doc in docs])))
    print('Mean Bytes Count: ' + str(np.mean([doc.bytesCount for doc in docs])))
    print('Mean Text to Html Ratio: ' + str(np.mean([doc.textToHTMLRatio for doc in docs])))

    print('Stop Words Rate: ' + str(np.sum([doc.stopWordsCount for doc in docs]) / wordsCount))
    print('Average Words Length In The Collection: ' + str(np.sum([doc.wordsLenSum for doc in docs]) / wordsCount))
    print('Average Words Length In The Dictionary: ' + str(np.sum([len(word) for word in dictionary.keys()])
                                                           / len(dictionary)))
    print('Latin Words Rate: ' + str(np.sum([doc.latWordsCount for doc in docs])
                                     / wordsCount))

    dictItems = np.array(list(dictionary.items()), dtype=[('word', 'S'), ('cf', 'int'), ('df', 'int')])
    cfStats = np.argsort(dictItems, order='cf')
    dfStats = np.argsort(dictItems, order='df')

    print('CF Top: ')
    print(dictItems[cfStats][:10])
    print('CF Tail: ')
    print(dictItems[cfStats][-10:])
    print('IDF Top: ')
    print(dictItems[dfStats][-10:])
    print('IDF Tail: ')
    print(dictItems[dfStats][:10])

    plotStats([doc.wordsCount for doc in docs], 'wordsCount.png')
    plotStats([doc.bytesCount for doc in docs], 'bytesCount.png')
    writeGraphToFile(graph)
