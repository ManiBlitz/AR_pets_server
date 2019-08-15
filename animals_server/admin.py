from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(AppRetention)
admin.site.register(Action)
admin.site.register(Stats)
admin.site.register(GamePoints)
admin.site.register(StaffProfile)
admin.site.register(ConnectLog)
admin.site.register(Alert)
