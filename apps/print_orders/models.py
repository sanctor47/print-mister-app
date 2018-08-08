import json

from django.db import models
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder

from apps.clients.models import Client


class Material(models.Model):
    title = models.CharField("Title", max_length=255)
    enable = models.BooleanField("Enable", default=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"

    def __str__(self):
        return self.title


class MaterialColour(models.Model):
    title = models.CharField("Title", max_length=255)
    hex = models.CharField("HEX", max_length=6)
    material = models.ForeignKey(Material, verbose_name="Material", related_name="colours")
    enable = models.BooleanField("Enable", default=True)

    class Meta:
        verbose_name = "Colours"
        verbose_name_plural = "Colours"

    def __str__(self):
        return "{} ({})".format(self.title, self.material)


class PrintOrder(models.Model):
    class STATUS:
        NEW = 0
        MODEL_ACCEPTED = 10
        ORDER_CONFIRMED = 20
        PRINTED = 30
        DELIVERED = 40
        REJECTED = 100
        CANCELED = 110
        ERROR = 200
    STATUS_CHOICES = (
        (STATUS.NEW, "New"),
        (STATUS.MODEL_ACCEPTED, "Accepted"),
        (STATUS.ORDER_CONFIRMED, "Order confirmed"),
        (STATUS.PRINTED, "Printed"),
        (STATUS.DELIVERED, "Delivered"),
        (STATUS.REJECTED, "Rejected"),
        (STATUS.CANCELED, "Canceled"),
        (STATUS.ERROR, "Error")
    )

    class DELIVERY_TYPE:
        DELIVERY = 0
        PICK_UP = 1
    DELIVERY_TYPE_CHOICES = (
        (DELIVERY_TYPE.DELIVERY, "Delivery"),
        (DELIVERY_TYPE.PICK_UP, "Pick up"),
    )

    class PAYMENT_TYPE:
        CASH = 0
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE.CASH, "Cash"),
    )

    client = models.ForeignKey(Client, related_name="print_orders")
    status = models.SmallIntegerField("Status", choices=STATUS_CHOICES, default=STATUS.NEW)
    delivery_type = models.SmallIntegerField("Delivery Type", choices=DELIVERY_TYPE_CHOICES)
    delivery_address = models.TextField("Delivery Address", null=True, blank=True)
    is_paid = models.BooleanField("Is Paid", default=False)
    payment_type = models.SmallIntegerField("Payment type", choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE.CASH)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    planned_finish_date = models.DateField("Planned Finish Date", null=True, blank=True)
    finish_date = models.DateField("Finish Date", null=True, blank=True)
    comment = models.TextField("Comment", null=True, blank=True)

    def can_user_confirm(self):
        return self.status == self.STATUS.MODEL_ACCEPTED

    def can_user_edit(self):
        return self.status == self.STATUS.NEW


class ModelFile(models.Model):
    client = models.ForeignKey(Client, verbose_name=u"Client")
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    def validate_file_extension(value):
        if not value.name.endswith('.stl'):
            raise ValidationError(u'Only stl files acceptable')
    file = models.FileField('File', upload_to="clients_models_files/", validators=[validate_file_extension])


class PrintOrderItem(models.Model):
    class LAYER_HEIGHT:
        FINE = 0
        STANDARD = 1
        COURSE = 2
    LAYER_HEIGHT_CHOICES = (
        (LAYER_HEIGHT.FINE, "Fine"),
        (LAYER_HEIGHT.STANDARD, "Standard"),
        (LAYER_HEIGHT.COURSE, "Course"),
    )

    class INFILL:
        STANDARD = 10
        EXTRA = 20
        HALF = 50
        SUPER = 80
    INFILL_CHOICES = (
        (INFILL.STANDARD, "Standard (10)"),
        (INFILL.EXTRA, "Extra (20)"),
        (INFILL.HALF, "Half (50)"),
        (INFILL.SUPER, "Super (80)"),
    )

    class SHELLS:
        THIN = 1
        STANDARD = 2
        THICK = 3
    SHELLS_CHOICES = (
        (SHELLS.THIN, "Thin (1)"),
        (SHELLS.STANDARD, "Standard (2)"),
        (SHELLS.THICK, "Thick (3)"),
    )

    order = models.ForeignKey(PrintOrder, verbose_name="Order", related_name="items")
    model_file = models.ForeignKey(ModelFile, verbose_name="Model")
    material = models.ForeignKey(Material, verbose_name="Material")
    colour = models.ForeignKey(MaterialColour, verbose_name="Colour")
    one_item_price = models.DecimalField("One Item Price", max_digits=9, decimal_places=2, null=True, blank=True)
    count = models.SmallIntegerField("Count")
    layer_height = models.SmallIntegerField("Layer Height", choices=LAYER_HEIGHT_CHOICES)
    infill = models.SmallIntegerField("Infill", choices=INFILL_CHOICES)
    shells = models.SmallIntegerField("Shells", choices=SHELLS_CHOICES)
    comment = models.TextField("Comment", null=True, blank=True)

    def total_price(self):
        if self.one_item_price:
            return self.one_item_price * self.count
        else:
            return None


class PrintOrderLog(models.Model):
    class USER_TYPES:
        OPERATOR = 0
        CLIENT = 1
    USER_TYPES_CHOICES = (
        (USER_TYPES.OPERATOR, "Operator"),
        (USER_TYPES.CLIENT, "Client"),
    )

    class ACTION_TYPE:
        CREATE = 0
        EDITED_BY_CLIENT = 5
        CONFIRM = 20
    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE.CREATE, "Create"),
        (ACTION_TYPE.EDITED_BY_CLIENT, "Edited by client"),
        (ACTION_TYPE.CONFIRM, "Confirm"),
    )

    order = models.ForeignKey(PrintOrder, verbose_name="Order", related_name="logs")
    user_type = models.SmallIntegerField("User type", choices=USER_TYPES_CHOICES)
    user_id = models.IntegerField("User Id")
    action_type = models.SmallIntegerField("Action type", choices=ACTION_TYPE_CHOICES)
    dump = models.TextField("Dump", null=True, blank=True)

    @classmethod
    def create_log(self, order, user, action_type=None):
        log = PrintOrderLog()
        log.order = order
        if isinstance(user, Client):
            log.user_type = self.USER_TYPES.CLIENT
        #elif isinstance(user, Operator)
        #   log.user_type = self.USER_TYPES.OPERATOR
        log.user_id = user.pk
        log.action_type = action_type if action_type else order.status
        log.dump = json.dumps(
            list(PrintOrder.objects.filter(id=order.id).values()),
            cls=DjangoJSONEncoder
        )
        for item in order.items.all():
            log.dump += json.dumps(
                list(PrintOrderItem.objects.filter(id=item .id).values()),
                cls=DjangoJSONEncoder
            )
        log.save()
