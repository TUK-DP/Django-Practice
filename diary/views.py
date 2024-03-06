from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from diary.models import Diary, Sentences, Keywords, Questions
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

            memory = TextRank(content=content)
            question, keyword = make_quiz(memory, keyword_size=5)
        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, answer = make_quiz(memory, keyword_size=5)

            keywords = Keywords.objects.bulk_create([Keywords(keyword=k, sentence=sentence) for k in keyword])
            Questions.objects.bulk_create([Questions(question=q, keyword=k) for q, k in zip(question, keywords)])
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

                memory = TextRank(content=content)
                question, keyword = make_quiz(memory, keyword_size=5)
        # Sentence 객체 생성
        content = request.get('content')
        newSentence = Sentences.objects.create(sentence=content, diary=findDiary)

                keywords = Keywords.objects.bulk_create([Keywords(keyword=k, sentence=sentence) for k in keyword])
                Questions.objects.bulk_create([Questions(question=q, keyword=k) for q, k in zip(question, keywords)])
        # 키워드 추출
        memory = TextRank(content=content)
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


class GetDiaryByUserView(APIView):
    @swagger_auto_schema(operation_description="유저의 일기 조회", query_serializer=GetUserRequest,
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
    @swagger_auto_schema(operation_description="일기회상 퀴즈", query_serializer=GetDiaryRequest,
                         responses={"200": "퀴즈"})
    def get(self, request):
        requestSerial = GetDiaryRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

            sentences = diary.sentences.all()
        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

            q = []
            a = []

            for sentence in sentences:
                keywords = sentence.keywords.all()
                a.extend(keywords)
                for keyword in keywords:
                    questions = keyword.questions.all()
                    q.extend(questions)
        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

            result = []
            for question_obj, keyword_obj in zip(q, a):
                result.append({"Q": question_obj.question, "A": keyword_obj.keyword})

            return JsonResponse({'result': result}, status=status.HTTP_200_OK)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Diary와 연관된 모든 Sentence 가져오기
        sentences = findDiary.sentences.all()

        # 모든 Sentence와 연관된 Quiz 가져오기 quizzes == [Quizs, Quizs, Quizs, ...]
        quizzes = sum([list(sentence.quizs.all()) for sentence in sentences], [])

        return ApiResponse.on_success(
            result=QuizSerializer(quizzes, many=True).data,
            response_status=status.HTTP_200_OK
        )