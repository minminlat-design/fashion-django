from django import forms
from .models import Account





class RegistrationForm(forms.ModelForm):
   
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'tf-field-input tf-input',
                'placeholder': ' ',
                'id': 'property1',
                'name': 'first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'tf-field-input tf-input',
                'placeholder': ' ',
                'id': 'property2',
                'name': 'last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'tf-field-input tf-input',
                'placeholder': ' ',
                'id': 'property3',
                'name': 'email',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'tf-field-input tf-input',
                'placeholder': ' ',
                'id': 'property4',
                'name': 'password',
            }),
            
        }
        
    