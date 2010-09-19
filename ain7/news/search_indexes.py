
from haystack import indexes
from haystack import site

from ain7.news.models import NewsItem


class NewsItemIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

site.register(NewsItem, NewsItemIndex)

