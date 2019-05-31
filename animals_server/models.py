from django.db import models


class User(models.Model):
    user_ip = models.CharField(max_length=200, unique=True)
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
