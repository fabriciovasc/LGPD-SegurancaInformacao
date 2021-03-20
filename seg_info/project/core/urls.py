from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path('logout/', views.logout_view, name='logout'),
    path('administracao/', include([
        path('user/', include([
            path('', views.UserListView.as_view(), name='user_list'),
            path('novo/', views.UserCreateView.as_view(), name='user_form'),
            path('<int:pk>/', views.UserUpdateView.as_view(), name='user_form'),
        ])),
    ])),
]
