from test_plus.test import TestCase

from src.articles.models import Article


class ArticlesModelsTest(TestCase):
    def setUp(self):
        self.user = self.make_user("test_user")
        self.other_user = self.make_user("other_test_user")
        self.article = Article.objects.create(
            title="Wonderful title",
            content="Delightful content",
            status="P",
            user=self.user,
        )
        self.article.tags.add("test1", "test2")
        self.not_p_article = Article.objects.create(
            title="Astonishing title",
            content="""Delightful content.
                    Snake joke:

                    First snake: I hope I'm not poisonous.
                    Second snake: why?
                    First snake: because I bit my lip!😂
                    """,
            user=self.user,
        )
        self.not_p_article.tags.add("test1", "test2")

    def test_object_instance(self):
        assert isinstance(self.article, Article)
        assert isinstance(self.not_p_article, Article)
        assert isinstance(Article.objects.get_published()[0], Article)

    def test_return_values(self):
        assert self.article.status == "P"
        assert self.article.status != "p"
        assert self.not_p_article.status == "D"
        assert str(self.article) == "Wonderful title"
        assert self.article in Article.objects.get_published()
        assert Article.objects.get_published()[0].title == "Wonderful title"
        assert self.not_p_article in Article.objects.get_drafts()

    def test_get_popular_tags(self):
        correct_dict = {"test1": 1, "test2": 1}
        assert Article.objects.get_counted_tags() == correct_dict.items()

    def test_change_draft_title(self):
        assert self.not_p_article.title == "Astonishing title"
        self.not_p_article.title = "Specific changed title"
        self.not_p_article.save()
        assert self.not_p_article.title == "Specific changed title"
