import numpy as np

from diary.text_rank_modules.get_rank_graph import get_graph_matrix, get_ranks
from diary.text_rank_modules.string_handler import sentence_normalize_tokenizer, map_to_noun_list


class TextRank:
    def __init__(self, content):
        # 문장 추출
        self.normalized_sentence_list = sentence_normalize_tokenizer(content)

        # 단어별 가중치 그래프(행렬곱) [[...]], {index: 단어} 사전
        words_graph, word_vocab = np.array([]), {}

        # get_graph_matrix 함수에서 ValueError 발생시 예외처리
        try:
            words_graph, word_vocab = get_graph_matrix(self.normalized_sentence_list)
        except ValueError:
            pass

        # 단어별 가중치 사전 생성 == {index: 가중치}
        weights_dict = get_ranks(words_graph)

        # (단어, index, 가중치) 리스트 생성
        word_rank_idx = [(word_vocab[index], index, weight) for index, weight in
                         weights_dict.items()]

        self.sorted_word_rank = sorted(word_rank_idx, key=lambda k: k[2], reverse=True)
        self.words_graph = words_graph
        self.words_dict = word_vocab
        self.weights_dict = weights_dict


def make_quiz(text_rank: TextRank, keyword_size=3):
    quiz_sentences = []
    remove_sentences = []
    answer_keywords = []

    # top weight keyword_size개 키워드 추출
    top_keyword_list = [keyword[0] for keyword in text_rank.sorted_word_rank[:keyword_size]]

    for word in top_keyword_list:
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
