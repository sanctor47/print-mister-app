from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView, CreateView
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib import messages

from .models import PrintOrder, Material, MaterialColour, PrintOrderItem
from .forms import ModelFileCreateForm, PrintOrderItemCreateForm, PrintOrderCreateForm


class CreatePrintOrderView(CreateView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
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
        return render(request, 'print_orders/create_order.html', options)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client

        order_form = PrintOrderCreateForm({
            'client': client.pk,
            'delivery_type': request.POST.get('delivery_type'),
            'delivery_address': request.POST.get('delivery_address'),
            'comment': request.POST.get('comment'),
        })
        if not order_form.is_valid():
            return HttpResponseBadRequest("error{}".format(order_form.errors))
        order = order_form.save()
        count = 0

        # items processing
        while True:
            if "models[{}].material".format(count) not in request.POST:
                break
            model_file_form = ModelFileCreateForm(
                {"client": client.pk},
                {"file": request.FILES.get("models[{}].model_file".format(count))}
            )
            if not model_file_form.is_valid():
                order.status = PrintOrder.STATUS.ERROR
                order.save()
                return HttpResponseBadRequest("error{}".format(model_file_form.errors))
            model_file = model_file_form.save()

            order_item_form = PrintOrderItemCreateForm({
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
        messages.add_message(request, messages.INFO, "Order #{} was successfully created".format(order.pk))
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
        orders = client.print_orders.all()
        return render(request, 'print_orders/orders_history.html', {'orders': orders})


class PrintOrderConfirm(UpdateView):
    def post(self, request, pk, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponse(status_code=401)
        client = request.user.client
        try:
            order = PrintOrder.objects.get(pk=pk, client=client)
        except PrintOrder.DoesNotExist:
            return HttpResponseNotFound()
        if order.can_user_confirm():
            order.status = PrintOrder.STATUS.ORDER_CONFIRMED
            order.save(update_fields=["status"])
            return redirect('current_print_orders')
        else:
            return HttpResponseBadRequest()
