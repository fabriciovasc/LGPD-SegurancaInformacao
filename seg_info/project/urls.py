from django.urls import include, path, re_path

urlpatterns = [
    re_path(r'^', include('project.core.urls')),
    re_path(r'^portaria/', include('project.portaria.urls')),
    path('select2/', include('django_select2.urls')),
]
