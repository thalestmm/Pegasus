from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("", views.planner_form, name="planner_form"),
    path("mission/", views.render_mission, name="flight_planning")
]

urlpatterns += staticfiles_urlpatterns()