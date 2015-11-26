"""
lerna URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(R"^$", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(R"^$", Home.as_view(), name="home")
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(R"^blog/", include(blog_urls))
"""

from ajax_select      import urls as ajax_select_urls
from django.conf      import settings
from django.conf.urls import include, url
from django.contrib   import admin

from news.views import IndexView

urlpatterns = (
    url(R"^$", IndexView.as_view(), name="index"),
    url(R"^news/", include("news.urls", namespace="news")),
    url(R"^admin/", include(admin.site.urls)),
    url(R"^ajax_select/", include(ajax_select_urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (
        url(R"^__debug__/", include(debug_toolbar.urls)),
    )
