from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from typing import Dict

from .serializer import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import *
from time import strftime
from datetime import timedelta
from django.utils import timezone


from .models import *

from django.utils.crypto import get_random_string
import pprint

# ---
# Constants
# ---

password_encrypt = "RSMA_002_TTYHW_0101_USREF01"
date_format = "%Y-%m-%d"
timestamp_origin = 1559390400
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


# -- Function to get the average playtime per day across the platform

@csrf_exempt
@api_view(['GET'])
def get_daily_playtime(request, format=None):
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

            # We go across all users to get their respective stats and aggregate them

            for user in users:

                for i in range(7):
                    openings_days = AppRetention.objects. \
                        filter(user=user).filter(timestamp_detect__week_day=i). \
                        order_by('timestamp_detect')

                    previous_timestamp = strftime('%Y-%m-%d %H:%M:%S', openings_days[0].timestamp_detect.timetuple())

                    for openings in openings_days:
                        if not openings.type_action:
                            time_played = int(
                                strftime('%Y-%m-%d %H:%M:%S', openings.timestamp_detect.timetuple())) - int(
                                previous_timestamp)
                            previous_timestamp = strftime('%Y-%m-%d %H:%M:%S', openings.timestamp_detect.timetuple())
                            playdays[playdays_list[i + 1]] += time_played

            playdays /= (
                users_number if users_number != 0 else 1)  # This simply divides all values by the number of players to create an average

            time_elapsed = timedelta(datetime.now().timestamp() - timestamp_origin).days / 7

            playdays /= time_elapsed  # This other division relates to the number of weeks already elapsed since the very first launch of the game

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
def get_active_players(request, format=None):
    try:
        if request.GET:

            number_active = 0
            users = User.objects.all()
            for user in users:
                number_active += 1 if AppRetention.objects.filter(user=user).order_by('-id')[0].type_action else 0

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
def get_weekly_active_players(request, format=None):
    try:
        if request.GET:

            # This variable represents the total number of unique players that opened the game at least one time
            # This means that for each player, we just need to find the first occurence of the opening for each
            # of the last seven days

            last_week = timezone.now().date() - timedelta(days=7)

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

            user_activity = AppRetention.objects.order_by('timestamp_detect').distinct('user',
                                                                                       'timestamp_detect__date').filter(
                timestamp_detect__gt=last_week)

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                new_day += timedelta(days=i)
                daily_active[str(i)] = user_activity.filter(timestamp_detect__date=new_day).count()

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


@csrf_exempt
@api_view(['GET'])
def get_average_in_game_interactions(request, format=None):
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


# @csrf_exempt
# @api_view(['GET'])
# def get_ccr(request, format=None):

# This function returns the customer churn rate
# It is the number of customers at the beginning of the week
# minus the number of customers at the end of the week
# divided by the total number of customers during that period

# to do so, we simply compile the number of players before the observation period
# along with the total number of new players over the week

@csrf_exempt
@api_view(['GET'])
def get_new_players_per_day(request, format=None):
    try:
        if request.GET:

            # This variable represents the total number of unique players that opened the game at least one time
            # This means that for each player, we just need to find the first occurence of the opening for each
            # of the last seven days

            last_week = timezone.now().date() - timedelta(days=7)

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

            new_users = User.objects.filter(date_creation__date__gt=last_week)

            # From there, we simply filter the different dates and count the number of activate player for each of them

            new_day = last_week
            for i in range(7):
                new_day += timedelta(days=i)
                daily_new[str(i)] = new_users.filter(date_creation__date=new_day).count()

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
            user.user_ip = request.ipinfo.ip
            user.user_ipinfo_all = request.ipinfo.all
            user.user_code = get_random_string(length=12)
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
    # This gives useful information on the usage and interations

    try:
        if request.POST:

            # We first store the stats of the player and catch the id of the stat
            # The stat primary key will then be used to connect the user action

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
            player_stats.stamina_level = request.POST['stamina_level']
            player_stats.xp_level = request.POST['xp_level']
            player_stats.save()

            # Once the stat is saved, we instantiate the user action to be stored

            player_action = Action()
            stat_id = player_stats.pk
            player_action.user = User.objects.get(user_code=user_code)
            player_action.stat = Stats.objects.get(pk=stat_id)
            player_action.button_identifier = request.POST['button_pressed']
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

            # We instantiate the user retention data

            player_action = AppRetention()
            user_code = request.POST['user_code']
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


# ---
# Other functions
# ---

