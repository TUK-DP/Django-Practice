from diary.get_rank_graph import get_graph_matrix, get_ranks
from diary.string_handler import sentence_normalize_tokenizer, map_to_nouns


class TextRank(object):
    def __init__(self, content):
        # 문장 추출
        self.normalized_sentence_list = sentence_normalize_tokenizer(content)
        # 명사로 이루어진 문장 리스트로 변환
        only_noun_sentence_list = map_to_nouns(self.normalized_sentence_list)

        self.sorted_word_rank = []
        self.words_graph = []
        self.sentences_dict = {}
        self.words_dict = {}
        self.weights_dict = {}

        if only_noun_sentence_list and only_noun_sentence_list != ['']:
            # 단어별 가중치 그래프 [단어수, 단어수], {index: 단어} 사전
            words_graph, word_vocab = get_graph_matrix(only_noun_sentence_list)

            # (단어, index, 가중치) 리스트 생성
            word_rank_idx = [(word_vocab[index], index, weight) for index, weight in
                             get_ranks(words_graph).items()]
            # weight 기준으로 정렬
            self.sorted_word_rank = sorted(word_rank_idx, key=lambda k: k[2], reverse=True)
        else:
            self.sorted_word_rank = []


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
