from django.contrib.flatpages import views
from django.shortcuts import  render


def page_not_found(request, exception):
    return render(request,
                  'recipes/misc/404.html',
                  {'path': request.path},
                  status=404)


def server_error(request):
    return render(request, 'recipes/misc/500.html', status=500)
    