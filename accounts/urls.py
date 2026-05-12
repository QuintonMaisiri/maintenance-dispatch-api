from django.urls import path

from . import views


urlpatterns = [
    path('csrf/', views.CSRFView.as_view(), name='csrf'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.me_view, name='me'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('staff/', views.StaffListView.as_view(), name='staff-list'),
]