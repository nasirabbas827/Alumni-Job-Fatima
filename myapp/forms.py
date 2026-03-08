from django import forms
from .models import UserRegister

class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = UserRegister
        fields = [
            'full_name', 'username', 'email', 'password', 
            'gender', 'age', 'role', 'phone', 'city', 'country'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Choose a unique username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Create a strong password'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. New York'}),
            'country': forms.TextInput(attrs={'placeholder': 'e.g. USA'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Your age'}),
            # Select widgets usually don't need placeholders, but we can style them
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This loop automatically adds a 'form-control' style class to every field
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'custom-input'})

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'custom-input'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'custom-input'
        })
    )

from django import forms
from .models import UserRegister


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserRegister
        fields = [
            'full_name',
            'email',
            'gender',
            'age',
            'phone',
            'city',
            'country',
            'education',
            'skills',
            'experience',
            'contact_number',
            'resume',
            'is_public'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Your age'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'contact_number': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. New York'}),
            'country': forms.TextInput(attrs={'placeholder': 'e.g. USA'}),
            'education': forms.TextInput(attrs={'placeholder': 'Your highest education'}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your skills (e.g. Python, Django, React)'}),
            'experience': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your work experience'}),
            'resume': forms.FileInput(),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply common styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'custom-input'})


from django import forms
from .models import UserRegister


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your registered email',
            'class': 'custom-input'
        })
    )


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter new password',
            'class': 'custom-input'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'custom-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")

        if p1 != p2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
    
from django import forms
from .models import Job


class JobForm(forms.ModelForm):

    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'location',
            'salary_min',
            'salary_max',
            'category',
            'skills_required'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Job Title'}),
            'description': forms.Textarea(attrs={'class': 'custom-input', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Job Location'}),
            'salary_min': forms.NumberInput(attrs={'class': 'custom-input'}),
            'salary_max': forms.NumberInput(attrs={'class': 'custom-input'}),
            'category': forms.TextInput(attrs={'class': 'custom-input'}),
            'skills_required': forms.Textarea(attrs={'class': 'custom-input', 'rows': 3}),
        }

from django import forms
from .models import JobApplication

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume']