
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

from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Image, Vote

class ImageAdmin(admin.ModelAdmin):
    list_display = ('real_name', 'date_pub', 'get_uploader')
    search_fields = ['real_name']

    def get_uploader(self, obj):
        return obj.usr_idx.username
    get_uploader.short_description = 'Autore'

admin.site.register(Image, ImageAdmin)

admin.site.register(Vote)

admin.site.unregister(Group)
