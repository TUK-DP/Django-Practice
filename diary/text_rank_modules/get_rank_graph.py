import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from diary.text_rank_modules.stop_words import stop_words
from diary.text_rank_modules.string_handler import map_to_noun_list, map_to_nouns


def get_graph_matrix(normalized_sentence_list):
    """문장별 가중치 그래프 생성
    TODO: 적은 문장이거나 단어가 적은 경우에 대한 예외처리해야함
    """

    # 오류가 나는 버전 (하지만 합리적으로 작동함 (직관적으로 중요하다 생각되는게 뽑힘)
    only_nouns = map_to_noun_list(normalized_sentence_list)
    cnt_vec = CountVectorizer(stop_words=stop_words)
    cnt_vec_mat = normalize(
        cnt_vec.fit_transform(only_nouns).toarray().astype(float)
        , axis=0
    )

    # 정상 작동 하지만 너무 많은 단어가 나옴

    # cnt_vec = CountVectorizer(tokenizer=map_to_noun_list, stop_words=stop_words)
    # 단어별 가중치 그래프 생성
    # cnt_vec_mat = normalize(
    #     cnt_vec.fit_transform(normalized_sentence_list).toarray().astype(float)
    #     , axis=0
    # )

    # 단어 사전 = {단어: index}
    vocab = cnt_vec.vocabulary_

    # 단어 (가중치 그래프, 단어 사전) 튜플을 저장 && 단어 사전 = {index: 단어}
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word]: word for word in vocab}


def get_ranks(words_graph, d=0.85):  # d = damping factor
    A = words_graph
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
