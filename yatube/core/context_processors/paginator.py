from django.core.paginator import Paginator

# Количество постов на странице
POSTS_ON_PAGE = 10


# Пэйджинатор
def paginator(request, post_list, page) -> Paginator:
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
