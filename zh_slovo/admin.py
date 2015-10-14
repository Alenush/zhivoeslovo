from django.contrib import admin

from .models import Dict_text, Annotate_text, Errors_in_text

# Register your models here.
admin.site.register(Dict_text)
admin.site.register(Annotate_text)
admin.site.register(Errors_in_text)