from .views import CompletePasswordReset, RequestPasswordResetEmail,LoginView, RegistrationView, UsernameValidationView, EmailValidationView, VerificationView, LogoutView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt # IMPORTANT, ONLY USING THIS BECAUSE THIS WEBSITE IS FOR TESTING/LEARNING
                                                    # SHOULD NOT BE USED IN A REAL ENVIRONMENT SHOULD BE CSRF_PROTECT
urlpatterns = [
    path('register', RegistrationView.as_view(), name = "register"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name = "validate-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name = "validate-email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name = "activate"),
    path('set-new-password/<uidb64>/<token>', CompletePasswordReset.as_view(), name = "reset-user-password"),
    path('login', LoginView.as_view(), name = "login"),
    path('logout', LogoutView.as_view(), name = "logout"),
    path('request-reset-link', RequestPasswordResetEmail.as_view(), name = "request-password"),
]