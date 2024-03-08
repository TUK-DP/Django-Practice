import numpy as np
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize


def get_graph_matrix(only_noun_sentence_list):
    """문장별 가중치 그래프 생성"""
    # CountVectorizer 객체 생성
    cnt_vec = CountVectorizer(tokenizer=Okt().morphs)
    # 단어별 가중치 그래프 생성
    cnt_vec_mat = normalize(
        cnt_vec.fit_transform(only_noun_sentence_list).toarray().astype(float)
        , axis=0
    )
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
