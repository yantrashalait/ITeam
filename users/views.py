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
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import CreateView, DetailView, UpdateView
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import smtplib


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

            msg = """
                <div class="row">
    				<div class="entryforms login">
    				    <div class="thirdprty_login">
    				        <div class="formContainer p-4">
                                <h5>Activate Your Account</h5>
                                <span>An email has been sent to {{ to_email }}. Please activate your account by clicking the link on the email to be able to Login.</span>
    				        </div>
    				        <div class="ask_users">
    				            Go to home <a class="float-right" href="https://iteam.com.np/">Home</a>
    				        </div>
    				    </div>
    				</div>
    			</div>
            """

            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, [to_email, ], msg)
            server.quit()
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

        return redirect(reverse_lazy('users:profile-create'))
    else:
        return HttpResponse('Activation link is invalid!')


@login_required(login_url='/login')
def profile(request, *args, **kwargs):
    try:
        profile = UserProfile.objects.get(user_id=kwargs.get('pk'))
        return render(request, 'users/profile.html', {'profile': profile})
    except:
        return redirect(reverse_lazy('users:profile-create'))


class ProfileCreate(LoginRequiredMixin, CreateView):
    template_name = 'users/userprofile_create.html'
    form_class = UserProfileForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ProfileCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('users:profile', kwargs={'pk': self.request.user.pk})


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'users/userprofile_create.html'
    form_class = UserProfileForm

    def get_object(self):
        return UserProfile.objects.get(user_id=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse('users:profile', kwargs={'pk': self.request.user.pk})
