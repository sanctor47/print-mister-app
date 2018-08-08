from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView, CreateView
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib import messages

from .models import PrintOrder, Material, MaterialColour, PrintOrderItem, PrintOrderLog
from .forms import ModelFileForm, PrintOrderItemForm, PrintOrderForm


class PrintOrderMixin(object):
    def get_options(self):
        options = {
            'delivery_types': PrintOrder.DELIVERY_TYPE_CHOICES,
            'layer_heights': PrintOrderItem.LAYER_HEIGHT_CHOICES,
            'infills': PrintOrderItem.INFILL_CHOICES,
            'shells': PrintOrderItem.SHELLS_CHOICES,
        }

        materials = {}
        for material in Material.objects.filter(enable=True):
            materials[material.id] = {'material': material}
        for colour in MaterialColour.objects.filter(enable=True, material__in=materials):
            if 'colours' not in materials[colour.material_id]:
                materials[colour.material_id]['colours'] = []
            materials[colour.material_id]['colours'].append(colour)
        options['materials'] = list(materials.values())
        return options


class CreatePrintOrderView(CreateView, PrintOrderMixin):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        options = self.get_options()
        return render(request, 'print_orders/create_order.html', options)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client

        order_form = PrintOrderForm({
            'client': client.pk,
            'delivery_type': request.POST.get('delivery_type'),
            'delivery_address': request.POST.get('delivery_address'),
            'comment': request.POST.get('comment'),
        })
        if not order_form.is_valid():
            return HttpResponseBadRequest("error{}".format(order_form.errors))
        order = order_form.save()

        # items processing
        count = 0
        while True:
            if "models[{}].material".format(count) not in request.POST:
                break
            model_file_form = ModelFileForm(
                {"client": client.pk},
                {"file": request.FILES.get("models[{}].model_file".format(count))}
            )
            if not model_file_form.is_valid():
                order.status = PrintOrder.STATUS.ERROR
                order.save()
                return HttpResponseBadRequest("error{}".format(model_file_form.errors))
            model_file = model_file_form.save()

            order_item_form = PrintOrderItemForm({
                'order': order.pk,
                'model_file': model_file.pk,
                'material': request.POST.get("models[{}].material".format(count)),
                'colour': request.POST.get("models[{}].colour".format(count)),
                'count': request.POST.get("models[{}].count".format(count)),
                'layer_height': request.POST.get("models[{}].layer_height".format(count)),
                'infill': request.POST.get("models[{}].infill".format(count)),
                'shells': request.POST.get("models[{}].shells".format(count)),
                'comment': request.POST.get("models[{}].comment".format(count)),
            })
            if not order_item_form.is_valid():
                order.status = PrintOrder.STATUS.ERROR
                order.save()
                return HttpResponseBadRequest("error{}".format(order_item_form.errors))
            order_item_form.save()
            count += 1

        PrintOrderLog.create_log(order, client)
        messages.add_message(request, messages.INFO, "Order #{} was successfully created".format(order.pk))
        return redirect('current_print_orders')


class PrintOrderEditPage(UpdateView, PrintOrderMixin):
    def get(self, request, pk=None, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client

        try:
            order = PrintOrder.objects.get(pk=pk, client=client, status=PrintOrder.STATUS.NEW)
        except PrintOrder.DoesNotExist:
            return HttpResponseNotFound()

        options = self.get_options()
        options['order'] = order
        return render(request, 'print_orders/edit_order.html', options)

    def post(self, request, pk=None, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client

        try:
            order = PrintOrder.objects.get(pk=pk, client=client, status=PrintOrder.STATUS.NEW)
        except PrintOrder.DoesNotExist:
            return HttpResponseNotFound()

        order_form = PrintOrderForm({
            'client': client.pk,
            'delivery_type': request.POST.get('delivery_type'),
            'delivery_address': request.POST.get('delivery_address'),
            'comment': request.POST.get('comment'),
        }, instance=order)
        if not order_form.is_valid():
            return HttpResponseBadRequest("error{}".format(order_form.errors))
        order = order_form.save()

        # already created items processing
        for item in order.items.all():
            if "models#{}.material".format(item.pk) not in request.POST:
                break
            if request.POST.get("models#{}.remove".format(item.pk)):
                item.delete()
            else:
                if "models#{}.model_file".format(item.pk) in request.FILES:
                    model_file_form = ModelFileForm(
                        {"client": client.pk},
                        {"file": request.FILES.get("models#{}.model_file".format(item.pk))},
                        instance=item.model_file
                    )
                    if not model_file_form.is_valid():
                        order.status = PrintOrder.STATUS.ERROR
                        order.save()
                        return HttpResponseBadRequest("error{}".format(model_file_form.errors))
                    model_file = model_file_form.save()

                order_item_form = PrintOrderItemForm({
                    'order': order.pk,
                    'model_file': item.model_file_id,
                    'material': request.POST.get("models#{}.material".format(item.pk)),
                    'colour': request.POST.get("models#{}.colour".format(item.pk)),
                    'count': request.POST.get("models#{}.count".format(item.pk)),
                    'layer_height': request.POST.get("models#{}.layer_height".format(item.pk)),
                    'infill': request.POST.get("models#{}.infill".format(item.pk)),
                    'shells': request.POST.get("models#{}.shells".format(item.pk)),
                    'comment': request.POST.get("models#{}.comment".format(item.pk)),
                }, instance=item)
                if not order_item_form.is_valid():
                    order.status = PrintOrder.STATUS.ERROR
                    order.save()
                    return HttpResponseBadRequest("error{}".format(order_item_form.errors))
                order_item_form.save()

        # new items processing
        count = 0
        while True:
            if "models[{}].material".format(count) not in request.POST:
                break
            model_file_form = ModelFileForm(
                {"client": client.pk},
                {"file": request.FILES.get("models[{}].model_file".format(count))}
            )
            if not model_file_form.is_valid():
                order.status = PrintOrder.STATUS.ERROR
                order.save()
                return HttpResponseBadRequest("error{}".format(model_file_form.errors))
            model_file = model_file_form.save()

            order_item_form = PrintOrderItemForm({
                'order': order.pk,
                'model_file': model_file.pk,
                'material': request.POST.get("models[{}].material".format(count)),
                'colour': request.POST.get("models[{}].colour".format(count)),
                'count': request.POST.get("models[{}].count".format(count)),
                'layer_height': request.POST.get("models[{}].layer_height".format(count)),
                'infill': request.POST.get("models[{}].infills".format(count)),
                'shells': request.POST.get("models[{}].shells".format(count)),
            })
            if not order_item_form.is_valid():
                order.status = PrintOrder.STATUS.ERROR
                order.save()
                return HttpResponseBadRequest("error{}".format(order_item_form.errors))
            order_item_form.save()
            count += 1

        PrintOrderLog.create_log(order, client, action_type=PrintOrderLog.ACTION_TYPE.EDITED_BY_CLIENT)
        messages.add_message(request, messages.INFO, "Order #{} was successfully changed".format(order.pk))
        return redirect('current_print_orders')


class CurrentPrintOrdersView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client
        orders = client.print_orders.filter(status__in=[
            PrintOrder.STATUS.NEW, PrintOrder.STATUS.MODEL_ACCEPTED, PrintOrder.STATUS.ORDER_CONFIRMED
        ]).order_by('-pk')
        return render(request, 'print_orders/current_orders.html', {'orders': orders})


class PrintOrdersHistoryView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client
        orders = client.print_orders.all().order_by('-pk')
        return render(request, 'print_orders/orders_history.html', {'orders': orders})


class PrintOrderDetailView(View):
    def get(self, request, pk=None, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client
        try:
            order = PrintOrder.objects.get(pk=pk, client=client)
        except PrintOrder.DoesNotExist:
            return HttpResponseNotFound()
        if order.status in [
            PrintOrder.STATUS.NEW,
            PrintOrder.STATUS.MODEL_ACCEPTED,
            PrintOrder.STATUS.ORDER_CONFIRMED,
            PrintOrder.STATUS.PRINTED,
        ]:
            return render(request, 'print_orders/current_detail_order.html', {'order': order})
        else:
            return render(request, 'print_orders/non_actual_detail_order.html', {'order': order})


class PrintOrderConfirmView(UpdateView):
    def post(self, request, pk=None, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponse(status_code=401)
        client = request.user.client
        try:
            order = PrintOrder.objects.get(pk=pk, client=client)
        except PrintOrder.DoesNotExist:
            return HttpResponseNotFound()
        if not order.can_user_confirm():
            return HttpResponseBadRequest()

        order.status = PrintOrder.STATUS.ORDER_CONFIRMED
        order.save(update_fields=["status"])
        PrintOrderLog.create_log(order, client)
        return redirect('current_print_orders')
