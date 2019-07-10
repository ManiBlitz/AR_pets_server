from django.db import models


class User(models.Model):
    user_ip = models.CharField(max_length=200, blank=True)
    user_code = models.CharField(max_length=40, unique=True)
    date_creation = models.DateField(auto_now_add=True)
    user_ipinfo_all = models.TextField(blank=True)
    user_country = models.CharField(max_length=200, blank=True)
    user_city = models.CharField(max_length=200, blank=True)
    is_developer = models.BooleanField(default=False)


class Stats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp_detect = models.DateTimeField(auto_now_add=True)
    health_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    health_max = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    happiness_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    happiness_max = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    thirst_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    thirst_max = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    hunger_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    hunger_max = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    strenght_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    strenght_max = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    stamina_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    stamina_max = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    points_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)
    xp_level = models.DecimalField(default=0.0, decimal_places=5, max_digits=10)


class Action(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stat = models.ForeignKey(Stats, on_delete=models.CASCADE)
    button_identifier = models.CharField(max_length=200)
    timestamp_detect = models.DateTimeField(auto_now_add=True)


class AppRetention(models.Model):
    type_action = models.BooleanField(default=True)  # This is set to true for open, False for close
    timestamp_detect = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stat = models.ForeignKey(Stats, on_delete=models.CASCADE)


# =====================================================
# Models linked to the user connection to the dashboard
# =====================================================

class StaffProfile(models.Model):
    code = models.CharField(max_length=40, unique=True)
    date_creation = models.DateField(auto_now_add=True)
    user_name = models.CharField(max_length=200, blank=False, unique=True)
    ipinfo_all = models.TextField(blank=True)
    auth_level = models.IntegerField(default=1)
    email = models.EmailField(unique=True)
    pwd = models.CharField(max_length=200, blank=False)
    last_pwd_change = models.DateTimeField()


class ConnectLog(models.Model):
    ipinfo_all = models.TextField(blank=True)
    username_used = models.CharField(max_length=200, blank=False)
    time_collect = models.DateTimeField(auto_now_add=True)
    connection_result = models.BooleanField(default=False)


class Alert(models.Model):
    connect_log = models.ForeignKey(ConnectLog, on_delete=models.CASCADE)
    type_alert = models.CharField(max_length=200, blank=False)
    log_time = models.DateTimeField(auto_now_add=True)
    visited = models.BooleanField(default=False)
    threat_level = models.IntegerField(default=0)
    ip_computer = models.CharField(max_length=200)

    # We will have three distinct threat levels that are 0 for info, 1 for warning and 2 for danger
    # The type alert is of four types:
    # -- Three logging attempts lock (threat level 1)
    # -- Logging from unidentified machine (threat level 1 if mistake, threat level 2 if success)
    # -- 10 random unsuccessful logging from particular IP addresses (threat level 0)
    # -- 5 random unsuccessful logging within the same minute (threat level 2)

    # ==> Each action triggering an Alert will lock the designated IP for an hour
    # ==> All alerts will be sent to the level 3 and 2 users
