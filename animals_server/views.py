from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from typing import Dict

from .serializer import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import *
from time import strftime
from datetime import timedelta
from datetime import datetime
from animals import settings
from django.db.models import Count
from django.db.models import Max

import pandas as pd
from simplecrypt import encrypt, decrypt
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori

import ipinfo

from .models import *

from django.utils.crypto import get_random_string
import pprint

# ---
# Constants
# ---

password_encrypt = "RSMA_002_TTYHW_0101_USREF01"
date_format = "%m/%d/%Y %H:%M:%S"
timestamp_origin = 1560772800
valid_days_limit = 7200

# ---
# Views functions
# ---

# =====
# Get functions
# =====


# -- Function to capture general stats based on timestamp, country and city

@csrf_exempt
@api_view(['GET'])
def get_stats(request, format=None):
    # The stats values will be provided through time, country and city
    # Hence we can have agility in our data manipulation

    try:
        if request.GET:

            # We set the time limitation to match the origin timestamp
            timestamp_used = timestamp_origin
            if request.GET['time_limitation'] > timestamp_origin:
                timestamp_used = request.GET['time_limitation']

            # We will use the contains statement to assure the country and city limitation
            country_limit = request.GET['country']
            city_limit = request.GET['city']

            user_stats = Stats.objects.filter(timestamp_detect__gte=timestamp_used). \
                filter(user__country__contains=country_limit). \
                filter(user__city__contains=city_limit)

            serializer = StatsSerializer(user_stats, many=True)
            return Response(serializer.data)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to capture single user stats based on timestamp

@csrf_exempt
@api_view(['GET'])
def get_user_stat(request, format=None):
    # The stats values will be provided through time, country and city
    # Hence we can have agility in our data manipulation

    try:
        if request.GET:

            user_data = User.objects.get(user_code=request.GET['user_code'])

            # We set the time limitation to match the origin timestamp
            timestamp_used = timestamp_origin
            if request.GET['time_limitation'] > timestamp_origin:
                timestamp_used = request.GET['time_limitation']

            if __name__ == '__main__':
                user_stats = Stats.objects.filter(user=user_data). \
                    filter(timestamp_detect__gte=timestamp_used)

            serializer = StatsSerializer(user_stats, many=True)
            return Response(serializer.data)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to get all users on the platform

@csrf_exempt
@api_view(['GET'])
def get_all_users(request, format=None):

    # This functions simply gathers the user code and creation-date of each user
    # this function must not be used often as it can slowdown the server in case of large number of users
    # for security measures, we decide to limit it to the last 100 users

    try:
        if request.GET:

            users = User.objects.all()[:100]
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to get the average playtime per day across the platform

@csrf_exempt
@api_view(['GET'])
def get_daily_playtime(request, format=None):           #IN-URL
    # The daily playtime is set over the days of the week
    # It is an average of the total play time per players
    # We will consider periods that fit within single days

    # TODO: Upgrade the code and make it more efficient
    # TODO: Reformat this function to make it less dense, it can be done with less code

    try:
        if request.GET:

            # We first define a variable that keeps the total play time for each day

            playdays = {
                'monday': 0,
                'tuesday': 0,
                'wednesday': 0,
                'thursday': 0,
                'friday': 0,
                'saturday': 0,
                'sunday': 0,
            }

            playdays_list = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

            users = User.objects.all()
            users_number = users.count()
            time_elapsed = timedelta(datetime.now().timestamp() - timestamp_origin).days / (7.0*3600*24)    # provides the time elapsed in weeks
            pprint.pprint(time_elapsed)

            # We go across all users to get their respective stats and aggregate them

            for user in users:

                for i in range(7):
                    openings_days = AppRetention.objects. \
                        filter(user=user).filter(timestamp_detect__week_day=i). \
                        order_by('timestamp_detect')

                    pprint.pprint(openings_days)
                    if len(openings_days) != 0:
                        previous_timestamp = openings_days[0].timestamp_detect.timestamp()
                        pprint.pprint(previous_timestamp)

                        for openings in openings_days:
                            if not openings.type_action:
                                time_played = int(openings.timestamp_detect.timestamp()) - int(previous_timestamp)
                                pprint.pprint(time_played)
                                playdays[playdays_list[i]] += float(time_played)/float((users_number if users_number != 0 else 1)*time_elapsed)
                            previous_timestamp = openings.timestamp_detect.timestamp()

            return Response(playdays)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to gather the number of active players

@csrf_exempt
@api_view(['GET'])
def get_active_players(request, format=None):       #IN-URL
    try:
        if request.GET:

            number_active = 0
            users = User.objects.all()
            for user in users:
                if AppRetention.objects.filter(user=user).last() is not None:
                    number_active += 1 if AppRetention.objects.filter(user=user).last().type_action else 0

            return Response({
                'active_players': number_active,
            })

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to capture the number of active users over the last seven days

@csrf_exempt
@api_view(['GET'])
def get_weekly_active_players(request, format=None):    #IN-URL
    try:
        if request.GET:

            # This variable represents the total number of unique players that opened the game at least one time
            # This means that for each player, we just need to find the first occurence of the opening for each
            # of the last seven days

            last_week = datetime.now().date() - timedelta(days=7)

            daily_active = {
                '0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0,
                '6': 0,
            }

            # We collect the unique daily active players and then limit the fetch to the last 7 days

            user_activity = AppRetention.objects.filter(timestamp_detect__gt=last_week).distinct('user', 'timestamp_detect__date')

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                daily_active[str(i)] = user_activity.filter(timestamp_detect__date=new_day).count()
                new_day += timedelta(days=1)

            return Response(
                daily_active
            )

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the number of in game interactions of the player

@csrf_exempt
@api_view(['GET'])
def get_average_in_game_interactions(request, format=None):     #IN-URL
    # For this function, we want to count the number of buttons a user clicks over the course of a game session
    # This can provide useful information on the user experience and the ease of play
    # To do so, we simply count the number of actions and the number of times the app was open
    # then we proceed to a simple division

    try:
        if request.GET:

            openings_count = AppRetention.objects.filter(type_action=True).count()
            actions_count = Action.objects.all().count()

            average_in_game_interactions = actions_count / openings_count if openings_count != 0 else 0

            return Response({
                'aigi': average_in_game_interactions,
            })

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['GET'])
def get_ccr(request, format=None):          # IN-URL
    # This function returns the customer churn rate
    # It is the number of customers at the beginning of the week
    # minus the number of customers at the end of the week
    # divided by the total number of customers during that period

    # to do so, we simply compile the number of active players before the observation period
    # along with the total number of new players over the week

    try:
        if request.GET:

            last_week = datetime.now().date() - timedelta(days=7)

            active_players = AppRetention.objects.filter(timestamp_detect__date__gte=last_week).distinct('user', 'timestamp_detect__date')

            weekly_active = active_players.count()
            firstday_active = active_players.filter(timestamp_detect__date=last_week).count()
            today_active = active_players.filter(timestamp_detect__date=datetime.now().date()).count()

            ccr = float(firstday_active - today_active) / float(weekly_active) if weekly_active != 0 else 0

            return Response({
                'CCR': ccr,
            })

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the number of new players per day

@csrf_exempt
@api_view(['GET'])
def get_new_players_per_day(request, format=None):          # IN-URL
    try:
        if request.GET:

            # This variable represents the total number of unique players that opened the game at least one time
            # This means that for each player, we just need to find the first occurence of the opening for each
            # of the last seven days

            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0,
                '6': 0,
            }

            # We collect the unique daily active players and then limit the fetch to the last 7 days

            new_users = User.objects.filter(date_creation__gt=last_week)

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                pprint.pprint('new_day value = '+str(new_day.day)+'/'+str(new_day.month)+'/'+str(new_day.year))
                daily_new[str(i)] = new_users.filter(date_creation__day=new_day.day, date_creation__month=new_day.month, date_creation__year=new_day.year).count()
                new_day += timedelta(days=1)

            return Response(
                daily_new
            )

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the game session frequency

@csrf_exempt
@api_view(['GET'])
def get_game_session_frequency(request, format=None):       #IN-URL
    try:
        if request.GET:

            # This function simply assesses the number of games sessions per day of the week
            # To do so, we need to know the number of times each player starts a game per day
            # Then we split the amount over the different seven days
            # and divide each by the total number of players and the number of weeks elapsed

            playdays = {
                'monday': 0,
                'tuesday': 0,
                'wednesday': 0,
                'thursday': 0,
                'friday': 0,
                'saturday': 0,
                'sunday': 0,
            }

            playdays_list = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

            user_number = User.objects.all().count() if (User.objects.all().count() != 0) else 1
            time_elapsed = timedelta(datetime.now().timestamp() - timestamp_origin).days / (7.0*3600*24)

            for i in range(7):
                playdays[playdays_list[i]] = AppRetention.objects.filter(timestamp_detect__week_day=i).count()/(user_number * time_elapsed)

            return Response(playdays)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the player retention rate

@csrf_exempt
@api_view(['GET'])
def get_player_retention_rate(request, format=None):
    # To calculate the player retention rate, we assess the number unique players active over the last 7 days
    # And we divide each day number by the number of players that were active 7 days ago

    try:
        if request.GET:

            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0,
                '6': 0,
            }

            distinct_users = AppRetention.objects.filter(timestamp_detect__date__gte=last_week).distinct('user',
                                                                                                         'timestamp_detect__date')

            new_day = last_week
            percentage_at_beginning = distinct_users.filter(timestamp_detect__date=last_week).count()
            for i in range(7):
                daily_new[str(i)] = float(distinct_users.filter(timestamp_detect__date=new_day).count()) / (float(
                    percentage_at_beginning) if percentage_at_beginning != 0 else 1)
                new_day += timedelta(days=1)

            return Response(daily_new)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# =====
# Functions in relation with the diet
# =====

# This set of functions are designed to understand the player's diet
# The goal is to see how it improves over time
# And also give information to the developers on the game balance


# -- function to assess the evolution of a player's diet based on its most purchased foods and drinks

@csrf_exempt
@api_view(['GET'])
def get_diet_evolution_per_player(request, format=None):

    # To assess this evolution, we first need to get the user identifier
    # Then we need to get all the elements starting with "SHOP_PURCH"
    # Then we establish a count each of the last 7 days and assess the top 5 foods and drinks for each day
    # the final result is a dict with 7 entries, and within each of those entries is a 5 elements array, each being a tuple

    try:
        if request.GET:

            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': {},
                '1': {},
                '2': {},
                '3': {},
                '4': {},
                '5': {},
                '6': {},
            }

            user_analyzed = User.objects.get(user_code=request.GET['user_code'])

            purchases_week = Action.objects.filter(user=user_analyzed).filter(button_identifier__startswith="SHOP_PURCH")
            new_day = last_week
            for i in range(7):
                purchase_day = purchases_week.filter(timestamp_detect__date__lte=new_day).values('button_identifier').\
                    annotate(total=Count('button_identifier')).order_by('total')[:5]
                purchase_size = purchase_day.count()

                foods = {}
                for j in range(purchase_size):

                    foods.update(
                        {
                            'food' + str(j): {
                                'food_name': purchase_day[j]['button_identifier'].split('_')[3],
                                'count': purchase_day[j]['total']
                            }
                        }
                    )

                daily_new[str(i)] = foods

                new_day += timedelta(days=1)

            return Response(daily_new)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- function to assess the evolution of the community diet based on most purchased foods and drinks

@csrf_exempt
@api_view(['GET'])
def get_most_consumed_food(request, format=None):

    # To assess this evolution, we first need to get the user identifier
    # Then we need to get all the elements starting with "SHOP_PURCH"
    # Then we establish a count each of the last 7 days and assess the top 5 foods and drinks for each day
    # the final result is a dict with 7 entries, and within each of those entries is a 5 elements array, each being a tuple

    try:
        if request.GET:

            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': {},
                '1': {},
                '2': {},
                '3': {},
                '4': {},
                '5': {},
                '6': {},
            }

            purchases_week = Action.objects.filter(button_identifier__startswith="SHOP_PURCH")
            new_day = last_week
            for i in range(7):
                purchase_day = purchases_week.filter(timestamp_detect__date__lte=new_day).values('button_identifier').\
                    annotate(total=Count('button_identifier')).order_by('total')[:5]
                purchase_size = purchase_day.count()

                foods = {}
                for j in range(purchase_size):

                    foods.update(
                        {
                            'food' + str(j): {
                                'food_name': purchase_day[j]['button_identifier'].split('_')[3],
                                'count': purchase_day[j]['total']
                            }
                        }
                    )

                daily_new[str(i)] = foods

                new_day += timedelta(days=1)

            return Response(daily_new)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to calculate the feeding frequency

@csrf_exempt
@api_view(['GET'])
def get_feeding_frequency(request, format=None):

    # This function gives information concerning the number of times the pet is fed over the course of a game session
    # To do so, we simply count the number of times the game was open
    # And count the number of times the pet was fed

    try:
        if request.GET:

            openings = AppRetention.objects.filter(type_action=True).count()
            feedings = Action.objects.filter(button_identifier__startswith='SHOP_PURCH').count()

            frequency = feedings/openings if openings != 0 else 0

            return Response({
                'feeding_frequency': frequency
            })
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to assess main foods used in game

@csrf_exempt
@api_view(['GET'])
def get_main_game_foods(request, format=None):

    # This function finds the top 10 foods consumed in game and get their percentage
    # To do so, we first fetch and count each of the foods consummed
    # Then we group them by count
    # And finally, we establish the percentage of each of them

    try:
        if request.GET:

            foods = Action.objects.filter(button_identifier__startswith="SHOP_PURCH").values('button_identifier').\
                annotate(total=Count('button_identifier')).order_by('total')[:10]

            food_total = sum([food['total'] for food in foods])

            foods_percentage = {}

            for i in range(len(foods)):
                foods_percentage.update({
                    'food' + str(i): {
                        'food_name': foods[i]['button_identifier'].split('_')[3],
                        'count': float(foods[i]['total'])*100/float(food_total)
                    }
                })

            return Response(foods_percentage)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to get the foods used per attribute values

@csrf_exempt
@api_view(['GET'])
def get_food_used_per_stats_value(request, format=None):

    # This function gives the main foods given to the pet when the attributes values are below a particular level
    # To do so, we lookup the stats having attributes values lower or equal to those set
    # Then we look for the associated SHOP_PURCH elements
    # And finally establish a percentage count for each food element

    try:
        if request.GET:

            happiness_level = request.POST['happiness_level']
            happiness_max = request.POST['happiness_max']
            health_level = request.POST['health_level']
            health_max = request.POST['health_max']
            thirst_level = request.POST['thirst_level']
            thirst_max = request.POST['thirst_max']
            hunger_level = request.POST['hunger_level']
            hunger_max = request.POST['hunger_max']
            strenght_level = request.POST['strength_level']
            strenght_max = request.POST['strength_max']
            stamina_level = request.POST['stamina_level']
            xp_level = request.POST['xp_level']

            validated_stats = Stats.objects.filter(happiness_level__lte=happiness_level).\
                filter(happiness_max__lte=happiness_max).filter(health_level_lte=health_level).\
                filter(health_max__lte=health_max).filter(thirst_level__lte=thirst_level).\
                filter(thirst_max__lte=thirst_max).filter(hunger_level__lte=hunger_level).\
                filter(hunger_max__lte=hunger_max).filter(strenght_level__lte=strenght_level).\
                filter(strenght_max__lte=strenght_max).filter(stamina_level__lte=stamina_level).\
                filter(xp_level__lte=xp_level)

            foods_stats = {}

            for stat in validated_stats:

                player_action = Action.objects.filter(stat=stat).filter(button_identifier__startswith="SHOP_PURCH")
                if player_action.count() != 0:

                    foods_stats[player_action['button_identifier'].split('_')[3]] += 1

            return Response(foods_stats)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the feeding times

@csrf_exempt
@api_view(['GET'])
def get_feeding_times(request, format=None):

    # This function gives information concerning the feeding times
    # We gather the different hours of the days
    # and proceed to get the number of feedings at those hours
    # Once all the hours are set, we simply make an percentage calculation over the different hours

    try:
        if request.GET:

            hours_of_the_day = {}

            actions_time = Action.objects.filter(button_identifier__startswith='SHOP_PURCH').\
                values('timestamp_detect__hour').annotate(total=Count('timestamp_detect__hour')).\
                order_by('timestamp_detect__hour')

            for action_time in actions_time:

                hours_of_the_day[str(action_time['timestamp_detect__hour'])] = action_time['total']

            return Response(hours_of_the_day)

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to calculate the average time between meals

@csrf_exempt
@api_view(['GET'])
def get_average_time_between_meals(request, format=None):

    # This function takes each player and calculate the average time between each meal
    # To do so, we first collect all the different users
    # For each of them, we collect the different 'SHOP_PURCH' elements
    # Then we collect the time between individual meals
    # Once all the times are collected, we make a player average, then we compile a platform average

    try:
        if request.GET:
            users = User.objects.all()
            users_count = users.count()
            main_avg = 0
            for user in users:
                meals_user = Action.objects.filter(user=user).filter(button_identifier__startswith="SHOP_PURCH")
                total_meals = meals_user.count()

                # meals_user contains the different meals given to the pet over time
                # total_meals contains the number of meals given to the pet

                time_previous_meal = meals_user[0].timestamp_detect.timestamp() if meals_user.count() != 0 else None

                average_time = 0
                for meal_user in meals_user:

                    meal_time = timedelta(meal_user.timestamp_detect.timestamp() - time_previous_meal).days / 3600
                    average_time += (meal_time/(total_meals-1)) if total_meals > 1 else 0
                    time_previous_meal = meal_user.timestamp_detect.timestamp()
                    # average_time gives us the average time per user

                main_avg += average_time

            main_avg /= users_count if users_count != 0 else 1

            return Response({
                'average_feeding_interval': main_avg,
            })
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to get the main foods per country

@csrf_exempt
@api_view(['GET'])
def get_main_foods_per_country(request, format=None):

    # For this function, we first select a country
    # Based on that country, we apply the same functionalities present in get_main_game_foods
    # We provide the 10 best foods of the list and return the result

    try:
        if request.GET:

            country = request.GET['country_observed']

            foods = Action.objects.filter(user__country__icontains=country).filter(button_identifier__startswith="SHOP_PURCH").values('button_identifier').\
                annotate(total=Count('button_identifier')).order_by('total')[:10]

            food_total = sum([food['total'] for food in foods])

            foods_percentage = {}

            for i in range(len(foods)):
                foods_percentage.update({
                    'food' + str(i): {
                        'food_name': foods[i]['button_identifier'].split('_')[3],
                        'count': float(foods[i]['total'])*100/float(food_total)
                    }
                })

            return Response({
                'country': country,
                'foods_percentage': foods_percentage,
            })

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to get the main food per city

@csrf_exempt
@api_view(['GET'])
def get_main_foods_per_city(request, format=None):

    # Similar concept than the country one but with city

    try:
        if request.GET:

            country = request.GET['country_observed']

            foods = Action.objects.filter(user__country__icontains=country).filter(button_identifier__startswith="SHOP_PURCH").values('button_identifier').\
                annotate(total=Count('button_identifier')).order_by('total')[:10]

            food_total = sum([food['total'] for food in foods])

            foods_percentage = {}

            for i in range(len(foods)):
                foods_percentage.update({
                    'food' + str(i): {
                        'food_name': foods[i]['button_identifier'].split('_')[3],
                        'count': float(foods[i]['total'])*100/float(food_total)
                    }
                })

            return Response({
                'country': country,
                'foods_percentage': foods_percentage,
            })

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)

# -- Function to get the main foods groups

@csrf_exempt
@api_view(['GET'])
def get_main_foods_groups(request, format=None):

    # To complete this function, there are three main tasks we need to accomplish
    # We first need to collect the different food itemsets bought during each game session by each player
    # Then we apply the mlxtend processing to the data to get the groups of at least two itemsets with a
    # support greater than 0.4

    try:
        if request.GET:

            users = User.objects.all()
            items_sets = []

            for user in users:
                opening_times = AppRetention.objects.filter(user=user).filter(type_action=True)
                pprint.pprint(opening_times)
                # This variable will contain all the different opening times

                previous_opening = opening_times[0].timestamp_detect if opening_times.count() != 0 else None

                pprint.pprint('first opening set :'+str(previous_opening), indent=1)

                for opening_time in opening_times:
                    pprint.pprint(opening_time)
                    bought_items = Action.objects.\
                        filter(timestamp_detect__gte=previous_opening).\
                        filter(timestamp_detect__lte=opening_time.timestamp_detect).\
                        filter(button_identifier__startswith='SHOP_PURCH')
                    pprint.pprint(bought_items, indent=2)
                    user_session_items_list = [str(item.button_identifier).split('_')[3] for item in bought_items]
                    items_sets.append(user_session_items_list)
                    previous_opening = opening_time.timestamp_detect

            # Now that we have our sets of bough items, we apply the functions to gather frequent itemsets

            pprint.pprint('items_collected')
            te = TransactionEncoder()
            te_ary = te.fit(items_sets).transform(items_sets)
            df = pd.DataFrame(te_ary, columns=te.columns_)

            # Now we compile the values using the apriori

            frequent_items = apriori(df, min_support=0.4, use_colnames=True)
            frequent_items['length'] = frequent_items['itemsets'].apply(lambda x: len(x))
            pprint.pprint('association computed')

            association_map = frequent_items[(frequent_items['length'] >= 2) &
                                             (frequent_items['support'] >= 0.4)]

            return Response(
                association_map.to_json(orient='values')
            )
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# ========================
# -- Leaderboard functions
# ========================

# These functions wil be used to assess the best elements of gameplay and the best players on the platform
# This leaderboard will also be used with the intent of making the game more competitive and see how players
# achieve overall.

# -- Function to find the 100 best players of the game

@csrf_exempt
@api_view(['GET'])
def get_best_players(request, format=None):
    # this function is based on specific attributes of the player
    # The best player can be defined based on the points, xp, or max level of other stats
    # Those stats are based on the player last recorded statistic points

    try:
        if request.GET:

            # first we get the attribute used for classification
            # if none is sent, we use the classification by XP

            classification = request.GET['classification'] if len(request.GET) >= 2 is not None else 'xp_level'
            pprint.pprint(classification)

            stats_rank = Stats.objects.all().order_by('user', 'timestamp_detect', classification).distinct('user')[:100]

            # Using this element we have the different user with their last entries ordered by the classification
            # value defined at the beginning

            serializer = StatsSerializer(stats_rank, many=True)

            return Response(
                serializer.data
            )
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to find the number of player for each active country

@csrf_exempt
@api_view(['GET'])
def get_players_per_country(request, format=None):
    # This function assesses the number of player for each part of the globe
    # To achieve this, we simply group the different countries and count their number of players
    # This data value is intended to be represented on a map and give insight on the national popularity of the game

    try:
        if request.GET:

            countries_count = User.objects.all().values('user_country').annotate(
                player_population=Count('user_country'))

            countries_population = {}

            for country in countries_count:
                pprint.pprint(country['user_country'])
                pprint.pprint(country['player_population'])
                countries_population[str(country['user_country'])] = country['player_population']

            return Response(
                countries_population
            )
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the total amount of food bought

@csrf_exempt
@api_view(['GET'])
def get_total_bought_food(request, format=None):
    # This function gives us a view on the total number of meals bought on the platform over the last 7 days
    # To achieve this, we simply collect the last seven days of actions
    # After that, we make sure to get the SHOP_PURCH elements and group them by date then count them
    # this gives us a count of the food bought each day for the last seven days

    try:
        if request.GET:

            # This variable represents the total number of unique players that opened the game at least one time
            # This means that for each player, we just need to find the first occurence of the opening for each
            # of the last seven days

            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0,
                '6': 0,
            }

            # We collect the unique daily active players and then limit the fetch to the last 7 days

            new_purchases = Action.objects. \
                filter(timestamp_detect__gte=last_week).filter(button_identifier__startswith='SHOP_PURCH')

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                pprint.pprint(
                    'new_day value = ' + str(new_day.day) + '/' + str(new_day.month) + '/' + str(new_day.year))
                daily_new[str(i)] = new_purchases.filter(timestamp_detect__day=new_day.day,
                                                         timestamp_detect__month=new_day.month,
                                                         timestamp_detect__year=new_day.year).count()
                new_day += timedelta(days=1)

            return Response(
                daily_new
            )

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to evaluate the games over the last 7 days

@csrf_exempt
@api_view(['GET'])
def get_total_plays(request, format=None):
    # The goal is to know how many times the different activities are played over the last 7 days
    # We simply compile the play count for each of the last seven days

    try:
        if request.GET:
            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0,
                '6': 0,
            }

            # We collect the unique daily active players and then limit the fetch to the last 7 days

            game_played = GamePoints.objects.filter(time_end_game=last_week)

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                pprint.pprint(
                    'new_day value = ' + str(new_day.day) + '/' + str(new_day.month) + '/' + str(new_day.year))
                daily_new[str(i)] = game_played.filter(time_end_game__day=new_day.day,
                                                       time_end_game__month=new_day.month,
                                                       time_end_game__year=new_day.year).count()
                new_day += timedelta(days=1)

            return Response(
                daily_new
            )

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the amount of playtime for each kind of activity over the last 7 days

@csrf_exempt
@api_view(['GET'])
def get_total_plays_per_type(request, format=None):
    # The goal is to know how many times the different activities are played over the last 7 days
    # We simply compile the play count for each of the last seven days

    try:
        if request.GET:
            last_week = datetime.now().date() - timedelta(days=7)

            daily_new = {
                '0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0,
                '6': 0,
            }

            # We collect the unique daily active players and then limit the fetch to the last 7 days

            game_played = GamePoints.objects.filter(time_end_game=last_week).filter(game_type=request.GET['game_type'])

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                pprint.pprint(
                    'new_day value = ' + str(new_day.day) + '/' + str(new_day.month) + '/' + str(new_day.year))
                daily_new[str(i)] = game_played.filter(time_end_game__day=new_day.day,
                                                       time_end_game__month=new_day.month,
                                                       time_end_game__year=new_day.year).count()
                new_day += timedelta(days=1)

            return Response(
                daily_new
            )

        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['GET'])
def get_leaderboard_per_game(request, format=None):
    # The concept of this part is to get the leaderboard of the different games
    # To do so, we need to get the type of game, then we look for the top 50 scores for each game
    # We also look for the ranking of the player for the specific game

    try:
        if request.GET:

            # We get the different scores for the game
            # We order them from highest to smallest and retrieve only the top 50 of them

            games_leaders = GamePoints.objects.filter(game_type=request.GET['type_game']).order_by('-total_points')[:50]

            serializer = GamePointsSerializer(games_leaders, many=True)
            return Response(serializer.data)
        else:
            return Response({
                'error_message': 'Wrong request'
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# =====
# Post functions
# =====


# -- Function to register user values

@csrf_exempt
@api_view(['POST'])
def register_user(request, format=None):
    # This function sends back the user values to the mobile
    # Once completed, the user receives his unique ID
    # That ID will be used for any communication with the server

    try:
        if request.POST:
            user = User()
            pprint.pprint(get_client_ip(request))
            user.user_ip = get_client_ip(request)
            ip_handler = ipinfo.getHandler(access_token='eb5a13e440a0b')
            user.user_ipinfo_all = ip_handler.getDetails(user.user_ip).all
            user.user_code = get_random_string(length=12)
            user.user_country = ip_handler.getDetails(user.user_ip).country_name
            user.user_city = ip_handler.getDetails(user.user_ip).city
            user.is_developer = request.POST['is_developer']

            pprint.pprint("Pushing data out")

            user.save()

            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        else:
            return Response({
                'user_registration_result': False,
                'error_message': "Cannot get to Post"
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'user_registration_result': False,
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to register stat_value

'''@csrf_exempt
@api_view(['POST'])
def register_stat(request, format=None):
    # This function sends back the user values to the mobile
    # Once completed, the user receives his unique ID
    # That ID will be used for any communication with the server

    try:
        if request.POST:
            player_stats = Stats()
            user_code = request.POST['user_code']
            player_stats.user = User.objects.get(user_code=user_code)
            player_stats.happiness_level = request.POST['happiness_level']
            player_stats.happiness_max = request.POST['happiness_max']
            player_stats.health_level = request.POST['health_level']
            player_stats.health_max = request.POST['health_max']
            player_stats.thirst_level = request.POST['thirst_level']
            player_stats.thirst_max = request.POST['thirst_max']
            player_stats.hunger_level = request.POST['hunger_level']
            player_stats.hunger_max = request.POST['hunger_max']
            player_stats.strenght_level = request.POST['strength_level']
            player_stats.strenght_max = request.POST['strength_max']
            player_stats.xp_level = request.POST['xp_level']
            player_stats.save()

            pprint.pprint('user_stats_captured')

            serializer = StatsSerializer(player_stats, many=False)
            return Response(serializer.data)

            # The return statement sends back all the information of the user to the program
            # The program will use that ID to link the action or App retention element considered

        else:
            return Response({
                'data_stored': False,
                'error_message': "Wrong request"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'user_registration_result': False,
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)'''


# -- Function to register user actions

@csrf_exempt
@api_view(['POST'])
def save_user_actions(request, format=None):
    # Each action of the user is based on a button
    # Depending on the button and the timing of the button
    # We know what part of the game the player is exploring
    # This gives useful information on the usage and interactions

    try:
        if request.POST:

            # We first store the stats of the player and catch the id of the stat
            # The stat primary key will then be used to connect the user action

            player_stats = Stats()
            user_code = request.POST['user_code']

            if request.POST['datetime'] is not None:
                player_stats.timestamp_detect = datetime.strptime(request.POST['datetime'], date_format)
            player_stats.user = User.objects.get(user_code=user_code)
            player_stats.happiness_level = request.POST['happiness_level']
            player_stats.happiness_max = request.POST['happiness_max']
            player_stats.health_level = request.POST['health_level']
            player_stats.health_max = request.POST['health_max']
            player_stats.thirst_level = request.POST['thirst_level']
            player_stats.thirst_max = request.POST['thirst_max']
            player_stats.hunger_level = request.POST['hunger_level']
            player_stats.hunger_max = request.POST['hunger_max']
            player_stats.strenght_level = request.POST['strength_level']
            player_stats.strenght_max = request.POST['strength_max']
            player_stats.stamina_level = request.POST['stamina_level']
            player_stats.xp_level = request.POST['xp_level']
            player_stats.points_level = request.POST['points_level']
            player_stats.save()

            # Once the stat is saved, we instantiate the user action to be stored

            player_action = Action()
            stat_id = player_stats.pk

            if request.POST['datetime'] is not None:
                player_action.timestamp_detect = datetime.strptime(request.POST['datetime'], date_format)
            player_action.user = User.objects.get(user_code=user_code)
            player_action.stat = Stats.objects.get(pk=stat_id)
            player_action.button_identifier = request.POST['button_pressed']
            pprint.pprint(player_action.button_identifier)
            player_action.save()

            pprint.pprint("Player action saved!")

            return Response({
                'action_stored': True,
                'stat_saved': True,
                'error_message': ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'action_stored': False,
                'stat_saved': False,
                'error_message': "Wrong request"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'action_stored': False,
            'stat_saved': False,
            'error_message': "Unexpected error occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to register user actions

@csrf_exempt
@api_view(['POST'])
def save_app_retention(request, format=None):
    # This view stores the opening and closing of the app
    # Simply said, we want to keep note of the player time spent playing the app
    # This can give information concerning the engagement

    try:
        if request.POST:

            # We first store the stats of the player and catch the id of the stat
            # The stat primary key will then be used to connect the user action

            player_stats = Stats()

            pprint.pprint(request.POST)

            if request.POST['datetime'] is not None:
                player_stats.timestamp_detect = datetime.strptime(request.POST['datetime'], date_format)

            user_code = request.POST['user_code']
            player_stats.user = User.objects.get(user_code=user_code)
            player_stats.happiness_level = request.POST['happiness_level']
            player_stats.happiness_max = request.POST['happiness_max']
            player_stats.health_level = request.POST['health_level']
            player_stats.health_max = request.POST['health_max']
            player_stats.thirst_level = request.POST['thirst_level']
            player_stats.thirst_max = request.POST['thirst_max']
            player_stats.hunger_level = request.POST['hunger_level']
            player_stats.hunger_max = request.POST['hunger_max']
            player_stats.stamina_level = request.POST['stamina_level']
            player_stats.strenght_level = request.POST['strength_level']
            player_stats.strenght_max = request.POST['strength_max']
            player_stats.xp_level = request.POST['xp_level']
            player_stats.points_level = request.POST['points_level']
            player_stats.save()

            # We instantiate the user retention data

            player_action = AppRetention()
            user_code = request.POST['user_code']
            if request.POST['datetime'] is not None:
                player_action.timestamp_detect = datetime.strptime(request.POST['datetime'], date_format)
            stat_id = player_stats.pk
            player_action.user = User.objects.get(user_code=user_code)
            player_action.stat = Stats.objects.get(pk=stat_id)
            player_action.type_action = request.POST['type_action']
            player_action.save()

            pprint.pprint("Player action saved!")
            return Response({
                'app_retention_stored': True,
                'stat_saved': True,
                'error_message': ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'app_retention_stored': False,
                'stat_saved': False,
                'error_message': "Wrong request"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'app_retention_stored': False,
            'stat_saved': False,
            'error_message': "Unexpected error occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to get the number of points of the player after the game

@csrf_exempt
@api_view(['POST'])
def save_game_points(request, format=None):
    # To get the total number of points, we need to fetch the score of the player
    # To do so, we just receive the game type and the total number of points of the player, along with the player info

    try:
        if request.POST:

            user = User.objects.get(user_code=request.POST['user_code'])
            game_points = GamePoints()
            game_points.user = user
            game_points.game_type = request.POST['activity_name']
            game_points.total_points = request.POST['total_points']

            game_points.save()

            return Response({
                'game_points_saved': True,
                'user_code': user.user_code,
                'total_points': game_points.total_points,
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'game_points_saved': True,
                'error_message': "Wrong request"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'game_points_saved': False,
            'error_message': "Unexpected error occured"
        }, status=status.HTTP_204_NO_CONTENT)



# -- Function to register a new user

@csrf_exempt
@api_view(['POST'])
def register_staff(request, format=None):
    # This function is set to register the users that will have access to the dashboard platform
    # Each user has a level and in front end, only level 3 can register level 2 and 1 users, and only level 2 users can
    # register level 1 users

    try:
        if request.POST:

            new_staff = StaffProfile()

            pprint.pprint(request.POST)
            ip_handler = ipinfo.getHandler(access_token='eb5a13e440a0b')
            user_ip = get_client_ip(request)

            new_staff.auth_level = request.POST['auth_level']
            new_staff.user_name = request.POST['username']
            new_staff.email = request.POST['email']
            new_staff.code = get_random_string(length=8)  # This random code will be used for retrieval purposes
            new_staff.ipinfo_all = ip_handler.getDetails(user_ip).all
            new_staff.pwd = encrypt(settings.SECRET_KEY, request.POST['pwd'])

            pprint.pprint('pushing data in')

            new_staff.save()

            return Response({
                'staff_registration_result': True
            })
        else:
            return Response({
                'staff_registration_result': False,
                'error_message': "Cannot get to Post"
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'staff_registration_result': False,
            'error_message': "Unexpected Error Occured"
        }, status=status.HTTP_204_NO_CONTENT)


# -- Function to login the staff member

@csrf_exempt
@api_view(['POST'])
def staff_login(request, format=None):
    # This function simply picks the username and the password of the player and compare them to those in machine
    # If no match, the user receives an error message, else, the player connects and a session is set in machine

    try:
        if request.POST:

            ip_handler = ipinfo.getHandler(access_token='eb5a13e440a0b')
            user_ip = get_client_ip(request)

            connect_log = ConnectLog()
            connect_log.ipinfo_all = ip_handler.getDetails(user_ip).all
            connect_log.username_used = request.POST['username']

            user_log = StaffProfile.objects.get(user_name=request.POST['username'])

            if decrypt(settings.SECRET_KEY, user_log.pwd).decode('utf8') == request.POST['pwd']:

                connect_log.connection_result = True
                connect_log.save()
                get_client_connection_log(request, connect_log)

                return Response({
                    'login': True
                })

            else:

                connect_log.connection_result = False
                connect_log.save()
                get_client_connection_log(request, connect_log)
                raise Exception('Invalid username or password')

        else:
            return Response({
                'staff_login': False,
                'error_message': "Cannot get to Post"
            }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_message = str(e)

        connect_log = ConnectLog()
        connect_log.ipinfo_all = ip_handler.getDetails(user_ip).all
        connect_log.username_used = request.POST['username']
        connect_log.connection_result = False
        connect_log.save()
        get_client_connection_log(request, connect_log)

        pprint.pprint(error_message)
        return Response({
            'staff_registration_result': False,
            'error_message': e
        })

# ---
# Other functions
# ---

# --  Function to get the user IP address


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        pprint.pprint("forwarded address is "+str(x_forwarded_for.split(',')[0]))
        ip = x_forwarded_for.split(',')[0]
        pprint.pprint(' the last most IP address is '+str(x_forwarded_for.split(',')[-1]))
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# -- Function to make login verifications concerning the client


def get_client_connection_log(request, connect_log):
    # this function assesses the four typical alert triggers of our function and pushes them in database when found
    # Each time the user connects, this process is done to define the alerts accordingly
    # We gather the last 10 logging attempts and dispatch our attention according to them

    ip_handler = ipinfo.getHandler(access_token='eb5a13e440a0b')
    user_ip = get_client_ip(request)
    ip_infoall = ip_handler.getDetails(user_ip).all

    user_logs = StaffProfile.objects.filter(ip_infoall=connect_log.ipinfo_all).count()

    if user_logs == 0:
        new_alert = Alert()
        new_alert.connect_log = connect_log
        new_alert.type_alert = "IP_UNKNOWN"
        new_alert.threat_level = 1 if not connect_log.connection_result else 2
        new_alert.ip_computer = user_ip
        new_alert.save()

    logging_records = ConnectLog.objects.filter(ipinfo_all=ip_infoall).order_by('-id')[:10][::-1]

    if len(logging_records) == 10:

        user_chain = True
        for record in logging_records:
            if record['connection_result']:
                user_chain = False
                break
        if user_chain:
            new_alert = Alert()
            new_alert.connect_log = connect_log
            new_alert.type_alert = "10_IP_INVALID"
            new_alert.threat_level = 0
            new_alert.ip_computer = user_ip
            new_alert.save()

    if len(logging_records) >= 5:

        analyzed_sequence = logging_records[-5:]

        if (analyzed_sequence[-1].timestamp() - analyzed_sequence[0]['time_collect'].timestamp()) < 60:
            new_alert = Alert()
            new_alert.connect_log = connect_log
            new_alert.type_alert = "5_ONE_MIN_INVALID"
            new_alert.threat_level = 2
            new_alert.ip_computer = user_ip
            new_alert.save()

    if len(logging_records) >= 3:

        assessed_user = connect_log.username_used
        user_found = (StaffProfile.objects.filter(user_name=assessed_user).count() != 0)

        if user_found:
            user_chain = True
            for record in logging_records[-3:]:
                if record['username_used'] != assessed_user:
                    user_chain = False
                    break
            if user_chain:
                new_alert = Alert()
                new_alert.connect_log = connect_log
                new_alert.type_alert = "3_CONS_INVALID_LOG"
                new_alert.threat_level = 0
                new_alert.ip_computer = user_ip
                new_alert.save()
