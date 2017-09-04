from django.shortcuts import render, HttpResponse
import json
from monitor.serializer import ClientHandler
# Create your views here.


def client_config(request, client_id):

    config_obj = ClientHandler(client_id)
    config = config_obj.fetch_configs()

    if config:
        return HttpResponse(json.dumps(config))