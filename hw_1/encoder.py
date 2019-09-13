import base64
import re
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import csv
import math
from urllib.parse import urljoin
from itertools import chain
from multiprocessing.pool import Pool
from multiprocessing import Manager
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
    wordsFull = re.findall(r'\w+', s)
    m = Mystem()
    words = np.array([])

    # for w in wordsFull[:10]:
    for w in wordsFull:
        lemmas = np.array(m.lemmatize(w))
        words = np.append(words, lemmas[lemmas != "\n"])

    uniqueWords = np.unique(words)
    isInStopWords = lambda word: word in stopWords

    wordsCount = len(words)
    bytesCount = len(s.encode('utf-8'))
    stopWordsCount = 0
    latWordsCount = 0
    wordsLenSum = 0

    for word in words:
        stat = dictionary.get(word, DictionaryStat())
        stat.cf += 1
        dictionary[word] = stat

        stopWordsCount += 1 if isInStopWords(word) else 0
        latWordsCount += 1 if isLat(word) else 0
        wordsLenSum += len(word)
    for word in uniqueWords:
        stat = dictionary.get(word, DictionaryStat())
        stat.df += 1
        dictionary[word] = stat

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


def readStopWordsForLanguage(lang, words):
    with open("../../stopwords/" + lang, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            words.add(row[0])


def readStopWords():
    words = set()
    readStopWordsForLanguage("russian", words)
    readStopWordsForLanguage("english", words)

    return words


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


def plotWordsRank(cfTop):
    plt.clf()
    x = [math.log10(i) for i in range(len(cfTop))]
    y = [math.log10(stat[1]) for stat in cfTop]
    plt.plot(x, y)
    plt.xlabel("log10(rank)")
    plt.ylabel("log10(cf)")
    plt.savefig('wordsRank.png')


dictionary = None
stopWords = readStopWords()

def init(args):
    global dictionary
    dictionary = args

def processFileBinded(i):
    global dictionary
    global stopWords
    return processFile(i, stopWords, dictionary)


if __name__ == '__main__':
    manager = Manager()
    dictionary = manager.dict()

    with Pool(5, initializer=init, initargs=(dictionary, )) as p:
        docs = p.map(processFileBinded, range(10))
        docs = list(chain(*docs))
    # docs = processFileBinded(0)
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

    topCnt = 10

    dictItems = np.array(list([(item[0], item[1].cf, item[1].df) for item in dictionary.items()]),
                         dtype=[('word', object), ('cf', int), ('df', int)])
    cfStats = np.argsort(dictItems, order='cf')
    dfStats = np.argsort(dictItems, order='df')
    cfTop = dictItems[cfStats][-topCnt:][::-1]
    cfTail = dictItems[cfStats][:topCnt]
    dfTop = dictItems[dfStats][:topCnt]
    dfTail = dictItems[dfStats][-topCnt:][::-1]
    idfTop = [(item[0], docsCount / item[2]) for item in dfTop]
    idfTail = [(item[0], docsCount / item[2]) for item in dfTail]

    print('CF Top: ')
    print(cfTop)
    print('CF Tail: ')
    print(cfTail)
    print('IDF Top: ')
    print(idfTop)
    print('IDF Tail: ')
    print(idfTail)

    plotStats([doc.wordsCount for doc in docs], 'wordsCount.png')
    plotStats([doc.bytesCount for doc in docs], 'bytesCount.png')
    writeGraphToFile(graph)
    write_sites_graph(graph)
    plotWordsRank(cfTop)
    plotWordsRank(dictItems[cfStats][::-1])
