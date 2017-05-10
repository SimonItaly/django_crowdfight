# Crowdfight
------------
A KittenWar like Django application, written in Python with Django >= 1.8 in 2017/04 for a college project.

License
-------
Crowdfight is free software: you can redistribute it and/or modify<br />
it under the terms of the GNU General Public License as published by<br />
the Free Software Foundation, either version 3 of the License, or<br />
any later version.<br />
<br />
Crowdfight is distributed in the hope that it will be useful,<br />
but WITHOUT ANY WARRANTY; without even the implied warranty of<br />
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br />
See the GNU General Public License for more details.<br />

Requirements
------------

```python
	django >= 1.8
	django-graphos >= 0.3.41
```

Run the following command from terminal for a quick installation:
```bash
	pip install -r requirements.txt
```

Installation
------------

Create the project
```bash
	django-admin startproject <your_project>
```

Enter the newly created folder
```bash
	cd <your_project>
```

In settings.py, add the following to INSTALLED_APPS:

```python
   INSTALLED_APPS = [
      ...
      'graphos',
      'crowdfight'
   ]
```

Edit the ALLOWED_HOSTS for granting access to the website

Edit the internationalization options
```python
     LANGUAGE_CODE = 'it-it'
     TIME_ZONE = 'CET'
     USE_I18N = True
     USE_L10N = True
     USE_TZ = True
```

Edit the serializer for allowing JSON serialization of the images
```python
     SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
```

Edit the paths for static and multimedia files
```python
     STATIC_ROOT = BASE_DIR + '/crowdfight/static/'
     STATIC_URL = '/static/'
     MEDIA_URL = 'media/'
     LOGIN_URL = '/login'
     LOGIN_REDIRECT_URL = '/'
```

In urls.py, add the following
```python
     from django.conf.urls import include, url
     ...
     urlpatterns = [
     	...
     	url(r'^', include('crowdfight.urls'))
     ]
```

Migrate the database
```bash
	python manage.py migrate
```

Run the server
```bash
	python manage.py runserver
```
