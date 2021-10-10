from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Verify account
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from .utils import account_activation_token

from django.contrib import auth

# Multithreading for faster email sending
import threading

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

class RegistrationView(View):
    # Whenever a user sends a get request
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        
        # Retrieve User data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = { # Store previously entered information
            'fieldValues': request.POST
        }
        # Validate user data
        if not User.objects.filter(username=username).exists():
            
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password is less than 6 characters")
                    return render(request, 'authentication/register.html', context)
                # Create user account
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                
                # Path to view

                # Get the domain we are currently on
                current_site = get_current_site(request)
                
                email_subject = 'Activate your account'
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)), # Encode UID
                    'token': account_activation_token.make_token(user), # retrieve the token
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})
                
                # Relative URL to verification
                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hello ' + user.username + ',\n\nPlease click the link below to activate your account: \n' + activate_url,
                    'noreply@ninoina333.com',
                    [email],
                )
                EmailThread(email).start()
                
                messages.success(request, "Account successfully created. Check your email to activate it.")
                return render(request, 'authentication/register.html')
        
        return render(request, 'authentication/register.html')

class UsernameValidationView(View):
    # Whenever a user sends a get request
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        # Validation
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters.'}, status = 400)
        # If username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Username is already taken.'}, status = 409)
        # Otherwise the username is valid
        return JsonResponse({'username_valid': True})

class EmailValidationView(View):
    
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid.'}, status = 400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Email is already taken.'}, status = 409)
        
        return JsonResponse({'email_valid': True})

class VerificationView(View):

    def get(self, request, uidb64, token):
        try: 
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            # Invalid link, User is already activated
            if not account_activation_token.check_token(user, token):
                return redirect('login' +'?message=' + 'User already activated') # Query String
            
            if user.is_active: # User already active
                return redirect('login')

            # Activate the user
            user.is_active = True
            user.save()

            messages.success(request, "Account activated successfully")
            return redirect('login')

        except Exception as ex:
            pass
        
        return redirect('login')

class LoginView(View):

    def get(self, request):
        return render(request, 'authentication/login.html')

    # TODO Wrong condition is activating when account isn't activated yet
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password) 

             # Check if the user has valid credentials
            if user is not None:
                auth.login(request, user)
                # Check if user is activated
                if user.is_active:
                    messages.success(request, "Welcome, " + user.username + 
                                    ". You are currently logged in.")
                    return redirect('expenses')
                else:
                    messages.error(request, "Account is not activated. Please activate your account through your email.")
                    return render(request, 'authentication/login.html')
            else:
                messages.error(request, "Invalid login credentials given")    
                return render(request, 'authentication/login.html')
        
        messages.error(request, "Please make sure all fields are filled")    
        return render(request, 'authentication/login.html')


class LogoutView(View):

    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out")
        return redirect('login')

class RequestPasswordResetEmail(View):
    
    def get(self, request):
        
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, "Please give a valid email")
            return render(request, 'authentication/reset-password.html', context)

        current_site = get_current_site(request)
        user=User.objects.filter(email=email)

        if user.exists():
            
            email_contents = {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user[0].pk)), # Encode UID
                    'token': PasswordResetTokenGenerator().make_token(user[0]), # retrieve the token
            }

            link = reverse('reset-user-password', kwargs={
                        'uidb64': email_contents['uid'], 'token': email_contents['token']})
                    
            # Relative URL to verification
            reset_url = 'http://'+current_site.domain+link
            email_subject = 'Reset your password'
            email = EmailMessage(
                email_subject,
                'Hi there, a password reset has been requested for your account.' + '\n\nPlease click the link below to reset your password: \n' + reset_url,
                'noreply@ninoina333.com',
                [email],
            )
            EmailThread(email).start()

        messages.success(request, "Email has been sent follow the link to reset your password.")
        
        return render(request, 'authentication/reset-password.html')

class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            
            # Verify if the user has used the link before
            if not PasswordResetTokenGenerator().check_token(user, token):

                messages.info(request, "Password has already been reset. Please request another link")
                return render(request, 'authentication/reset-password.html')
        except Exception as error:
            pass

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'authentication/set-new-password.html', context)
        if len(password) < 6:
            messages.error(request, "Passwords too short.")
            return render(request, 'authentication/set-new-password.html', context)
        
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, "Password changed successfully.")
            return redirect('login')
        except Exception as error:
            messages.info(request, "Something went wrong with your request. Please try again.")
            return render(request, 'authentication/set-new-password.html', context)
        