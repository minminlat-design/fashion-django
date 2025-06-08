from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .forms import AccountDetailsForm, RegistrationForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants as message_constants
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm





def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.save()
            
            # 🔐 Automatically log in the user after registration
            login(request, user)
            
            messages.success(request, 'Registration successful.')
            return redirect('dashboard')
    else:        
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'account/register.html', context)



@login_required
def dashboard(request):
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard'}
    )
    


@login_required
def load_account_section(request, section):
    if section == 'orders':
        template = 'account/partials/orders.html'
        context = {}
    elif section == 'address':
        template = 'account/partials/address.html'
        context = {}
    elif section == 'account_details':
        template = 'account/partials/account_details.html'
        context = {
            'form': AccountDetailsForm(user=request.user),
            'DEFAULT_MESSAGE_LEVELS': message_constants

        }
    else:  # default to dashboard
        template = 'account/partials/dashboard.html'
        context = {}

    return render(request, template, context)

    


# Password change
@login_required
def account_details(request):
    if request.method == 'POST':
        form = AccountDetailsForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Account updated successfully.'})

            messages.success(request, 'Account updated successfully.')
            return redirect('dashboard')
        else:
            # Handle AJAX request with rendered HTML
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                rendered_html = render_to_string('account/partials/account_details.html', {
                    'form': form,
                    'DEFAULT_MESSAGE_LEVELS': message_constants
                }, request=request)
                return JsonResponse({'success': False, 'html': rendered_html}, status=400)

            messages.error(request, 'Please correct the errors below.')
    else:
        form = AccountDetailsForm(request.user)

    return render(request, 'account/partials/account_details.html', {
        'form': form,
        'DEFAULT_MESSAGE_LEVELS': message_constants
    })



class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/login.html'
    email_template_name = 'registration/password_reset_email.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, (
            
            "We’ve emailed you instructions for setting your password, if an account exists "
            "with the email you entered. You should receive them shortly. "
            "If you don’t receive an email, please make sure you’ve entered the address you registered with, "
            "and check your spam folder."
        ))
        return response
    
    def get_success_url(self):
        # Redirect back with a query param to tell template to show reset block
        return reverse_lazy('password_reset') + '?reset=1'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add a flag to show the reset form if 'reset=1' param present
        context['show_reset'] = self.request.GET.get('reset') == '1'
        context['login_form'] = AuthenticationForm(self.request)
        context['reset_form'] = context.get('form', PasswordResetForm())
        return context
    
    