from typing import List
from django.core.paginator import Paginator, Page

from posts.models import Post
from yatube.settings import NUM_OF_POST


def pages_obj(
        post_list: List[Post],
        page_number: int,
        num_of_post: int = NUM_OF_POST) -> Page:
    paginator = Paginator(post_list, num_of_post)
    return paginator.get_page(page_number)
