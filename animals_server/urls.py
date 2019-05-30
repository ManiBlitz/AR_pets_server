from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [

    # Get functions URLs

    # Post functions URLs
    path('user_register', views.register_user),  # INSERTED
    path('action_save', views.save_user_actions),
    path('app_retention_save', views.save_app_retention),

]

urlpatterns = format_suffix_patterns(urlpatterns)
