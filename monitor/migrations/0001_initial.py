# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-30 09:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('ip_addr', models.GenericIPAddressField(unique=True)),
                ('monitored_by', models.CharField(choices=[('agent', 'Agent'), ('snmp', 'SNMP'), ('wget', 'WGET')], max_length=64, verbose_name='监控方式')),
                ('host_alive_check_interval', models.IntegerField(default=30, verbose_name='主机存活状态监测间隔')),
                ('status', models.IntegerField(choices=[(1, 'Online'), (2, 'Down'), (3, 'Unreachable'), (5, 'Problem')], default=1, verbose_name='状态')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='服务名称')),
                ('interval', models.PositiveIntegerField(default=60, verbose_name='监控间隔')),
                ('plugin_name', models.CharField(max_length=64, unique=True, verbose_name='插件名')),
                ('has_sub_service', models.BooleanField(default=False, help_text='如果一个服务还有独立的子服务，选择这个，比如网卡服务有多个独立的子网卡')),
                ('memo', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('key', models.CharField(max_length=64, unique=True)),
                ('data_type', models.PositiveIntegerField(choices=[('int', 'int'), ('float', 'float'), ('str', 'string')], default='int', verbose_name='指标数据类型')),
                ('memo', models.CharField(blank=True, max_length=128, null=True, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='模板名称')),
                ('services', models.ManyToManyField(blank=True, to='monitor.Service', verbose_name='服务列表')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='items',
            field=models.ManyToManyField(blank=True, to='monitor.ServiceIndex', verbose_name='指标列表'),
        ),
        migrations.AddField(
            model_name='hostgroup',
            name='templates',
            field=models.ManyToManyField(blank=True, to='monitor.Template'),
        ),
        migrations.AddField(
            model_name='host',
            name='host_groups',
            field=models.ManyToManyField(blank=True, to='monitor.HostGroup'),
        ),
        migrations.AddField(
            model_name='host',
            name='templates',
            field=models.ManyToManyField(blank=True, to='monitor.Template'),
        ),
    ]
