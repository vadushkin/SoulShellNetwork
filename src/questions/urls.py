from django.urls import re_path

from src.questions import views

app_name = "questions"

urlpatterns = [
    re_path(r"^$", views.QuestionListView.as_view(), name="question_list"),
    re_path(r"^answered/$", views.QuestionAnsListView.as_view(), name="question_answered"),
    re_path(r"^accept-answer/$", views.accept_answer, name="accept_answer"),
    re_path(r"^indexed/$", views.QuestionsIndexListView.as_view(), name="question_indexed"),
    re_path(r"^ask-question/$", views.CreateQuestionView.as_view(), name="ask_question"),
    re_path(r"^question-detail/(?P<pk>\d+)/$", views.QuestionDetailView.as_view(), name="question_detail"),
    re_path(r"^propose-answer/(?P<question_id>\d+)/$", views.CreateAnswerView.as_view(), name="propose_answer"),
    re_path(r"^question/vote/$", views.question_vote, name="question_vote"),
    re_path(r"^answer/vote/$", views.answer_vote, name="answer_vote"),
]
