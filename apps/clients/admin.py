from django.contrib import admin

from .models import Client


class ClientAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", )
    search_fields = ("user__email", )
    list_display = ('user', 'full_name')


admin.site.register(Client, ClientAdmin)
