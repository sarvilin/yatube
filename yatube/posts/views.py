from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow

from core.utils import pages_obj


def index(request):
    post_list = Post.objects.select_related('author', 'group')

    page_number = request.GET.get('page')
    page_obj = pages_obj(post_list, page_number)

    context = {
        'page_obj': page_obj,
        'index': True,
    }
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

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'number_of_posts_by_author': number_of_posts_by_author,
        'following': following,
    }
    template = "posts/profile.html"
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    number_of_posts_by_author = author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments,
        'number_of_posts_by_author': number_of_posts_by_author,
        'form': form,
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
    """Форма изменения поста."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)

    page_number = request.GET.get('page')
    page_obj = pages_obj(post_list, page_number)

    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    template = "posts/follow.html"
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
