import numpy as np
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from diary.string_handler import sentence_normalize_tokenizer, map_to_nouns


class GraphMatrix:
    # 문장별 가중치 그래프 생성
    def __init__(self, sentence):
        # CountVectorizer 객체 생성
        cnt_vec = CountVectorizer(tokenizer=Okt().morphs)

        # 단어별 가중치 그래프 생성
        cnt_vec_mat = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
        # 단어 사전 = {단어: index}
        vocab = cnt_vec.vocabulary_

        # 단어 가중치 그래프, 단어 사전 을 저장 && 단어 사전 = {index: 단어}
        self.words_graph_vocab = np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word]: word for word in vocab}


class Rank:
    @staticmethod
    def get_ranks(graph, d=0.85):  # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0  # diagonal 부분을 0으로
            link_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
            if link_sum != 0:
                A[:, id] /= link_sum
            A[:, id] *= -d
            A[id, id] = 1

        B = (1 - d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(A, B)  # 연립방정식 Ax = b
        return {idx: r[0] for idx, r in enumerate(ranks)}


class TextRank(object):
    def __init__(self, content):
        # 문장 추출
        self.normalized_sentence_list = sentence_normalize_tokenizer(content)
        # 명사로 이루어진 문장 리스트로 변환
        nouns = map_to_nouns(self.normalized_sentence_list)

        if nouns and nouns != ['']:
            # 가중치 그래프 객체 생성
            matrix = GraphMatrix(nouns)
            # 단어별 가중치 그래프 [단어수, 단어수], {index: 단어} 사전
            words_graph, word_vocab = matrix.words_graph_vocab

            # (단어, index, 가중치) 리스트 생성
            word_rank_idx = [(word_vocab[index], index, weight) for index, weight in
                             Rank.get_ranks(words_graph).items()]
            # weight 기준으로 정렬
            self.sorted_word_rank = sorted(word_rank_idx, key=lambda k: k[2], reverse=True)
        else:
            self.sorted_word_rank = []

    def get_keywords(self, keyword_size=3):
        # 단어 가중치 상위 word_size개 word만 추출
        return [keyword[0] for keyword in self.sorted_word_rank[:keyword_size]]


def make_quiz(text_rank: TextRank, keyword_size=3):
    quiz_sentences = []
    remove_sentences = []
    answer_keywords = []

    for word in text_rank.get_keywords(keyword_size=keyword_size):
        for sentence in text_rank.normalized_sentence_list:
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
