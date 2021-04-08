from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Регистрация нового пользователя"""

    form_class = CreationForm
    success_url = reverse_lazy('index_view')
    template_name = 'registration/signup.html'

    def get_form_kwargs(self):
        """Функция передает request в forms.py"""

        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs
