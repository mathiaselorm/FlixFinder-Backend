from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.forms import EmailField

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all the required fields, plus a repeated password.
    """
    email = EmailField(label=_("Email Address"), help_text=_("A valid email address, please."))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'location', 'password1', 'password2',)
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'phone_number': _('Phone Number'),
            'date_of_birth': _('Date of Birth'),
            'gender': _('Gender'),
            'location': _('Location'),
        }
        help_texts = {
            'email': _('A valid email address, please.'),
        }

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def save(self, commit=True):
        """
        Save the provided password in hashed format
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on the user, but replaces the password field with admin's password hash display field.
    """
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'location', 'profile_picture', 'bio', 'is_active', 'is_staff',)
        labels = {
            'email': _('Email Address'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'phone_number': _('Phone Number'),
            'date_of_birth': _('Date of Birth'),
            'gender': _('Gender'),
            'location': _('Location'),
            'profile_picture': _('Profile Picture'),
            'bio': _('Biography'),
        }
        help_texts = {
            'is_active': _('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'),
            'is_staff': _('Designates whether the user can log into this admin site.'),
        }
