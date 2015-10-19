from django.contrib import admin

from .models import Dict_text, Answer_user, Errors_table


# Register your models here.
admin.site.register(Dict_text)
admin.site.register(Errors_table)
admin.site.register(Answer_user)