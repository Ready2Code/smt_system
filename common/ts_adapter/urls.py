from django.conf.urls import url
from ts_adapter import views as ts_adapter_views

urlpatterns = [
    url(r'^$',               ts_adapter_views.ts_adapter,        name='ts_adapter'),
    url(r'^update_list/$',   ts_adapter_views.update_list,       name='update_list'),
    url(r'^modify/$',        ts_adapter_views.modify_item,       name='modify'),
    url(r'^delete/$',        ts_adapter_views.delete_item,       name='delete'),
    url(r'^start/$',         ts_adapter_views.start,             name='start_ts_adapter'),
    url(r'^stop/$',          ts_adapter_views.stop,              name='stop_ts_adapter'),
]

