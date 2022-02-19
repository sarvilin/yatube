from typing import List

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, Page
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User

NUM_OF_POST = 10


def index(request):
    post_list = Post.objects.select_related('author', 'group')

    page_number = request.GET.get('page')
    page_obj = pages_obj(post_list, page_number)

    context = {'page_obj': page_obj}
    template = "posts/index.html"
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')

    page_number = request.GET.get('page')
    page_obj = pages_obj(post_list, page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()

    number_of_posts_by_author = post_list.count()
    page_number = request.GET.get('page')
    page_obj = pages_obj(post_list, page_number)

    context = {
        'page_obj': page_obj,
        'author': author,
        'number_of_posts_by_author': number_of_posts_by_author,
    }
    template = "posts/profile.html"
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    author = post.author
    number_of_posts_by_author = author.posts.count()

    context = {
        'post': post,
        'number_of_posts_by_author': number_of_posts_by_author,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    """Форма создания поста."""
    template = 'posts/create_post.html'

    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form})

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if not form.is_valid():
        return render(request, template, {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author.username)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    if request.method != "POST":
        form = PostForm(instance=post)
        return render(request, template, {'form': form, 'is_edit': True})

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, template, {'form': form, 'is_edit': True})
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


def pages_obj(
        post_list: List[Post],
        page_number: int,
        num_of_post: int = NUM_OF_POST) -> Page:
    paginator = Paginator(post_list, num_of_post)
    return paginator.get_page(page_number)
