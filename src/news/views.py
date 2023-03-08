from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DeleteView

from src.decorators import ajax_required
from src.mixins import AuthorRequiredMixin
from src.news.models import News


class NewsListView(LoginRequiredMixin, ListView):
    model = News
    paginate_by = 15

    def get_queryset(self, **kwargs):
        return News.objects.filter(reply=False)


class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = News
    success_url = reverse_lazy("news:list")


@login_required
@ajax_required
@require_http_methods(["POST"])
def post_news(request):
    user = request.user

    post = request.POST["post"]
    post = post.strip()

    if 0 < len(post) <= 280:
        posted = News.objects.create(user=user, content=post)
        html = render_to_string("news/news_single.html", {"news": posted, "request": request})
        return HttpResponse(html)
    else:
        length = len(post) - 280
        return HttpResponseBadRequest(content=f"Text is {length} characters longer than accepted.")


@login_required
@ajax_required
@require_http_methods(["POST"])
def like(request):
    news_id = request.POST["news"]

    user = request.user

    news = News.objects.get(pk=news_id)
    news.switch_like(user)

    return JsonResponse({"likes": news.count_likers()})


@login_required
@ajax_required
@require_http_methods(["GET"])
def get_thread(request):
    news_id = request.GET["news"]
    news = News.objects.get(pk=news_id)

    news_html = render_to_string(
        "news/news_single.html", {"news": news},
    )
    thread_html = render_to_string(
        "news/news_thread.html", {"thread": news.get_thread(), "request": request},
    )
    return JsonResponse({"uuid": news_id, "news": news_html, "thread": thread_html})


@login_required
@ajax_required
@require_http_methods(["POST"])
def post_comment(request):
    user = request.user

    post = request.POST["reply"]
    post = post.strip()

    par = request.POST["parent"]
    parent = News.objects.get(pk=par)

    if post:
        parent.reply_this(user, post)
        return JsonResponse({"comments": parent.count_thread()})
    else:
        return HttpResponseBadRequest()


@login_required
@ajax_required
@require_http_methods(["POST"])
def update_interactions(request):
    data_point = request.POST["id_value"]
    news = News.objects.get(pk=data_point)
    data = {"likes": news.count_likers(), "comments": news.count_thread()}
    return JsonResponse(data)
