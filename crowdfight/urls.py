
'''
    Crowdfight is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Crowdfight is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    Developed in Python by:
            - Bisi Simone    [ bisi.simone (at) gmail (dot) com ]
    for studying purposes ONLY on year 2017.
'''

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

import django.views.defaults
from django.views.static import serve

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    url(r'^winners$', views.winners, name='winners'),
    url(r'^losers$', views.losers, name='losers'),
    url(r'^newest$', views.newest, name='newest'),

    url(r'^register$', views.register, name='register'),
    url(r'^login$', auth_views.login, {'template_name': 'crowdfight/login.html'}, name='login'),
    url(r'^logout/$', views.web_logout, name='logout'),

    url(r'^profile/(?P<username>\w+)/$', views.profile, name='profile'),
    url(r'^stats$', views.stats, name='stats'),
    url(r'^add_image$', views.add_image, name='add_image'),

    url(r'^top_today$', views.top_today, name='top_today'),
    url(r'^top_month$', views.top_month, name='top_month'),
    url(r'^top_days$', views.top_days, name='top_days'),

    url(r'^image/(?P<image_idx>[0-9]+)/$', views.image, name='image'),
    
    url(r'^404$', views.page_404, name='page_404'),
    
    url(r'^$', views.index, name='index'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [ url(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, }), url(r'^static/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_ROOT }), ]
