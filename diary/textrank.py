# 세팅
from konlpy.tag import Okt, Kkma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np

#========================================
# 1. 데이터 가져오기(추후 변경)

# 텍스트 데이터 가져오는 함수
def get_text(diary):
    sentences = diary.split('.')
    return sentences

# =============================================
# 2. 자연어 처리

# Kkma 분석기
kkma = Kkma()

# Okt 분석기
okt = Okt()

# 명사만 추출하는 메서드
def get_nouns(sentences):
    nouns = []
    for sentence in sentences:
        if sentence != '':
            nor_sentence = okt.normalize(sentence)
            nouns.append(' '.join([noun for noun in kkma.nouns(str(nor_sentence))]))
            
    return nouns

# =============================================
# 3. 가중치 계산

tfidf = TfidfVectorizer()
cnt_vec = CountVectorizer()
graph_sentence = []

# TF-IDF maxtrix를 사용해 sentence graph를 리턴
def build_sent_graph(sentence):
    tfidf_mat = tfidf.fit_transform(sentence).toarray()
    graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
    return graph_sentence

# 단어 단위의 word graph를 만듦
def build_words_graph(sentence):
    cnt_vec_mat = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
    vocab = cnt_vec.vocabulary_
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word] : word for word in vocab}

# =============================================
# 4. TextRank 구현

def get_ranks(graph, d=0.85):       # d = damping factor
    A = graph
    maxtrix_size = A.shape[0]
    for id in range(maxtrix_size):
        A[id, id] = 0               # diagonal 부분을 0으로
        link_sum = np.sum(A[:, id]) # A[:, id] = A[:][id]
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1
    
    B = (1-d) * np.ones((maxtrix_size, 1))
    ranks = np.linalg.solve(A, B)   # 연립방정식 Ax = B
    return {idx: r[0] for idx, r in enumerate(ranks)}

# =============================================
# 5. 결과 확인

# 문장 요약 메서드(기본 10문장, 매개변수 따로 주면 그 숫자만큼 요약해줌)
def summarize(sorted_sent_rank_idx, diary_sentences, sent_num = 10):
    summary = []
    index = []
    for idx in sorted_sent_rank_idx[:sent_num]:
        index.append(idx)
    
    index.sort()

    for idx in index:
        summary.append(diary_sentences[idx])
    
    return summary

# 단어 추출 메서드(기본 10개, 매개변수 따로 주면 그 개수만큼 추출해줌)
def keywords(sorted_word_rank_idx, idx2word, word_num = 10):
    keywords = []
    index = []
    for idx in sorted_word_rank_idx[:word_num]:
        index.append(idx)

    for idx in index:
        keywords.append(idx2word[idx])

    return keywords

# =============================================
# 6. 일기 회상 퀴즈

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

# print(question)
# print(answer)

# for idx, (sentence, keyword) in enumerate(zip(question, answer), start=1):
#     print(f"Q{idx}. {sentence}")
#     print(f"A{idx}. {keyword}\n")