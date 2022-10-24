from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("", views.carp_form, name="carp_form"),
]

urlpatterns += staticfiles_urlpatterns()