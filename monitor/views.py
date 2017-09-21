from django.shortcuts import render

# Create your views here.
# _*_coding:utf8_*_


from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
import json, time
# Create your views here.
from monitor.serializer import ClientHandler, get_host_triggers
import json
from monitor.backends import redis_conn
from monitor.backends import data_optimization
from monitor import models
from monitor.backends import data_processing
from monitor import serializer
from monitor import graphs

REDIS_OBJ = redis_conn.redis_conn(settings)


def dashboard(request):
    return render(request, 'monitor/dashboard.html')


def triggers(request):
    return render(request, 'monitor/triggers.html')


def hosts(request):
    host_list = models.Host.objects.all()
    print("hosts:", host_list)
    return render(request, 'monitor/hosts.html', {'host_list': host_list})


def host_detail(request, host_id):
    host_obj = models.Host.objects.get(id=host_id)
    return render(request, 'monitor/host_detail.html', {'host_obj': host_obj})


def trigger_list(request):
    host_id = request.GET.get("by_host_id")

    host_obj = models.Host.objects.get(id=host_id)

    alert_list = host_obj.eventlog_set.all().order_by('-date')
    return render(request, 'monitor/trigger_list.html', locals())


def host_groups(request):
    host_groups = models.HostGroup.objects.all()
    return render(request, 'monitor/host_groups.html', locals())
