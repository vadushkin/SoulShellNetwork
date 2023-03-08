from django.test import Client
from django.urls import reverse
from test_plus.test import TestCase

from src.questions.models import Question, Answer


class QAViewsTest(TestCase):
    def setUp(self):
        self.user = self.make_user("first_user")
        self.other_user = self.make_user("second_user")

        self.client = Client()
        self.other_client = Client()

        self.client.login(username="first_user", password="password")
        self.other_client.login(username="second_user", password="password")

        self.question_one = Question.objects.create(
            user=self.user,
            title="Which bus went from Spain to America?",
            content="Columbus",
            tags="hilarious, funny",
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="Dad jokes 3!",
            content="""
            I read the other day that people eat more bananas than monkeys. 
            No surprises there.
            I can’t even remember the last time I ate a monkey.
            """,
            has_answer=True,
            tags="hilarious, funny",
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="Laugh",
            is_answer=True,
        )

    def test_index_questions(self):
        response = self.client.get(reverse("questions:question_indexed"))
        assert response.status_code == 200
        assert "Which bus went from Spain to America?" in str(response.context["questions"])

    def test_create_question_view(self):
        current_count = Question.objects.count()
        response = self.client.post(
            reverse("questions:ask_question"),
            {
                "title": "What is a bunny without a carrot? - Hungry!",
                "content": """
                Did you hear about the new movie constipation? 
                It hasn't come out yet.
                """,
                "status": "O",
                "tags": "funny, ridiculous",
            },
        )
        assert response.status_code == 302
        new_question = Question.objects.first()
        assert new_question.title == "What is a bunny without a carrot? - Hungry!"
        assert Question.objects.count() == current_count + 1

    def test_answered_questions(self):
        response = self.client.get(reverse("questions:question_list"))
        assert response.status_code == 200
        assert "Which bus went from Spain to America?" in str(response.context["questions"])

    def test_unanswered_questions(self):
        response = self.client.get(reverse("questions:question_list"))
        assert response.status_code == 200
        assert "Which bus went from Spain to America?" in str(response.context["questions"])

    def test_answer_question(self):
        current_answer_count = Answer.objects.count()
        response = self.client.post(
            reverse("questions:propose_answer", kwargs={"question_id": self.question_one.id}),
            {
                "content": "Laugh",
            },
        )
        assert response.status_code == 302
        assert Answer.objects.count() == current_answer_count + 1

    def test_question_upvote(self):
        response_one = self.client.post(
            reverse("questions:question_vote"),
            {
                "value": "U",
                "question": self.question_one.id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response_one.status_code == 200

    def test_question_downvote(self):
        response_one = self.client.post(
            reverse("questions:question_vote"),
            {
                "value": "D",
                "question": self.question_one.id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response_one.status_code == 200

    def test_answer_upvote(self):
        response_one = self.client.post(
            reverse("questions:answer_vote"),
            {
                "value": "U",
                "answer": self.answer.uuid_id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response_one.status_code == 200

    def test_answer_downvote(self):
        response_one = self.client.post(
            reverse("questions:answer_vote"),
            {
                "value": "D",
                "answer": self.answer.uuid_id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response_one.status_code == 200

    def test_accept_answer(self):
        response_one = self.client.post(
            reverse("questions:accept_answer"),
            {
                "answer": self.answer.uuid_id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response_one.status_code == 200

    def test_owner_in_context(self):
        response_one = self.client.get(
            reverse("questions:question_detail", kwargs={"pk": self.question_one.id}),
        )
        response_two = self.other_client.get(
            reverse("questions:question_detail", kwargs={"pk": self.question_two.id}),
        )

        assert response_one.status_code == 200
        assert response_two.status_code == 200

        assert response_one.context.get("is_question_owner") is True
        assert response_two.context.get("is_question_owner") is False
