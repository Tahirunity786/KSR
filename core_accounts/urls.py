from django.urls import path
from core_accounts.views import DeleteUserProfile, Register, ShowProfile, UpdateUserProfile, UserLogin, GoogleAuthAPIView


urlpatterns = [
    path('public/u/register/<str:user_type>/', Register.as_view()),
    path('public/o/oauth/google/', GoogleAuthAPIView.as_view()),
    path('public/u/login/', UserLogin.as_view()),
    path('profile/update/', UpdateUserProfile.as_view()),
    path('profile/delete/', DeleteUserProfile.as_view()),
    path('profile/delete/', DeleteUserProfile.as_view()),
    path('profile/<int:id>/show/', ShowProfile.as_view()),
]
