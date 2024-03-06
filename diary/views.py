from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from diary.serializers import *
from users.models import User
from .textrank import TextRank, make_quiz


class WriteView(APIView):
    @swagger_auto_schema(operation_description="일기 작성", request_body=WriteRequest, responses={"201": '작성 성공'})
    def post(self, request):
        requestSerial = WriteRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # user 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        # Diary 객체 생성
        newDiary = Diary.objects.create(user=findUser, title=request.get('title'))

        sentence = request.get('content')

        # Sentences 객체 생성
        newSentence = Sentences.objects.create(sentence=sentence, diary=newDiary)

        # 키워드 추출
        memory = TextRank(content=sentence)

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, answer = make_quiz(memory, keyword_size=5)

        # Quizs 객체 생성
        Quizs.objects.bulk_create(
            [Quizs(question=q, answer=a, sentence=newSentence) for q, a in zip(question, answer)]
        )

        return ApiResponse.on_success(
            result=SentenceSimpleSerializer(newSentence).data,
            response_status=status.HTTP_201_CREATED
        )


class UpdateView(APIView):
    @swagger_auto_schema(operation_description="일기 수정", request_body=UpdateRequest, responses={"201": '작성 성공'})
    def post(self, request):
        requestSerial = UpdateRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        # Diary와 연관된 모든 Sentence 삭제
        findDiary.sentences.all().delete()

        content = request.get('content')
        newSentence = Sentences.objects.create(sentence=content, diary=findDiary)

        memory = TextRank(content=content)
        question, answer = make_quiz(memory, keyword_size=5)

        Quizs.objects.bulk_create(
            [Quizs(question=q, answer=a, sentence=newSentence) for q, a in zip(question, answer)]
        )

        return ApiResponse.on_success(
            result=SentenceSimpleSerializer(newSentence).data,
            response_status=status.HTTP_201_CREATED
        )


class GetDiaryByUserView(APIView):
    @swagger_auto_schema(operation_description="유저의 일기 조회", query=GetUserRequest,
                         response={"200": DiarySerializer})
    def get(self, request):
        requestSerial = GetUserRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # User 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        # User와 연관된 모든 Diary 가져오기
        findDiaries = Diary.objects.filter(user=findUser)

        return ApiResponse.on_success(
            result=DiarySerializer(findDiaries, many=True).data,
            response_status=status.HTTP_200_OK
        )


class GetQuizView(APIView):
    @swagger_auto_schema(operation_description="일기회상 퀴즈", query=GetDiaryRequest,
                         responses={"200": "퀴즈"})
    def get(self, request):
        requestSerial = GetDiaryRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        # Diary와 연관된 모든 Sentence 가져오기
        sentences = findDiary.sentences.all()

        # 모든 Sentence와 연관된 Quiz 가져오기 == [Quizs, Quizs, Quizs, ...]
        quizzes = sum([sentence.quizs.all() for sentence in sentences], [])

        return ApiResponse.on_success(
            result=QuizSerializer(quizzes, many=True).data,
            response_status=status.HTTP_200_OK
        )


"""
떠나는 길에 네가 내게 말했지\n너는 바라는 게 너무나 많아\n잠깐이라도 널 안 바라보면\n머리에 불이 나버린다니까\n나는 흐르려는 눈물을 참고\n하려던 얘길 어렵게 누르고\n그래, 미안해라는 한 마디로\n너랑 나눈 날들 마무리했었지\n달디달고, 달디달고, 달디단, 밤양갱, 밤양갱\n내가 먹고 싶었던 건, 달디단, 밤양갱, 밤양갱이야\n떠나는 길에 네가 내게 말했지\n너는 바라는 게 너무나 많아\n아냐, 내가 늘 바란 건 하나야\n한 개뿐이야, 달디단, 밤양갱\n달디달고, 달디달고, 달디단, 밤양갱, 밤양갱\n내가 먹고 싶었던 건, 달디단, 밤양갱, 밤양갱이야\n상다리가 부러지고\n둘이서 먹다 하나가 쓰러져버려도\n나라는 사람을 몰랐던 넌\n떠나가다가 돌아서서 말했지\n너는 바라는 게 너무나 많아\n아냐, 내가 늘 바란 건 하나야\n한 개뿐이야, 달디단, 밤양갱\n"""
