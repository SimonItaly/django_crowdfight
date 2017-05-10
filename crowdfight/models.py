
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

from __future__ import unicode_literals

import time
import hashlib

from datetime import datetime, date, time, timedelta

from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.db.models.signals import post_save

from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.encoding import python_2_unicode_compatible

from django.dispatch import receiver

#-------------------------------------------------------------------------------

from django.contrib.auth.models import User

#-------------------------------------------------------------------------------

class ImageManager(models.Manager):
	def sort_by_score(self, crescent):
		if(crescent):
			images = Image.objects.order_by('score').exclude(score=0)
		else:
			images = Image.objects.order_by('-score').exclude(score=0)
		return images[0:9]

	def last_ten_images(self):
		images = Image.objects.order_by('-date_pub')
		return images[0:9]

	def get_images_by_author(self, author):
		images = Image.objects.filter(usr_idx=author)
		return images

	def sort_images_by_author(self, author):
		images = Image.objects.filter(usr_idx=author).exclude(score=0).order_by('-score')
		return images

class Image(models.Model):
	#Primary key
	img_idx = models.AutoField(primary_key=True)

	#Image owner = foreign key      
	usr_idx = models.ForeignKey(User)

	#Image -> https://docs.djangoproject.com/en/1.10/ref/models/fields/#imagefield
	upload = models.ImageField(upload_to = 'crowdfight/photos/')

	sha1 = models.CharField(max_length=36)

	#Image name
	real_name = models.CharField(max_length=100)

	#Fights
	versus_won = models.IntegerField(default=0)
	versus_total = models.IntegerField(default=0)
	score = models.FloatField(default=0.0)

	#Datetime of image upload
	date_pub = models.DateTimeField('Data pubblicazione', default = timezone.now())

	objects = ImageManager()

	def save(self, *args, **kwargs):
		if not self.pk:
			sha = generate_sha(self.upload)
			self.sha1 = sha
		super(Image, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.real_name

def generate_sha(file):
	sha = hashlib.sha1()
	file.seek(0)
	while True:
		buf = file.read(104857600)
		if not buf:
			break
		sha.update(buf)
	sha1 = sha.hexdigest()
	file.seek(0)
	return sha1

#-------------------------------------------------------------------------------

class VoteManager(models.Manager):
	def last_ten_votes(self):
		qs = super(VoteManager,self).get_queryset()
		return qs.order_by('-date_vote')[0:9]

	def sort(self):
		votes = Vote.objects.order_by('winner_img', "date_vote")
		return votes

	def sort_votes(self, votes):
		votes = votes.values('winner_img').annotate(total=Count('winner_img')).order_by('-total')
		return votes

	def get_month_votes(self):
		today = datetime.today()
		votes = Vote.objects.filter(date_vote__year=today.year, date_vote__month=today.month)
		return self.sort_votes(votes)

	def get_month_best(self):
		votes = self.get_month_votes()
		if votes:
			return votes[0]
		else:
			return None

	def get_today_votes(self):
		today = datetime.today()
		return self.get_votes_of_day(today.day, today.month, today.year)

	def get_votes_of_day(self, day, month, year):
		votes = Vote.objects.filter(date_vote__year=year, date_vote__month=month, date_vote__day=day)
		return self.sort_votes(votes)

	def get_best_of_day(self, day, month, year):
		votes = self.get_votes_of_day(day, month, year)
		if votes:
			return votes[0]
		else:
			return None

	def get_today_best(self):
		votes = self.get_today_votes()
		if votes:
			return votes[0]
		else:
			return None

	def get_winning_votes_for_image_in_range(self, date_start, date_end, search):
		return Vote.objects.filter(date_vote__range=[date_start, date_end], winner_img=search)

	def get_losing_votes_for_image_in_range(self, date_start, date_end, search):
		return Vote.objects.filter(date_vote__range=[date_start, date_end], loser_img=search)

	def get_votes_in_interval(self, date_start, date_end):
		return Vote.objects.filter(date_vote__range=[date_start, date_end])

	def group_by_date(self):
		return Vote.objects.extra({'day':"date(date_vote)"}).values('day').annotate(count=Count('vote_idx'))

class Vote(models.Model):

	vote_idx = models.AutoField(primary_key=True)

	winner_img = models.ForeignKey(Image, related_name = 'Immagine1')
	loser_img = models.ForeignKey(Image, related_name = 'Immagine2')
	
	date_vote = models.DateTimeField('Data voto', default = timezone.now)

	objects = VoteManager()

	def __unicode__(self):
		return self.winner_img.real_name + " vs " + self.loser_img.real_name + "(" + self.date_vote.strftime("%Y-%m-%d %H:%M:%S") + ")"
