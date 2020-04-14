from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=32,label = "Display Name", required=True)
    email = forms.EmailField(label = "Email", required=True)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
    
    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.display_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user 