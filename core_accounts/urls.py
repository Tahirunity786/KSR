from django.urls import path
from core_accounts.views import Register, UserLogin, GoogleAuthAPIView


urlpatterns = [
    path('public/u/register/<str:user_type>/', Register.as_view()),
    path('public/o/oauth/google/', GoogleAuthAPIView.as_view()),
    path('public/u/login/', UserLogin.as_view()),
]
