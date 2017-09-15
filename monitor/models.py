from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Host(models.Model):
    name = models.CharField(max_length=64, unique=True)
    ip_addr = models.GenericIPAddressField(unique=True)
    host_groups = models.ManyToManyField('HostGroup', blank=True)
    templates = models.ManyToManyField("Template", blank=True)
    monitored_by_choices = (
        ('agent', 'Agent'),
        ('snmp', 'SNMP'),
        ('wget', 'WGET'),
    )
    monitored_by = models.CharField(max_length=64, choices=monitored_by_choices, verbose_name='监控方式')
    status_choices = (
        (1, 'Online'),
        (2, 'Down'),
        (3, 'Unreachable'),
        # (4, 'Offline'),
        (5, 'Problem'),
    )
    host_alive_check_interval = models.IntegerField(default=30, verbose_name="主机存活状态监测间隔")
    status = models.IntegerField(choices=status_choices, default=1, verbose_name="状态")
    memo = models.TextField(blank=True, null=True, verbose_name="备注")

    def __str__(self):
        return "%s" % self.name


class HostGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    templates = models.ManyToManyField("Template", blank=True)
    memo = models.TextField("备注", blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class Service(models.Model):
    """store all the avaliable monitor services"""
    name = models.CharField(max_length=64, unique=True, verbose_name="服务名称")
    interval = models.PositiveIntegerField(default=60, verbose_name="监控间隔")
    plugin_name = models.CharField(max_length=64, unique=True, verbose_name="插件名")
    items = models.ManyToManyField("ServiceIndex", blank=True, verbose_name="指标列表")
    has_sub_service = models.BooleanField(default=False, help_text="如果一个服务还有独立的子服务，选择这个，比如网卡服务有多个独立的子网卡")
    memo = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class ServiceIndex(models.Model):
    """存储每个服务的指标信息"""
    name = models.CharField(max_length=64)  # linux cpu idle
    key = models.CharField(max_length=64, unique=True)  # idle
    data_type_choice = (
        ("int", "int"),
        ("float", "float"),
        ("str", "string"),
    )
    data_type = models.CharField(max_length=32, choices=data_type_choice, default="int", verbose_name="指标数据类型")
    memo = models.CharField(max_length=128, blank=True, null=True, verbose_name="备注")

    def __str__(self):
        return "%s.%s" % (self.name, self.key)


class Template(models.Model):
    """一个模板存储多个服务"""
    name = models.CharField(max_length=64, unique=True, verbose_name="模板名称")
    services = models.ManyToManyField("Service", blank=True, verbose_name="服务列表")

    def __str__(self):
        return "%s" % self.name


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class Trigger(models.Model):
    """触发器"""
    name = models.CharField(max_length=64, blank=True, null=True)
    template = models.ForeignKey("Template")
    severity_choice = (
        (0, "info"),
        (1, "Warning"),
        (2, "Average"),
        (3, "Critical"),
        (4, "Diaster"),
    )
    severity = models.SmallIntegerField(default=0, choices=severity_choice)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TriggerExpression(models.Model):
    """触发器表达式"""
    trigger = models.ForeignKey("Trigger")
    service = models.ForeignKey("Service")
    service_index = models.CharField(max_length=64)
    operator_choice = (
        ("gt", ">"),
        ("lt", "<"),
        ("eq", "=")
    )
    operator = models.CharField(choices=operator_choice, max_length=32)
    data_calc_func_choices = (
        ("avg", "平均值"),
        ("max", "最大值"),
        ("min", "最小值"),
        ("hit", "HIT"),
        ("last", "最近的值"),
    )
    data_calc_func = models.CharField(max_length=64, choices=data_calc_func_choices)
    calc_func_args = models.CharField(max_length=64, verbose_name="函数的非固定参数,json格式")
    threshold = models.IntegerField(verbose_name="阈值")
    logic_choices = (
        (0, "AND"),
        (1, "OR")
    )
    login_with_next = models.SmallIntegerField(choices=logic_choices)

    def __str__(self):
        return "%s" % self.trigger