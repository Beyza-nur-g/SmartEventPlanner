from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'birth_date', 'gender', 'phone_number', 'interests', 'profile_picture']
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture','first_name', 'last_name', 'birth_date', 'gender', 'email', 'phone_number', 'interests', 'location' ]

class ResetPasswordForm(forms.Form):
    verification_code = forms.CharField(max_length=4, label='Doğrulama Kodu')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Yeni Şifre')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Yeni Şifre (Tekrar)')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError('Şifreler eşleşmiyor. Lütfen tekrar deneyin.')
        return cleaned_data
