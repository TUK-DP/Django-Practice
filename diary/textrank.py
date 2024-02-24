from konlpy.tag import Kkma, Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from hanspell import spell_checker
import numpy as np

# # 불용어 파일
# stopfile_path = './stopwords.txt'

# # 텍스트 데이터 가져오는 함수
# def get_stopword(stop_file_path):
#     with open(stop_file_path, 'r', encoding='utf-8') as f:
#         text = f.read()
#     return text

# # 불용어 데이터를 저장
# stopword = get_stopword(stopfile_path)

class SentenceTokenizer(object):
    def __init__(self):
        self.okt = Okt()
        # self.stopwords = stopword

    def get_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            text = text.replace('\n', '.')
            sentences = text.split('.')
            for idx in range(len(sentences)):
                sentences[idx] = spell_checker.check(sentences[idx]).checked
        
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
        
    def build_sent_graph(self, sentence):
        tfidf_mat = self.tfidf.fit_transform(sentence).toarray()
        self.graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
        return  self.graph_sentence
        
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
    def __init__(self, text):
        self.sent_tokenize = SentenceTokenizer()
        
        self.sentences = self.sent_tokenize.get_text(text)
        
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

# 다이어리 파일
file_path = './prac.txt'

textrank = TextRank(file_path)
# for row in textrank.summarize(3):
#     print(row)
#     print()
# print('keywords :', textrank.keywords())

quiz_sent, quiz_word = make_quiz(textrank.sentences, textrank.keywords())

for idx, (sentence, keyword) in enumerate(zip(quiz_sent, quiz_word), start=1):
    print(f"Q{idx}. {sentence}")
    print(f"A{idx}. {keyword}\n")