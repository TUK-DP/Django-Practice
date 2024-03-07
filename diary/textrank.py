import re
import numpy as np
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class SentenceNormalize:
    def __init__(self):
        self.okt = Okt()
        self.hanpattern = '([ㄱ-ㅎㅏ-ㅣ]+)'
        self.signpattern = '[^\w\s]'
        self.repl = ''

    def sent_normalize(self, sentence):
        # 이상한 받침 제거
        sentence = self.okt.normalize(sentence)
        # 한글 자음, 모음 제거
        sentence = re.sub(pattern=self.hanpattern, repl=self.repl, string=sentence)
        # 특수 기호 제거
        sentence = re.sub(pattern=self.signpattern, repl=self.repl, string=sentence)

        # 맞춤법 수정
        return sentence


class SentenceTokenizer:
    @staticmethod
    def get_text(content):
        # 문장 분리할 특수문자 정의
        replace_dict = {"\n": ".", "!": ".", "?": "."}
        # 특수문자 제거
        content = content.translate(str.maketrans(replace_dict))
        # 문장 분리
        sentences = content.rsplit('.')

        # 빈 문자열 제거 && 양옆 공백 제거
        sentences = [sentence.strip() for sentence in sentences if sentence != '']

        # 문장 정규화 객체 생성
        text_normalize = SentenceNormalize()

        # 문장 정규화
        return list(map(text_normalize.sent_normalize, sentences))

    @staticmethod
    def get_nouns(sentences):
        # 빈 문자열 제거
        sentences = [sentence for sentence in sentences if sentence != '']

        okt = Okt()

        stopword = ["오늘", "내일", "빨리", "바쁘게"]

        # 명사 추출후 명사 리스트를 문자열로 변환하는 함수
        def join_nouns(sentence):
            return ' '.join([noun for noun in okt.nouns(str(sentence))
                             if noun not in stopword])

        # 명사 추출
        return list(map(join_nouns, sentences))


class GraphMatrix:
    # 문장별 가중치 그래프 생성
    def __init__(self, sentence):
        # tfidf 객체 생성
        tfidf = TfidfVectorizer()

        tfidf_mat = tfidf.fit_transform(sentence).toarray()
        # 문장 사전 = {단어: index}
        vocab = tfidf.vocabulary_

        # 문장 가중치 그래프, 문장 사전 을 저장 && 문장 사전 = {index: 단어}
        self.sent_graph_vocab = np.dot(tfidf_mat, tfidf_mat.T), {vocab[word]: word for word in vocab}

        # CountVectorizer 객체 생성
        cnt_vec = CountVectorizer()

        # 단어별 가중치 그래프 생성
        cnt_vec_mat = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
        # 단어 사전 = {단어: index}
        vocab = cnt_vec.vocabulary_

        # 단어 가중치 그래프, 단어 사전 을 저장 && 단어 사전 = {index: 단어}
        self.words_graph_vocab = np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word]: word for word in vocab}

    # def get_sent_graph_vocab(self):
    #     return self.sent_graph_vocab

    def get_words_graph_vocab(self):
        return self.words_graph_vocab


class Rank:
    @staticmethod
    def get_ranks(graph, d=0.85):  # d = damping factor

        A = graph

        node_size = A.shape[0]

        for node in range(node_size):
            A[node, node] = 0  # diagonal(자기 자신의 노드의 가중치 == node -> node 가중치) 부분을 0으로

            # node에 해당하는 열의 총합
            col_sum = np.sum(A[:, node])  # graph[:, node] = graph[:][node]

            # 열의 합이 0이 아닐 경우만 나누기
            A[:, node] /= (col_sum if col_sum != 0 else 1)

            # -d를 곱하고
            A[:, node] *= -d

            # node -> node 가중치를 1로 만듬
            A[node, node] = 1

        # 모든 원소가 1 - d로 이루어진 node_size x 1 행렬 생성
        B = (1 - d) * np.ones((node_size, 1))

        """
        연립방정식 
        A[0][0] * X1 + A[0][1] * X2 + ... + A[0][n] * Xn = B[0]
        A[1][0] * X1 + A[1][1] * X2 + ... + A[1][n] * Xn = B[1]
        ...
        A[n][0] * X1 + A[n][1] * X2 + ... + A[n][n] * Xn = B[n]
        를 푼다.
        """
        # ranks == [X1 ~ Xn]
        ranks = np.linalg.solve(A, B)

        # {index: 가중치} 사전 생성
        return {idx: r[0] for idx, r in enumerate(ranks)}


class TextRank(object):
    def __init__(self, content):
        """
        :param content: The content of the text.
        """
        # 문장 추출
        self.sentences = SentenceTokenizer.get_text(content)
        # 명사 추출
        nouns = SentenceTokenizer.get_nouns(self.sentences)

        # 명사가 없는 경우 초기화
        if not nouns or nouns == ['']:
            self.sorted_word_rank = []
            self.words_graph = []
            self.sentences_dict = {}
            self.words_dict = {}
            self.weights_dict = {}
            return

        # 가중치 그래프 객체 생성
        matrix = GraphMatrix(nouns)
        # 문장별 가중치 그래프 [문장수, 문장수], {index: 문장} 사전
        # sent_graph, sent_vocab = matrix.get_sent_graph_vocab()
        # 단어별 가중치 그래프 [단어수, 단어수], {index: 단어} 사전
        words_graph, word_vocab = matrix.get_words_graph_vocab()

        # 단어별 가중치 사전 생성 == {index: 가중치}
        weights_dict = Rank.get_ranks(words_graph)
        # (단어, index, 가중치) 리스트 생성
        word_rank_idx = [(word_vocab[index], index, weight) for index, weight in weights_dict.items()]
        # weight 기준으로 정렬
        self.sorted_word_rank = sorted(word_rank_idx, key=lambda k: k[2], reverse=True)
        self.words_graph = words_graph
        self.sentences_dict = {index: sentence for index, sentence in enumerate(self.sentences)}
        self.words_dict = word_vocab
        self.weights_dict = weights_dict

    # sent_size 개의 문장 요약
    # def summarize(self, sent_size=3):
    #     return [sentence for sentence, index, weight in self.sorted_sent_rank[:sent_size]]

    def get_keywords(self, keyword_size=3):
        # 단어 가중치 상위 word_size개 word만 추출
        return [keyword[0] for keyword in self.sorted_word_rank[:keyword_size]]


def make_quiz(text_rank: TextRank, keyword_size=3):
    quiz_sentences = []
    remove_sentences = []
    answer_keywords = []

    for word in text_rank.get_keywords(keyword_size=keyword_size):
        for sentence in text_rank.sentences:
            # 문장에 키워드가 있고, 사용한 문장이 아니며, 사용한 키워드가 아닐 경우
            if word in sentence and sentence not in remove_sentences and word not in answer_keywords:
                # 사용한 문장과 사용한 키워드를 저장
                remove_sentences.append(sentence)
                answer_keywords.append(word)

                # 문장에서 키워드를 _로 대체
                sentence = sentence.replace(word, "_" * len(word))

                # 퀴즈 문장 추가
                quiz_sentences.append(sentence)

    return quiz_sentences, answer_keywords
