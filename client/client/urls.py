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
from tools import views as tools_views
from ntpclient  import views as ntpclient_views
from ts_adapter import views as ts_adapter_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',                         controller_views.start_page,         name='startpage'),
    url(r'^opentv/$',                  controller_views.start_controller,   name='opentv'),
    url(r'^command/$',                 controller_views.handle_command,     name='command'),
    url(r'^show_channels/command/$',   controller_views.handle_command,     name='show_channels_command'),
    url(r'^show_channels/$',           controller_views.show_channels,      name='show_channels'),
    url(r'^currentprogramme/$',        controller_views.get_current_programme_info,      name='get_current_programme'),
    url(r'^show_channels/related_operator/$',        controller_views.related_operator,   name='related_operator'),
    url(r'^get_channels/$',            controller_views.get_channels,       name='get_channels'),
    url(r'^cplay/(\d+)/$',             controller_views.cplay_channel,      name='cplay_channel'),
    url(r'^play/(\d+)/([\w-]+)/$',     controller_views.play_channel,       name='play_channel'),
    url(r'^stop/(\d+)/([\w-]+)/$',     controller_views.stop_channel,       name='stop_channel'),
    url(r'^show_channels/set_settings/$',          controller_views.modify_controller_settings,       name='modify_service_settings'),

    url(r'^show_channels/related_operator/get_related/$',            controller_views.get_related,       name='get_related'),
    url(r'^ntpclient_page/$',          ntpclient_views.ntpclient_page,     name='ntpclient_page'),
    url(r'^ntpclient_page/get_ntpclient_status$',          ntpclient_views.get_ntpclient_status,     name='get_ntpclient_status'),
    url(r'^ntpclient_page/start_ntpclient$',          ntpclient_views.start_ntpclient,     name='start_ntpclient'),
    url(r'^show_channels/related_operator/command/$',   controller_views.handle_command,     name='related_operator_command'),
    url(r'^tools/$',                    tools_views.tools,         name='tools'),
    url(r'^tools/render$',                    tools_views.video_render,         name='video_render'),
    url(r'^ts_adapter/$',               ts_adapter_views.ts_adapter,         name='ts_adapter'),
    url(r'^ts_adapter/update_list/$',   ts_adapter_views.update_list,         name='update_list'),
    url(r'^ts_adapter/modify/$',        ts_adapter_views.modify_item,              name='modify'),
    url(r'^ts_adapter/delete/$',        ts_adapter_views.delete_item,              name='delete'),
]
