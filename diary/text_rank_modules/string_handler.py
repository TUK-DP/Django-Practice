import re

from konlpy.tag import Okt

okt = Okt()
# 한글 자음, 모음
han_pattern = '([ㄱ-ㅎㅏ-ㅣ]+)'

# 특수 기호
sign_pattern = r'[^\w\s]'

# 불용어
stop_word = ["오늘", "내일", "빨리", "바쁘게"]

# 문장 분리할 특수문자 정의
replace_str = "\n ! ?"
replace_dict = {key: '.' for key in replace_str.split()}


def sentence_normalize_tokenizer(sentence):
    """긴 문장을 문장 리스트로 변환하는 함수"""
    # 문자의 특수문자 제거
    sentence = sentence.translate(str.maketrans(replace_dict))
    # 문장 분리
    sentence_list = sentence.rsplit('.')

    # 빈 문자열은 없애고 문장 정규화 진행
    return [string_normalizer(sentence) for sentence in sentence_list if sentence != '']


def string_normalizer(string):
    """문자열 정규화 함수

    1. 이상한 받침 제거
    2. 한글 자음, 모음 제거
    3. 특수 기호 제거
    """
    # 이상한 받침 제거
    string = okt.normalize(string)
    # 한글 자음, 모음 제거
    string = re.sub(pattern=han_pattern, repl='', string=string)
    # 특수 기호 제거
    return re.sub(pattern=sign_pattern, repl='', string=string)


def map_to_nouns(sentences):
    """문장 리스트를 명사 리스트로 변환하는 함수
    return:
    ["명사 명사 ..." , "명사 명사 ..." , ...]
    """
    # 명사 추출후 명사 리스트를 문자열로 변환하는 함수
    def join_nouns(sentence):
        return ' '.join([noun for noun in okt.nouns(str(sentence))
                         if noun not in stop_word])

    # 빈 문자열 제거와 명사 붙힌 리스트 반환
    return [join_nouns(sentence) for sentence in sentences if sentence != '']
