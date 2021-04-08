from django import forms
from django.contrib.auth import authenticate, get_user_model, login
from recipes.tasks import send_verification_email

User = get_user_model()


class CreationForm(forms.ModelForm):
    """Форма регистрации нового пользователя"""

    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    first_name = forms.CharField(label='Имя ФИО')
    username = forms.CharField(label='Имя пользователя Username')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password')

    def save(self, commit=True):
        """
        Переопределяем метод для того чтоб после регистрации пользователь был
        аутентифицирован
        """

        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            auth_user = authenticate(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password']
            )
            login(self.request, auth_user)
            send_verification_email.delay(user.id)
        return user
