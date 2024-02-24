from konlpy.tag import Kkma, Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from hanspell import spell_checker
import numpy as np
import re

class SentenceNomalize():
    def __init__(self):
        self.okt = Okt()
        self.hanpattern = '([ㄱ-ㅎㅏ-ㅣ]+)'
        self.signpattern = '[^\w\s]'
        self.repl = ''
    
    def sent_nomalize(self, sentence):
        # 이상한 받침 제거
        sentence = self.okt.normalize(sentence)
        # 한글 자음, 모음 제거
        sentence = re.sub(pattern=self.hanpattern, repl=self.repl, string=sentence)
        # 특수 기호 제거
        sentence = re.sub(pattern=self.signpattern, repl=self.repl, string=sentence)
        # 맞춤법 수정
        sentence = spell_checker.check(sentence).checked
        
        return sentence

class SentenceTokenizer():
    def __init__(self):
        self.okt = Okt()
        self.replace_dict = {"\n": ".", "!": ".", "?": "."}
        self.text_nomalize = SentenceNomalize()
        # self.stopwords = stopword

    def get_text(self, content):
        content = content.translate(str.maketrans(self.replace_dict))
        sentences = content.rsplit('.')
        idx = 0
        while idx < len(sentences):
            # 빈 문자열 제거
            if sentences[idx] == '':
                del sentences[idx]
            else:
                self.text_nomalize.sent_nomalize(sentences[idx])
                idx += 1
        
        return sentences

    def get_nouns(self, sentences):
        nouns = []
        for sentence in sentences:
            if sentence != '':
                nouns.append(' '.join([noun for noun in self.okt.nouns(str(sentence))]))
        
        return nouns

class GraphMatrix(object):
    def __init__(self):
        self.tfidf = TfidfVectorizer()
        self.cnt_vec = CountVectorizer()
        self.graph_sentence = []
        
    # 문장별 가중치 그래프 생성
    def build_sent_graph(self, sentence):
        tfidf_mat = self.tfidf.fit_transform(sentence).toarray()
        self.graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
        return  self.graph_sentence
        
    # 단어별 가중치 그래프 생성
    def build_words_graph(self, sentence):
        cnt_vec_mat = normalize(self.cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
        vocab = self.cnt_vec.vocabulary_
        return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word] : word for word in vocab}

class Rank(object):
    def get_ranks(self, graph, d=0.85): # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0 # diagonal 부분을 0으로 
            link_sum = np.sum(A[:,id]) # A[:, id] = A[:][id]
            if link_sum != 0:
                A[:, id] /= link_sum
            A[:, id] *= -d
            A[id, id] = 1
            
        B = (1-d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(A, B) # 연립방정식 Ax = b
        return {idx: r[0] for idx, r in enumerate(ranks)}

class TextRank(object):
    def __init__(self, content):
        self.sent_tokenize = SentenceTokenizer()
        
        self.sentences = self.sent_tokenize.get_text(content)
        
        self.nouns = self.sent_tokenize.get_nouns(self.sentences)
                    
        self.graph_matrix = GraphMatrix()
        self.sent_graph = self.graph_matrix.build_sent_graph(self.nouns)
        self.words_graph, self.idx2word = self.graph_matrix.build_words_graph(self.nouns)
        
        self.rank = Rank()
        self.sent_rank_idx = self.rank.get_ranks(self.sent_graph)
        self.sorted_sent_rank_idx = sorted(self.sent_rank_idx, key=lambda k: self.sent_rank_idx[k], reverse=True)
        
        self.word_rank_idx =  self.rank.get_ranks(self.words_graph)
        self.sorted_word_rank_idx = sorted(self.word_rank_idx, key=lambda k: self.word_rank_idx[k], reverse=True)
        
        
    def summarize(self, sent_num=3):
        summary = []
        index=[]
        for idx in self.sorted_sent_rank_idx[:sent_num]:
            index.append(idx)
        
        index.sort()
        for idx in index:
            summary.append(self.sentences[idx])
        
        return summary
        
    def keywords(self, word_num=3):
        rank = Rank()
        rank_idx = rank.get_ranks(self.words_graph)
        sorted_rank_idx = sorted(rank_idx, key=lambda k: rank_idx[k], reverse=True)
        
        keywords = []
        index=[]
        for idx in sorted_rank_idx[:word_num]:
            index.append(idx)
            
        index.sort()
        for idx in index:
            keywords.append(self.idx2word[idx])
        
        return keywords

def make_quiz(sentences, words):
    quiz_sentences = []
    remove_sentences = []
    answer_keywords = []

    for word in words:
        for sentence in sentences:
            if word in sentence and sentence not in remove_sentences and word not in answer_keywords:
                remove_sentences.append(sentence)
                replacement = "_" * len(word)
                sentence = sentence.replace(word, replacement)
                answer_keywords.append(word)
                quiz_sentences.append(sentence)

    return quiz_sentences, answer_keywords