from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from oauth_app.views import MyLoginView


urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html")),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),


    path('login/', MyLoginView.as_view(redirect_authenticated_user=True),name='login'),
    #path('logout/', LogoutView.as_view(next_page='login'),name='logout'),
    #path('register/', RegisterView.as_view(),name='register'),


    path('password-reset/', PasswordResetView.as_view(template_name='account/password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'),name='password_reset_complete'),



]