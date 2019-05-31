from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *
import smtplib
from django.utils.crypto import get_random_string
import pprint

# ---
# Constants
# ---

password_encrypt = "RSMA_002_TTYHW_0101_USREF01"
date_format = "%Y-%m-%d"
timestamp_origin = 1546000000
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

@csrf_exempt
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
        }, status=status.HTTP_204_NO_CONTENT)


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
            player_action = Action()
            user_code = request.POST['user_code']
            stat_id = request.POST['stat_id']
            player_action.user = User.objects.get(user_code=user_code)
            player_action.stat = Stats.objects.get(pk=stat_id)
            player_action.button_identifier = request.POST['button_pressed']
            player_action.save()

            pprint.pprint("Player action saved!")
            return Response({
                'action_stored': True,
                'error_message': ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'action_stored': False,
                'error_message': "Wrong request"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'action_stored': False,
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
            player_action = AppRetention()
            user_code = request.POST['user_code']
            stat_id = request.POST['stat_id']
            player_action.user = User.objects.get(user_code=user_code)
            player_action.stat = Stats.objects.get(pk=stat_id)
            player_action.type_action = request.POST['type_action']
            player_action.save()

            pprint.pprint("Player action saved!")
            return Response({
                'app_retention_stored': True,
                'error_message': ""
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'app_retention_stored': False,
                'error_message': "Wrong request"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        error_message = str(e)
        pprint.pprint(error_message)
        return Response({
            'app_retention_stored': False,
            'error_message': "Unexpected error occured"
        }, status=status.HTTP_204_NO_CONTENT)


# ---
# Other functions
# ---


def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header = 'From: %s\n' % from_addr
    message = header + message

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(login, password)
    server.sendmail(from_addr, to_addr_list, message)
    server.close()
