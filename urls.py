from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^orm/schema/module/(?P<path>.{0,50})', views.ModuleSchema.as_view()),
    url(r'^orm/schema/(?P<path>.{0,50})', views.Schema.as_view()),
    url(r'^orm/query/(?P<path>.{0,50})', views.Query.as_view()),
]
