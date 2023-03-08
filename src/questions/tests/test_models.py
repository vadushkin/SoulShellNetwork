from test_plus.test import TestCase

from src.questions.models import Question, Answer


class QAModelsTest(TestCase):
    def setUp(self):
        self.user = self.make_user("test_user")
        self.other_user = self.make_user("other_test_user")
        self.question_one = Question.objects.create(
            user=self.user,
            title="If you walk 2 black dogs on a leash, how do you fly to Mars?",
            content="What do you thing?",
        )
        self.question_one.tags.add("test1", "test2")
        self.question_two = Question.objects.create(
            user=self.user,
            title="Dad jokes 2!",
            content="""
            Fastest way to stop an argument between a bunch of deaf people?
            Just switch off the lights.
            """,
            has_answer=True,
        )
        self.question_two.tags.add("test1", "test2")
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="""
            Father talks to his 5-year-old son: 
            - “No, Mitie, you don’t have to worry. 
            There is no monster sleeping under your bed. 
            It sleeps every day in the bed next to me.“
            """,
            is_answer=True,
        )

    def test_can_vote_question(self):
        self.question_one.votes.update_or_create(
            user=self.user, defaults={"value": True},
        )
        self.question_one.votes.update_or_create(
            user=self.other_user, defaults={"value": True},
        )
        self.question_one.count_votes()

        assert self.question_one.total_votes == 2

    def test_can_vote_answer(self):
        self.answer.votes.update_or_create(
            user=self.user, defaults={"value": True},
        )
        self.answer.votes.update_or_create(
            user=self.other_user, defaults={"value": True},
        )
        self.answer.count_votes()

        assert self.answer.total_votes == 2

    def test_get_question_voters(self):
        self.question_one.votes.update_or_create(
            user=self.user, defaults={"value": True},
        )
        self.question_one.votes.update_or_create(
            user=self.other_user, defaults={"value": False},
        )
        self.question_one.count_votes()

        assert self.user in self.question_one.get_upvoters()
        assert self.other_user in self.question_one.get_downvoters()

    def test_get_answered_voters(self):
        self.answer.votes.update_or_create(
            user=self.user, defaults={"value": True},
        )
        self.answer.votes.update_or_create(
            user=self.other_user, defaults={"value": False},
        )
        self.answer.count_votes()

        assert self.other_user in self.answer.get_downvoters()
        assert self.user in self.answer.get_upvoters()

    def test_question_str_return_value(self):
        assert isinstance(self.question_one, Question)
        assert str(self.question_one) == "If you walk 2 black dogs on a leash, how do you fly to Mars?"

    def test_question_non_answered_question(self):
        assert self.question_one == Question.objects.get_unanswered()[0]

    def test_question_answered_question(self):
        assert self.question_two == Question.objects.get_answered()[0]

    def test_question_answers_returns(self):
        assert self.answer == self.question_two.get_answers()[0]

    def test_question_answer_count(self):
        assert self.question_two.count_answers == 1

    def test_question_accepted_answer(self):
        assert self.question_two.get_accepted_answer() == self.answer

    def test_get_popular_tags(self):
        correct_dict = {"test1": 2, "test2": 2}
        assert Question.objects.get_counted_tags() == correct_dict.items()

    def test_answer_return_value(self):
        assert str(self.answer) == """
            Father talks to his 5-year-old son: 
            - “No, Mitie, you don’t have to worry. 
            There is no monster sleeping under your bed. 
            It sleeps every day in the bed next to me.“
            """

    def test_answer_accept_method(self):
        answer_one = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="Tombstone engraving: I TOLD you I was sick!",
        )
        answer_two = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="There is nothing more depressing than a failed suicide attempt.",
        )
        answer_three = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="Toilet paper plays an important role in my life.",
        )

        self.assertFalse(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        self.assertFalse(self.question_one.has_answer)

        answer_one.accept_answer()

        self.assertTrue(answer_one.is_answer)
        self.assertTrue(self.question_one.has_answer)

        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)

        self.assertEqual(self.question_one.get_accepted_answer(), answer_one)
