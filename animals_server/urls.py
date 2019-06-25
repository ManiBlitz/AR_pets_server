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

    # Post functions URLs
    path('user_register', views.register_user),                                     # INSERTED
    path('action_save', views.save_user_actions),                                   # INSERTED
    path('app_retention_save', views.save_app_retention),                           # INSERTED

]

urlpatterns = format_suffix_patterns(urlpatterns)
