from django import forms
from django.contrib.auth.forms import UserCreationForm
from webapp.models import Profile

class CreateProfileForm(forms.ModelForm):
    sage_username = forms.CharField(
        required=True,
        help_text='IMPORTANT: your Sage username cannot be changed later on.   \
        The provided username will be used for any publicly visible or shared data, so please choose your username carefully.'
    )

    class Meta:
        model = Profile
        fields = ('sage_username',)

    def clean_email(self):
        sage_username = self.cleaned_data.get('sage_username')

        #if Profile.objects.filter(sage_username=sage_username).exclude(username=username).count():
        #    raise forms.ValidationError('This username has been taken. Please try a different username.')
        return sage_username

    def save(self, commit=True):
        user = super(CreateProfileForm, self).save(commit=False)
        user.profile.sage_username = self.cleaned_data['sage_username']

        if commit:
            user.save()

        return user
