from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Comment
from .forms import ArticleForm, CommentForm

def article_list(request):
    articles_list = Article.objects.all().order_by('-created_at')  # Сортировка по дате создания (новые сначала)
    paginator = Paginator(articles_list, 5)  # Разбиваем на страницы по 5 статей

    page = request.GET.get('page')  # Получаем номер текущей страницы из запроса
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # Если page не является целым числом, показываем первую страницу
        articles = paginator.page(1)
    except EmptyPage:
        # Если page выходит за пределы диапазона, показываем последнюю страницу
        articles = paginator.page(paginator.num_pages)

    return render(request, 'blog/article_list.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect('article_detail', pk=article.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/article_detail.html', {'article': article, 'form': form})

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'blog/article_form.html', {'form': form})

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user == article.author or request.user.is_superuser:
        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                return redirect('article_detail', pk=article.pk)
        else:
            form = ArticleForm(instance=article)
        return render(request, 'blog/article_form.html', {'form': form})
    else:
        return redirect('article_list')

@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user == article.author or request.user.is_superuser:
        article.delete()
    return redirect('article_list')