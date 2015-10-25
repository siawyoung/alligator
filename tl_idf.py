#-*- coding: utf-8 -*-

import os
javapath = "/Users/vuhuyle/workspace/stanford-postagger-2015-04-20/stanford-postagger.jar"
os.environ['CLASSPATH'] = javapath
# print os.environ['CLASSPATH']
# print os.environ['PATH']

import re
import nltk
from nltk.tokenize import RegexpTokenizer, TweetTokenizer
from nltk import bigrams, trigrams
import math
from math import log
import numpy as np



stopwords = nltk.corpus.stopwords.words('english')
#tokenizer = RegexpTokenizer("[\w’]+", flags=re.UNICODE)
#tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
tokenizer = TweetTokenizer()

def freq(word, doc):
    return doc.count(word)


def word_count(doc):
    return len(doc)


def tf(word, doc):
    return (freq(word, doc) / float(word_count(doc)))

def freq_tf(word, doc, word_count):
    _freq = doc.count(word)
    return _freq, _freq/word_count


def num_docs_containing(word, list_of_docs):
    count = 0
    for document in list_of_docs:
        if freq(word, document) > 0:
            count += 1
    return 1 + count


def idf(word, list_of_docs):
    return math.log(len(list_of_docs) /
            float(num_docs_containing(word, list_of_docs)))


def tf_idf(word, doc, list_of_docs):
    return (tf(word, doc) * idf(word, list_of_docs))

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def make_matrices(search_results):
    #Compute the frequency for each term.
    threshold = 3
    limit = 50
    vocabulary = {}
    docs = {}
    all_tips = []
    labels = {}

    for result, content in search_results:
        url = result['url']
        try:
            labels[url] += 1
            continue
        except:
            docs[url] = {}
            labels[url] = 1

        tokens = tokenizer.tokenize(content)

        # bi_tokens = bigrams(tokens)
        # tri_tokens = trigrams(tokens)
        
        tokens = [token.lower() for token in tokens if len(token) > 2]
        tokens = [token for token in tokens if token not in stopwords and not is_number(token)]

        # bi_tokens = [' '.join(token).lower() for token in bi_tokens]
        # bi_tokens = [token for token in bi_tokens if token not in stopwords]

        # tri_tokens = [' '.join(token).lower() for token in tri_tokens]
        # tri_tokens = [token for token in tri_tokens if token not in stopwords]

        final_tokens = []
        final_tokens.extend(tokens)
        # final_tokens.extend(bi_tokens)
        # final_tokens.extend(tri_tokens)
        # docs[tip] = {'freq': {}, 'tf': {}, 'idf': {},
                            # 'tf-idf': {}, 'tokens': []}
        

        for token in final_tokens:
            try:
                docs[url][token]
                continue
            except:
                f = freq(token, final_tokens)
                # tf = 1 + math.log(freq(token, final_tokens))
                tf = 1 + log(f)
                docs[url][token] = {'tf': tf}
                # docs[url][token]['tf'] = freq(token, final_tokens)
                # docs[tip][token]['freq'], docs[tip][token]['tf'] = freq_tf(token, final_tokens)
            try:
                vocabulary[token] += 1
            except:
                vocabulary[token] = 1

    # print docs
    # print vocabulary
    # important = [word for word, count in vocabulary.iteritems() if count > 1]
    # print important

    doc_count = len(docs)
    sorted_docs = {}
    top_vocabs = {}
    # print doc_count
    for url, doc in docs.iteritems():
        for token, value in doc.iteritems():
            idf = math.log(doc_count / vocabulary[token])
            #value['idf'] = math.log(doc_count / vocabulary[token])
            value['idf'] = 1
            value['tf-idf'] = value['tf'] * value['idf']
        sorted_doc_array = sorted(doc.items(), key=lambda value: -value[1]['tf-idf'])[:limit]
        sorted_doc = {}
        for token, value in sorted_doc_array:
            sorted_doc[token] = value
            top_vocabs[token] = -1
        sorted_docs[url] = sorted_doc

    matrix = []

    top_vocabs = top_vocabs.keys()
    for token in top_vocabs:
        row = []
        urls = []
        labelsArray = []
        for url, sorted_doc in sorted_docs.iteritems():
            urls.append(url)
            labelsArray.append(labels[url])
            try:
                row.append(sorted_doc[token]['tf-idf'])
            except:
                row.append(0)
        matrix.append(row)
    matrix = np.matrix(matrix)
    top_vocabs_col = np.matrix(top_vocabs).T
    labelsArray = np.matrix(labelsArray).T
    urls = np.matrix(urls)

    print urls.shape
    print top_vocabs_col.shape
    print matrix.shape
    print labelsArray.shape

    return urls, top_vocabs_col, matrix, labelsArray

        #doc.sort(key = lambda token: doc[token]['tf-idf'])
    # for doc in docs:
    #     for token in docs[doc]['tf']:
    #         #The Inverse-Document-Frequency
    #         docs[doc]['idf'][token] = idf(token, vocabulary)
    #         #The tf-idf
    #         docs[doc]['tf-idf'][token] = tf_idf(token, docs[doc]['tokens'], vocabulary)

    # print docs

    # #Now let's find out the most relevant words by tf-idf.
    # words = {}
    # for doc in docs:
    #     for token in docs[doc]['tf-idf']:
    #         if token not in words:
    #             words[token] = docs[doc]['tf-idf'][token]
    #         else:
    #             if docs[doc]['tf-idf'][token] > words[token]:
    #                 words[token] = docs[doc]['tf-idf'][token]

    #     print doc
    #     for token in docs[doc]['tf-idf']:
    #         print token, docs[doc]['tf-idf'][token]

    # for item in sorted(words.items(), key=lambda x: x[1], reverse=True):
    #     print "%f <= %s" % (item[1], item[0])