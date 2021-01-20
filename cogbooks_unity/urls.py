"""
URL routes for the bookmarks app.
"""

from django.conf import settings
from django.conf.urls import url

from .views import UnityView, LTIView

urlpatterns = [
    url(
        r'^$',
        UnityView.as_view(),
        name='panel_index'
    ),
    url(
        r'^/ltiurl/{}$'.format(settings.USAGE_KEY_PATTERN),
        LTIView.as_view(),
        name='ltiurl',
    ),
]

