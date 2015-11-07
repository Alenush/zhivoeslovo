from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Dict_text, Answer_user, Errors_table

class ErrorsResource(resources.ModelResource):
    class Meta:
        model = Errors_table

class ErrorsAdmin(ImportExportModelAdmin):
    resource_class = ErrorsResource
    pass

# Register your models here.
admin.site.register(Dict_text)
admin.site.register(Errors_table, ErrorsAdmin)
admin.site.register(Answer_user)
