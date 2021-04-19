from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

handler404 = 'foodgram.views.page_not_found'
handler500 = 'foodgram.views.server_error'

urlpatterns = [
    path('', include('recipes.urls')),
    path('accounts/', include('users.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('about/about-author/', views.flatpage,
         {'url': '/about-author/'}, name="about-author"),
    path('about/about-spec/', views.flatpage,
         {'url': '/about-spec/'}, name="about-spec"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
