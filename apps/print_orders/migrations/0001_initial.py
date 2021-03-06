# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-06 13:15
from __future__ import unicode_literals

import apps.print_orders.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('enable', models.BooleanField(default=True, verbose_name='Enable')),
            ],
            options={
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materials',
            },
        ),
        migrations.CreateModel(
            name='MaterialColour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('hex', models.CharField(max_length=6, verbose_name='HEX')),
                ('enable', models.BooleanField(default=True, verbose_name='Enable')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='colours', to='print_orders.Material', verbose_name='Material')),
            ],
            options={
                'verbose_name': 'Colours',
                'verbose_name_plural': 'Colours',
            },
        ),
        migrations.CreateModel(
            name='ModelFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('file', models.FileField(upload_to='clients_models_files/', validators=[apps.print_orders.models.ModelFile.validate_file_extension], verbose_name='File')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client', verbose_name='Client')),
            ],
        ),
        migrations.CreateModel(
            name='PrintOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, 'New'), (10, 'Accepted'), (20, 'Order confirmed'), (30, 'Printed'), (40, 'Delivered'), (100, 'Rejected'), (110, 'Canceled'), (200, 'Error')], default=0, verbose_name='Status')),
                ('delivery_type', models.SmallIntegerField(choices=[(0, 'Delivery'), (1, 'Pick up')], verbose_name='Delivery Type')),
                ('delivery_address', models.TextField(blank=True, null=True, verbose_name='Delivery Address')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is Paid')),
                ('payment_type', models.SmallIntegerField(choices=[(0, 'Cash')], default=0, verbose_name='Payment type')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('planned_finish_date', models.DateField(blank=True, null=True, verbose_name='Planned Finish Date')),
                ('finish_date', models.DateField(blank=True, null=True, verbose_name='Finish Date')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='print_orders', to='clients.Client')),
            ],
        ),
        migrations.CreateModel(
            name='PrintOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('one_item_price', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='One Item Price')),
                ('count', models.SmallIntegerField(verbose_name='Count')),
                ('layer_height', models.SmallIntegerField(choices=[(0, 'Fine'), (1, 'Standard'), (2, 'Course')], verbose_name='Layer Height')),
                ('infill', models.SmallIntegerField(choices=[(10, 'Standard (10)'), (20, 'Extra (20)'), (50, 'Half (50)'), (80, 'Super (80)')], verbose_name='Infill')),
                ('shells', models.SmallIntegerField(choices=[(1, 'Thin (1)'), (2, 'Standard (2)'), (3, 'Thick (3)')], verbose_name='Shells')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('colour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='print_orders.MaterialColour', verbose_name='Colour')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='print_orders.Material', verbose_name='Material')),
                ('model_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='print_orders.ModelFile', verbose_name='Model')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='print_orders.PrintOrder', verbose_name='Order')),
            ],
        ),
    ]
