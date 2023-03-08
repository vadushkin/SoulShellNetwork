import tempfile

from PIL import Image
from django.test import Client, override_settings
from django.urls import reverse
from test_plus.test import TestCase

from src.articles.models import Article


def get_temp_img():
    size = (200, 200)
    color = (255, 0, 0, 0)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        image = Image.new("RGB", size, color)
        image.save(f, "PNG")

    return open(f.name, mode="rb")


class ArticlesViewsTest(TestCase):
    def setUp(self):
        self.user = self.make_user("first_user")
        self.other_user = self.make_user("second_user")

        self.client = Client()
        self.other_client = Client()

        self.client.login(username="first_user", password="password")
        self.other_client.login(username="second_user", password="password")

        self.article = Article.objects.create(
            title="Astonishing title",
            content="""Delightful content""",
            status="P",
            user=self.user,
        )
        self.not_p_article = Article.objects.create(
            title="Dad jokes",
            content="""Delightful content.
                    Snake joke:

                    First snake: I hope I'm not poisonous.
                    Second snake: why?
                    First snake: because I bit my lip!😂
                    """,
            user=self.user,
        )

        self.test_image = get_temp_img()

    def tearDown(self):
        self.test_image.close()

    def test_index_articles(self):
        response = self.client.get(reverse("articles:list"))
        self.assertEqual(response.status_code, 200)

    def test_error_404(self):
        response_no_art = self.client.get(
            reverse("articles:article", kwargs={"slug": "no-slug"})
        )
        self.assertEqual(response_no_art.status_code, 404)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_article(self):
        response = self.client.post(
            reverse("articles:write_new"),
            {
                "title": "Adorable title",
                "content": "R2D2",
                "tags": "Shiny, Lovely",
                "status": "P",
                "image": self.test_image,
            },
        )
        assert response.status_code == 302

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_single_article(self):
        current_count = Article.objects.count()
        response = self.client.post(
            reverse("articles:write_new"),
            {
                "title": "Adorable title",
                "content": "R2D2",
                "tags": "Shiny, Lovely",
                "status": "P",
                "image": self.test_image,
            },
        )
        assert response.status_code == 302
        assert Article.objects.count() == current_count + 1

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_draft_article(self):
        response = self.client.post(
            reverse("articles:write_new"),
            {
                "title": "Adorable title",
                "content": "R2D2",
                "tags": "Shiny, Lovely",
                "status": "D",
                "image": self.test_image,
            },
        )
        resp = self.client.get(reverse("articles:drafts"))
        assert resp.status_code == 200
        assert response.status_code == 302
        assert (
                resp.context["articles"][0].slug
                == "first-user-adorable-title"
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_draft_article_change(self):
        response = self.client.post(
            reverse("articles:edit_article", kwargs={"pk": self.not_p_article.id}),
            {
                "title": "Specific changed title",
                "content": "R2D2",
                "tags": "Shiny, Lovely",
                "status": "D",
                "image": self.test_image,
            },
        )
        resp = self.client.get(reverse("articles:drafts"))
        assert resp.status_code == 200
        assert response.status_code == 302
        assert resp.context["articles"][0].title == "Specific changed title"
        assert (
                resp.context["articles"][0].slug == "first-user-dad-jokes"
        )
