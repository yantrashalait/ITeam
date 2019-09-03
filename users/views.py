from django.contrib.auth.decorators import login_required
from users.forms import UserRegisterForm
from django.shortcuts import render, redirect
from users.models import UserProfile
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .signup_tokens import account_activation_token
from django.conf import settings
from django.contrib.auth.models import User 
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.is_active = False
            user.save()

            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            message = render_to_string('users/acc_active_email.html', {
                'user': user,
                'domain': settings.SITE_URL,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'users/emailnotify.html', {'email': user.email})
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            return render(request, 'users/register.html', {
                'form': form,
                'username': username,
                'email': email,
            })
    else:        
        form = UserRegisterForm()        
        return render(request, 'users/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return redirect(reverse_lazy('login'))
    else:
        return HttpResponse('Activation link is invalid!')