from django.contrib import admin

from .models import *


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title',  'enable')
    list_filter = ('enable', )


class MaterialColourAdmin(admin.ModelAdmin):
    list_filter = ('enable', 'material')
    list_display = ('title', 'material', 'enable')


class ModelFileAdmin(admin.ModelAdmin):
    raw_id_fields = ("client", )
    search_fields = ("client__user__email", )


class PrintOrderItemInlineAdmin(admin.TabularInline):
    model = PrintOrderItem
    raw_id_fields = ("model_file", )
    fields = ("model_file", "count", "material", "colour", "one_item_price", "layer_height", "infill", "shells",
              "comment")


class PrintOrderAdmin(admin.ModelAdmin):
    list_filter = ("status", "items__material", "items__colour",)
    search_fields = ("client__email", )
    list_display = ("id", "status", "client", )
    inlines = (PrintOrderItemInlineAdmin, )


class PrintOrderLogAdmin(admin.ModelAdmin):
    search_fields = ("order__id",)
    list_filter = ("action_type", )
    list_display = ("id", "order_id", "action_type")


admin.site.register(Material, MaterialAdmin)
admin.site.register(MaterialColour, MaterialColourAdmin)
admin.site.register(PrintOrder, PrintOrderAdmin)
admin.site.register(ModelFile, ModelFileAdmin)
admin.site.register(PrintOrderLog, PrintOrderLogAdmin)
