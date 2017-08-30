from django.db import models


# Create your models here.


class Host(models.Model):
    hostname = models.CharField(max_length=64, unique=True)
    ip_addr = models.GenericIPAddressField(unique=True)
    agent_choices = ((0, 'snmp'),
                     (1, 'agent'),
                     )
    agent_type = models.SmallIntegerField(choices=agent_choices)
    templates = models.ManyToManyField("Template", blank=True)
    status_choices = ((0, "Unkown"),
                      (1, "OK"),
                      (2, "Problem"),
                      (3, "Down"),
                      )
    status = models.SmallIntegerField(choices=status_choices, default=0)
    enabled = models.BooleanField(default=True)


class Service(models.Model):
    """store all the avaliable monitor services"""
    name = models.CharField(max_length=64, unique=True)
    interval = models.PositiveIntegerField(default=60, verbose_name="监控间隔")
    plugin_name = models.CharField(max_length=64, unique=True)
    indexs = models.ManyToManyField("ServiceIndex", blank=True)


class ServiceIndex(models.Model):
    """存储每个服务的指标信息"""
    name = models.CharField(max_length=64, unique=True)
    data_type_choice = ((0, "int"),
                        (1, "str"),
                        )
    data_type = models.PositiveIntegerField(choices=data_type_choice, default=0)


class Template(models.Model):
    """一个模板存储多个服务"""
    name = models.CharField(max_length=64, unique=True)
    services = models.ManyToManyField("Service", blank=True)

