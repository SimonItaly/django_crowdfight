
# -*- coding: utf-8 -*-

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

import random
import logging

import datetime
from datetime import datetime, date, time, timedelta

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.template import RequestContext

from .models import User, Image, Vote
from .forms import *

# Logging features
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
logger.addHandler(ch)

if settings.DEBUG is True:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)

# Percentage function
def percentage(part, whole):
    if whole < 1:
        return 0.0
    return 100 * float(part)/float(whole)

#-------------------------------------------------------------------------------

# Index
def index(request):
    
    # Get cookie
    cookie = request.COOKIES.get('won')

    img1 = 0
    img2 = 0

    old_img1 = 0
    old_img2 = 0

    # Get old images for parsing the results
    if cookie:
        check = 0

        if 'old_img1' in request.session:
            old_img1 = request.session['old_img1']
            check += 1
        
        if 'old_img2' in request.session:
            old_img2 = request.session['old_img2']
            check += 1

        if check >= 2:    
            if cookie == '1':
                parse_winner_results(old_img1, old_img2)
            elif cookie == '2':
                parse_winner_results(old_img2, old_img1)

            old_img1.pc_win = int(round(percentage(old_img1.versus_won, old_img1.versus_total)))
            old_img1.pc_lost = 100 - old_img1.pc_win

            old_img2.pc_win = int(round(percentage(old_img2.versus_won, old_img2.versus_total)))
            old_img2.pc_lost = 100 - old_img2.pc_win

    # Generate random images
    all_images = Image.objects.all()
    size = all_images.count()
    numbers = range(0, size)

    if size >= 2:
        idx1 = random.choice(numbers)

        numbers.remove(idx1)

        idx2 = random.choice(numbers)

        img1 = all_images[idx1]
        img2 = all_images[idx2]

        logger.debug(">>>> Generazione di una nuova sfida")
        logger.debug("-------- Pool size = %d" % (size))
        logger.debug("-------- Versus = " + img1.real_name + " vs " + img2.real_name)
        logger.debug("---- Cookie \'won\' = " + (cookie if cookie else "(none)"))

    # Generate response
    response =  render(request,
                       'crowdfight/index.html',
                        { 
                        'img1' : img1,
                        'img2' : img2,
                        'debug' : settings.DEBUG,
                        'cookie_won' : cookie,
                        'old_img1' : old_img1,
                        'old_img2' : old_img2
                        })

    # Unset cookie
    response.delete_cookie('won')

    # Save old images in session
    request.session['old_img1'] = img1
    request.session['old_img2'] = img2

    return response

# Parse click on index
def parse_winner_results(img_won, img_lost):
    
    logger.debug(">>>> parse_winner_results(img_won = " + img_won.real_name + ", img_lost = " + img_lost.real_name + ")")
    
    img_won.versus_won += 1

    img_won.versus_total += 1
    img_won.score += (1.0/img_won.versus_total)
    img_won.save()

    img_lost.versus_total += 1
    img_lost.score -= (1.0/img_lost.versus_total)
    img_lost.save()

    vote = Vote.objects.create(winner_img=img_won, loser_img=img_lost)
    vote.save()

#-------------------------------------------------------------------------------

# Page 404
def page_404(request):
    response =  render(request, 'crowdfight/404.html')
    return response

#-------------------------------------------------------------------------------

# Anonymous rating pages

# All time winners (top 10)
def winners(request):
    images = Image.objects.sort_by_score(0)
    return ratings(request, images, u'Immagini più vincenti', 'won')

# All time losers (worst 10)
def losers(request):
    images = Image.objects.sort_by_score(1)
    return ratings(request, images, u'Immagini più perdenti', 'lost')

# Latest 10 images
def newest(request):
    images = Image.objects.last_ten_images()
    return ratings(request, images, u'Immagini aggiunte di recente', '')

# General function for showing a rating page
def ratings(request, images, title, showstats):

    name = 'percent'
    percent = 0

    if request.method == 'POST':
        max_show = int(request.POST.get('max_show'))
    else:
        max_show = 10

    img_count = images.count()
    images = images[0:max_show]

    if(showstats == 'won'):
        name = 'percent_won'
        percent = [0] * img_count

        for idx, img in enumerate(images):
            percent[idx] = int(percentage(img.versus_won, img.versus_total))

    elif(showstats == 'lost'):
        name = 'percent_lost'
        percent = [0] * img_count

        for idx, img in enumerate(images):
            img.versus_lost = img.versus_total - img.versus_won
            percent[idx] = int(percentage(img.versus_lost, img.versus_total))
    
    response =  render(request,
                       'crowdfight/ratings.html',
                        { 
                        'title' : title,
                        'images' : images,
                        'img_range' : range(1, img_count+1),
                        name : percent
                        })
    return response

#-------------------------------------------------------------------------------

# Most voted image of today
def top_today(request):
    query = Vote.objects.get_today_best()

    if(query):
        image_idx = query['winner_img']
        image_votes = query['total']
        logger.debug("top_today -> %d - votes = %d" % (image_idx, image_votes))
    else:
        image_idx = 0
        image_votes = -1

    return top(request, image_idx, image_votes, "Top del giorno")

# Most voted image of the month
def top_month(request):
    query = Vote.objects.get_month_best()

    if(query):
        image_idx = query['winner_img']
        image_votes = query['total']
        logger.debug("top_today -> %d - votes = %d" % (image_idx, image_votes))
    else:
        image_idx = 0
        image_votes = -1

    return top(request, image_idx, image_votes, "Top del mese")

# General function for showing a "top" image
def top(request, image_idx, image_votes, title):
    return render_image(request, image_idx, title, image_votes)

# Function for showing a requested image
def image(request, image_idx):
    return render_image(request, image_idx, '', 0)

# General function for showing the image stats
def render_image(request, image_idx, title, image_votes):
    
    deleted = False
    percent_won = 0
    percent_lost = 0

    if image_idx == 0:
        image = 0
        image_votes = -1
    else:
            
        try:
            image = Image.objects.get(img_idx=image_idx)

            image.versus_lost = image.versus_total - image.versus_won

            percent_won = int(percentage(image.versus_won, image.versus_total))
            percent_lost = int(percentage(image.versus_lost, image.versus_total))

            # Title = image name only if it's not a "top" page request
            if image_votes == 0:
                title = image.real_name

            # Delete image
            cookie = request.COOKIES.get('delete')
            if cookie:
                # Prevent image id spoofing
                if image.usr_idx.id == request.user.id and image.img_idx == int(cookie):
                    image.delete()
                    deleted = True
                    image = -1
                    image_votes = -1

        except Image.DoesNotExist:
            image = -1
            image_votes = -1

    response = render(request,
                      'crowdfight/image.html',
                        { 
                        'title' : title,
                        'image' : image,
                        'votes' : image_votes,
                        'percent_won' : percent_won,
                        'percent_lost' : percent_lost,
                        'deleted': deleted
                        })

    response.delete_cookie('delete')

    return response

#-------------------------------------------------------------------------------

from django.shortcuts import redirect

# Registration page
@csrf_protect
def register(request):

    context = 0

    logger.debug("---- register(request)")

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        logger.debug("-------- generate RegistrationForm(request.POST)")

        if form.is_valid():

            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                email = form.cleaned_data['email']
            )
            user.set_password(form.cleaned_data['password1'])
            user.save()

            context = { 'user' : user }

            logger.debug("-------- form.is_valid = true")
            logger.debug("------------ user.username = " + user.username)
            logger.debug("------------ user.email = " + user.email)

            form = 0
        else:
            logger.debug("-------- form.is_valid = false")
            user = 0
    else:
        logger.debug("-------- generate RegistrationForm()")

        form = RegistrationForm()
        user = 0
        context = { 'form' : form }
    
    return render(request, "crowdfight/register.html", context)

# Login page
@csrf_protect
def login(request):

    form = LoginForm()

    return render(
        request,
        'crowdfight/login.html',
        { 'form': form }
    )

# Logout page
@login_required
def web_logout(request):
    logout(request)
    return redirect('/')

#-------------------------------------------------------------------------------

# Profile page (own or requested)
@login_required
def profile(request, username):

    try:

        requested_user = User.objects.get(username=username)
        images = Image.objects.get_images_by_author(author=requested_user)

    except User.DoesNotExist:
        requested_user = 0
        images = 0

    response =  render(request,
                       'crowdfight/profile.html',
                        {
                        'requested_user' : requested_user,
                        'images' : images,
                        'testdata' : range(0, 14)
                        })
    return response

#-------------------------------------------------------------------------------

# Page for adding a new image
@csrf_protect
@login_required
def add_image(request):

    context = 0
    image = 0

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():

            sha = generate_sha(form.cleaned_data['image'])

            img = Image.objects.filter(sha1=sha)

            if img:
                logger.debug("Duplicate: sha1 = " + sha)
                image = -1
            else:
                image = Image.objects.create(
                    usr_idx = request.user,
                    upload = form.cleaned_data['image'],
                    real_name = form.cleaned_data['title']
                )

    form = ImageUploadForm()

    context = { 'form' : form,
                'image' : image }

    response =  render(request,
                'crowdfight/add_image.html',
                context)
    return response

#-------------------------------------------------------------------------------

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import ColumnChart
from itertools import *

# Statistics for registered users
@csrf_protect
@login_required
def stats(request):

    usr_idx = request.user.id
    images = Image.objects.sort_images_by_author(author=usr_idx)

    if images.count() >= 2:

        best_image = images.first()
        worst_image = images.last()

        best_image.versus_lost = best_image.versus_total - best_image.versus_won
        bi_pw = int(percentage(best_image.versus_won, best_image.versus_total))
        bi_pl = int(percentage(best_image.versus_lost, best_image.versus_total))

        worst_image.versus_lost = worst_image.versus_total - worst_image.versus_won
        wi_pw = int(percentage(worst_image.versus_won, worst_image.versus_total))
        wi_pl = int(percentage(worst_image.versus_lost, worst_image.versus_total))

    else:
        best_image = 0
        worst_image = 0
        bi_pw = bi_pl = 0
        wi_pw = wi_pl = 0

    search = 0
    chart = 0

    if request.method == 'POST':
        pk = request.POST.get('img_idx')
        search = Image.objects.get(img_idx=pk)

        # Form needed
        range_start = request.POST.get('range_start')
        range_end = request.POST.get('range_end')

        if range_start and range_end and range_start < range_end:
            # Search for the image in the date range
            votes_search_winning = Vote.objects.get_winning_votes_for_image_in_range(range_start, range_end, search)
            votes_search_losing = Vote.objects.get_losing_votes_for_image_in_range(range_start, range_end, search)

            # Group by date
            vsw_group = votes_search_winning.extra({'day':"date(date_vote)"}).values('day').annotate(num=Count('vote_idx'))
            vsl_group = votes_search_losing.extra({'day':"date(date_vote)"}).values('day').annotate(num=Count('vote_idx'))

            if vsw_group or vsl_group:

                '''
                logger.debug("-------- vsw_group: %d" % (vsw_group.count()))
                for v in vsw_group:
                    logger.debug("------------ votes: %s, %d" % (v['day'], v['num']))
                    data.append([v['day'], v['num'], -1])

                logger.debug("-------- vsl_group: %d" % (vsl_group.count()))
                for v in vsl_group:
                    logger.debug("------------ votes: %s, %d" % (v['day'], v['num']))
                    data.append([v['day'], -1, v['num']])
                '''

                title = "Sfide di %s dal %s al %s" % (search.real_name, range_start, range_end)

                data = [ ['Data', 'Vittorie', 'Sconfitte'] ]

                day = ''
                won = 0
                lost = 0
                nxt = 0

                # Sort the array by date, chaining won and lost
                result_list = sorted( chain(vsw_group, vsl_group), key=lambda instance: instance['day'])
                max_len = len(result_list)

                # Appending [day, won, lost] to data array
                for idx in range(0, max_len):
                    
                    if nxt == -1:
                        nxt = 0
                        continue

                    day = result_list[idx]['day']
                    won = result_list[idx]['num']
                    lost = 0

                    nxt = idx+1
                    if nxt < max_len:
                        if day == result_list[nxt]['day']:
                            lost = result_list[nxt]['num']
                            nxt = -1

                    data.append( [day, won, lost] )

                chart = ColumnChart(SimpleDataSource(data=data), heigh=270, width=580, options={'title': title})
            else:
                # No results
                chart = -1
        else:
            # Dates range is invalid
            chart = -2

    response =  render(request,
                'crowdfight/stats.html',
                { 'images' : images,
                  'best_image' : best_image,
                  'bi_pw' : bi_pw,
                  'bi_pl' : bi_pl,
                  'worst_image' : worst_image,
                  'wi_pw' : wi_pw,
                  'wi_pl' : wi_pl,
                  'chart' : chart })

    return response

#-------------------------------------------------------------------------------

# ...
def top_days(request):

    days = 0
    images = []

    if request.method == 'POST':
        try:
            days = int(request.POST.get('days'))
            if days > 100:
                days = 100

        except ValueError:
            days = 0

        if days > 0:
            d = datetime.today()

            for n in range(0, int(days)+1):
                v = Vote.objects.get_best_of_day(d.day, d.month, d.year)
                if v:
                    img_idx = v['winner_img']
                    img = Image.objects.get(img_idx=img_idx)
                    img.date = d
                    images.append(img)

                d = d - timedelta(days=1)

    ###

    response =  render(request,
                       'crowdfight/top_days.html',
                        { 
                        'images' : images,
                        'days' : days
                        })
    return response
