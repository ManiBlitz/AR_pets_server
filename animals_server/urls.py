from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [

    # Get functions URLs
    path('avg_ingame_interactions', views.get_average_in_game_interactions),        # INSERTED
    path('weekly_active_players', views.get_weekly_active_players),                 # INSERTED
    path('active_players', views.get_active_players),                               # INSERTED
    path('daily_playtime', views.get_daily_playtime),                               # INSERTED
    path('customer_churn_rate', views.get_ccr),                                     # INSERTED
    path('new_player_per_day', views.get_new_players_per_day),                      # INSERTED
    path('game_session_frequency', views.get_game_session_frequency),               # INSERTED
    path('player_retention_rate', views.get_player_retention_rate),                 # INSERTED
    path('all_users', views.get_all_users),                                         # INSERTED

    path('diet_evolution', views.get_diet_evolution_per_player),                    # INSERTED
    path('most_consumed_food', views.get_most_consumed_food),                       # INSERTED
    path('feeding_frequency', views.get_feeding_frequency),                         # INSERTED
    path('main_foods', views.get_main_game_foods),                                  # INSERTED
    path('feeding_times', views.get_feeding_times),                                 # INSERTED
    path('avg_time_between_meals', views.get_average_time_between_meals),  # INSERTED
    path('main_country_foods', views.get_main_foods_per_country),                   # INSERTED
    path('main_city_foods', views.get_main_foods_per_city),                         # INSERTED
    path('main_food_associations', views.get_main_foods_groups),  # INSERTED

    path('leaderboard', views.get_best_players),  # INSERTED
    path('players_per_country', views.get_players_per_country),  # INSERTED
    path('total_food_bought', views.get_total_bought_food),  # INSERTED

    path('staff_register', views.register_staff),  # TO_TEST
    path('staff_login', views.staff_login),  # TO_TEST

    # Post functions URLs
    path('user_register', views.register_user),                                     # INSERTED
    path('action_save', views.save_user_actions),                                   # INSERTED
    path('app_retention_save', views.save_app_retention),                           # INSERTED

]

urlpatterns = format_suffix_patterns(urlpatterns)
