from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView
from taggit.models import Tag

from src.articles.models import Article
from src.decorators import ajax_required
from src.news.models import News
from src.questions.models import Question


class SearchListView(LoginRequiredMixin, ListView):
    model = News
    template_name = "search/search_results.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        query = self.request.GET.get("query")

        context["active"] = "news"
        context["hide_search"] = True
        context["tags_list"] = Tag.objects.filter(name=query)
        context["news_list"] = News.objects.filter(
            content__icontains=query, reply=False,
        ).distinct()
        context["articles_list"] = Article.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
            status="P",
        ).distinct()
        context["questions_list"] = Question.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
        ).distinct()
        context["users_list"] = (
            get_user_model()
            .objects.filter(Q(username__icontains=query) | Q(name__icontains=query))
            .distinct()
        )
        context["news_count"] = context["news_list"].count()
        context["articles_count"] = context["articles_list"].count()
        context["questions_count"] = context["questions_list"].count()
        context["users_count"] = context["users_list"].count()
        context["tags_count"] = context["tags_list"].count()
        context["total_results"] = (
                context["news_count"]
                + context["articles_count"]
                + context["questions_count"]
                + context["users_count"]
                + context["tags_count"]
        )
        return context


@login_required
@ajax_required
def get_suggestions(request):
    query = request.GET.get("term", "")
    users = list(
        get_user_model().objects.filter(
            Q(username__icontains=query) | Q(name__icontains=query),
        ),
    )
    articles = list(
        Article.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
            status="P",
        ),
    )
    questions = list(
        Question.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
        ),
    )

    data_retrieved = users

    data_retrieved.extend(articles)
    data_retrieved.extend(questions)

    results = []

    for data in data_retrieved:
        data_json = {}

        if isinstance(data, get_user_model()):
            data_json["id"] = data.id
            data_json["label"] = data.username
            data_json["value"] = data.username

        if isinstance(data, Article):
            data_json["id"] = data.id
            data_json["label"] = data.title
            data_json["value"] = data.title

        if isinstance(data, Question):
            data_json["id"] = data.id
            data_json["label"] = data.title
            data_json["value"] = data.title

        results.append(data_json)

    return JsonResponse(results, safe=False)
