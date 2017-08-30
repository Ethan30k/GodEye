#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.conf.urls import url, include
from monitor import api_views

urlpatterns = [
    url(r'client/config/(\d+)$', api_views.client_config),
]
