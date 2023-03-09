# from django.test import Client
# from django.urls import reverse
# from test_plus.test import TestCase
#
# from src.articles.models import Article
# from src.news.models import News
# from src.questions.models import Question
#
#
# class SearchViewsTests(TestCase):
#     def setUp(self):
#         self.user = self.make_user("first_user")
#         self.other_user = self.make_user("second_user")
#
#         self.client = Client()
#         self.other_client = Client()
#
#         self.client.login(username="first_user", password="password")
#         self.other_client.login(username="second_user", password="password")
#
#         self.title = "Dad jokes 4! "
#         self.content = """How do you make holy water?
#         Freeze it into ice, then drill in some holes.
#         """
#         self.article = Article.objects.create(
#             user=self.user,
#             title="Do you know how Moses makes his tea? Hebrews it!",
#             content=self.content,
#             tags="ridiculous, funny",
#             status="P",
#         )
#         self.article_2 = Article.objects.create(
#             user=self.other_user,
#             title="Jokes about unemployed people are not funny. They just don't work.",
#             content="What did I do when I landed in Iraq by mistake? - Iran.",
#             tags="bad",
#             status="P",
#         )
#         self.question_one = Question.objects.create(
#             user=self.user,
#             title="How do you call a boat without a rope? - Boat!",
#             content="How many pears grow on a tree? - They all do.",
#             tags="ridiculous, funny",
#         )
#         self.question_two = Question.objects.create(
#             user=self.user,
#             title="They tested a revolutionary new blender. They got mixed results.",
#             content="""What do people like to wear in England? - Tea-shirts.""",
#             has_answer=True,
#             tags="ridiculous, funny",
#         )
#         self.news_one = News.objects.create(
#             user=self.user,
#             content="What type of candy is always late? A chocolate.",
#         )
#
#     def test_news_search_results(self):
#         response = self.client.get(
#             reverse("search:results"),
#             {
#                 "query": "This is",
#             },
#         )
#
#         assert response.status_code == 200
#
#         assert self.article in response.context["articles_list"]
#         assert self.news_one in response.context["news_list"]
#         assert self.question_one in response.context["questions_list"]
#         assert self.question_two in response.context["questions_list"]
#
#     def test_questions_suggestions_results(self):
#         response = self.client.get(
#             reverse("search:suggestions"),
#             {
#                 "term": "first",
#             },
#             HTTP_X_REQUESTED_WITH="XMLHttpRequest",
#         )
#         assert response.json()[0]["value"] == "first_user"
#         assert response.json()[1]["value"] == "Jokes about unemployed people are not funny. They just don't work."
#         assert response.json()[2]["value"] == "Do you know how Moses makes his tea? Hebrews it!"
#         assert response.json()[3]["value"] == "They tested a revolutionary new blender. They got mixed results."
#         assert response.json()[4]["value"] == "How do you call a boat without a rope? - Boat!"
#

from django.test import Client
from django.urls import reverse
from test_plus.test import TestCase

from src.articles.models import Article
from src.news.models import News
from src.questions.models import Question


class SearchViewsTests(TestCase):
    """
    Includes tests for all the functionality
    associated with Views
    """

    def setUp(self):
        self.user = self.make_user("first_user")
        self.other_user = self.make_user("second_user")

        self.client = Client()
        self.other_client = Client()

        self.client.login(username="first_user", password="password")
        self.other_client.login(username="second_user", password="password")

        self.title = "First! Dad jokes 4!"
        self.content = """This is first!
        How do you make holy water?
        Freeze it into ice, then drill in some holes.
        """

        self.article = Article.objects.create(
            user=self.user,
            title="First! Do you know how Moses makes his tea? Hebrews it!",
            content=self.content,
            tags="funny, hilarious",
            status="P",
        )
        self.article_2 = Article.objects.create(
            user=self.other_user,
            title="First! Jokes about unemployed people are not funny. They just don't work",
            content="First!",
            tags="wow",
            status="P",
        )
        self.question_one = Question.objects.create(
            user=self.user,
            title="This is first! How do you call a boat without a rope? - Boat!",
            content="This is first! What did I do when I landed in Iraq by mistake? - Iran.",
            tags="cool, ridiculous",
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="First! They tested a revolutionary new blender. They got mixed results.",
            content="""This is first! What do people like to wear in England? - Tea-shirts.""",
            has_answer=True,
            tags="funny, ridiculous",
        )
        self.news_one = News.objects.create(
            user=self.user,
            content="This is first! What type of candy is always late? A chocolate.",
        )

    def test_news_search_results(self):
        response = self.client.get(
            reverse("search:results"),
            {
                "query": "This is",
            },
        )

        assert response.status_code == 200

        assert self.news_one in response.context["news_list"]
        assert self.question_one in response.context["questions_list"]
        assert self.question_two in response.context["questions_list"]
        assert self.article in response.context["articles_list"]

    def test_questions_suggestions_results(self):
        response = self.client.get(
            reverse("search:suggestions"),
            {
                "term": "first",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.json()[0]["value"] == "first_user"
        assert response.json()[1]["value"] == "First! Jokes about unemployed people are not funny. They just don't work"
        assert response.json()[2]["value"] == "First! Do you know how Moses makes his tea? Hebrews it!"
        assert response.json()[3]["value"] == "First! They tested a revolutionary new blender. They got mixed results."
        assert response.json()[4]["value"] == "This is first! How do you call a boat without a rope? - Boat!"
