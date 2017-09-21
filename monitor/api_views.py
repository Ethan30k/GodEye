from django.shortcuts import render, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from monitor.serializer import ClientHandler
from monitor.backends import data_optimization
from monitor.backends import redis_conn
from django.conf import settings
from monitor import models
from monitor.serializer import get_host_triggers
from monitor.backends import data_processing
from monitor import serializer
from monitor import graphs

# Create your views here.

REDIS_OBJ = redis_conn.redis_conn(settings)
print(REDIS_OBJ.set("test", 12234))


def client_config(request, client_id):
    config_obj = ClientHandler(client_id)
    config = config_obj.fetch_configs()

    if config:
        return HttpResponse(json.dumps(config))


@csrf_exempt
def service_report(request):
    print("client data:", request.POST)

    if request.method == 'POST':
        # REDIS_OBJ.set("test_alex",'hahaha')
        try:
            print('host=%s, service=%s' % (request.POST.get('client_id'), request.POST.get('service_name')))
            data = json.loads(request.POST['data'])
            # print(data)
            # StatusData_1_memory_latest
            client_id = request.POST.get('client_id')
            service_name = request.POST.get('service_name')
            # 把数据存下来
            data_saveing_obj = data_optimization.DataStore(client_id, service_name, data, REDIS_OBJ)

            # redis_key_format = "StatusData_%s_%s_latest" %(client_id,service_name)
            # data['report_time'] = time.time()
            # REDIS_OBJ.lpush(redis_key_format,json.dumps(data))
            # 同时触发trigger检查
            print("-------触发trigger检查---------")
            host_obj = models.Host.objects.get(id=client_id)
            service_triggers = get_host_triggers(host_obj)

            trigger_handler = data_processing.DataHandler(settings, connect_redis=False)
            for trigger in service_triggers:
                trigger_handler.load_service_data_and_calulating(host_obj, trigger, REDIS_OBJ)
            print("service trigger::", service_triggers)

        except IndexError as e:
            print('----->err:', e)

    return HttpResponse(json.dumps("---report success---"))


def hosts_status(request):

    hosts_data_serializer = serializer.StatusSerializer(request, REDIS_OBJ)
    hosts_data = hosts_data_serializer.by_hosts()

    return HttpResponse(json.dumps(hosts_data))


def hostgroups_status(request):
    group_serializer = serializer.GroupStatusSerializer(request, REDIS_OBJ)
    group_serializer.get_all_groups_status()

    return HttpResponse('ss')


def graphs_generator(request):

    graphs_generator = graphs.GraphGenerator2(request, REDIS_OBJ)
    graphs_data = graphs_generator.get_host_graph()
    print("graphs_data", graphs_data)
    return HttpResponse(json.dumps(graphs_data))
