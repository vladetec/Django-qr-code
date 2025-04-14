
from django.contrib import admin
from django.urls import path, include
from .api import api
from home import render_home
from home_after import render_home_after
from my_qrcodes import render_my_qrcodes
from contact import render_contact
from login.views import logout_user
from django.conf import settings
from django.conf.urls.static import static
from my_qrcodes import views



from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('', render_home, name = 'home'),
    path('home_after/', render_home_after, name='home_after'),
    # path('',include("home_after.urls"), name='home_after'),
    path('', include('login.urls'), name="login"),
    path('my_qrcodes/', render_my_qrcodes, name='my_qrcodes'),
    path('contact/', render_contact, name="contact"),
    path('',include("create.urls"), name='create'),
   
    
    path('logout/', logout_user, name = "logout"),
    path('delete_qrcode/<int:qrcode_id>/', views.delete_qrcode, name='delete_qrcode'),
    path('',include("home_after.urls"), name='packet_standard'),
    path('',include("home_after.urls"), name='packet_pro'),
    
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
