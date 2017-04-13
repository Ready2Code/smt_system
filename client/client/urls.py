"""client URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from controller import views as controller_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^opentv/$',            controller_views.start_controller,   name='opentv'),
    url(r'^command/$',               controller_views.handle_command,     name='home'),
    url(r'^show_channels/command/$',               controller_views.handle_command,     name='home'),
    url(r'^show_channels/$',     controller_views.show_channels,      name='show_channels'),
    url(r'^currentprogramme/$',     controller_views.get_current_programme_info,      name='get_current_programme'),
    url(r'^get_channels/$',      controller_views.get_channels,       name='get_channels'),
    url(r'^cplay/(\d+)/$',        controller_views.play_channel,       name='play_channel'),


]
