import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from diary.text_rank_modules.stop_words import stop_words
from diary.text_rank_modules.string_handler import map_to_nouns_join


def get_graph_matrix(normalized_sentence_list: list):
    """문장별 가중치 그래프 생성
    TODO: 적은 문장이거나 단어가 적은 경우에 대한 예외처리해야함
    """

    # 명사 리스트로 변환 ["명사 명사 ...", "명사 명사 ...", ...]
    only_nouns_enum_list = map_to_nouns_join(normalized_sentence_list)

    cnt_vec = CountVectorizer(stop_words=stop_words)

    # 단어별 가중치 그래프 생성
    cnt_vec_mat = normalize(
        cnt_vec.fit_transform(only_nouns_enum_list).toarray().astype(float)
        , axis=0
    )

    # 단어 (가중치 그래프, 단어 사전) 튜플 , 단어 사전 = {index: 단어}
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {word: index for index, word in cnt_vec.vocabulary_.items()}


def get_ranks(words_graph: np.array, d=0.85):  # d = damping factor
    # 빈 문장이 들어온 경우
    if words_graph.shape[0] == 0:
        # 빈 사전 반환
        return {}

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

