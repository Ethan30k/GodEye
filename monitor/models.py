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


class TriggerExpression(models.Model):
    trigger = models.ForeignKey('Trigger', verbose_name=u"所属触发器")
    service = models.ForeignKey(Service, verbose_name=u"关联服务")
    service_index = models.ForeignKey(ServiceIndex, verbose_name=u"关联服务指标")
    specified_index_key = models.CharField(verbose_name=u"只监控专门指定的指标key", max_length=64, blank=True, null=True)
    operator_type_choices = (('eq', '='), ('lt', '<'), ('gt', '>'))
    operator_type = models.CharField(u"运算符", choices=operator_type_choices, max_length=32)
    data_calc_type_choices = (
        ('avg', 'Average'),
        ('max', 'Max'),
        ('hit', 'Hit'),
        ('last', 'Last'),
    )
    data_calc_func = models.CharField(u"数据处理方式", choices=data_calc_type_choices, max_length=64)
    data_calc_args = models.CharField(u"函数传入参数", help_text=u"若是多个参数,则用,号分开,第一个值是时间", max_length=64)
    threshold = models.IntegerField(u"阈值")

    logic_type_choices = (('or', 'OR'), ('and', 'AND'))
    logic_type = models.CharField(u"与一个条件的逻辑关系", choices=logic_type_choices, max_length=32, blank=True, null=True)

    def __str__(self):
        return "%s %s(%s(%s))" % (self.service_index, self.operator_type, self.data_calc_func, self.data_calc_args)

    class Meta:
        pass  # unique_together = ('trigger_id','service')


class Trigger(models.Model):
    name = models.CharField(u'触发器名称', max_length=64)
    severity_choices = (
        (1, 'Information'),
        (2, 'Warning'),
        (3, 'Average'),
        (4, 'High'),
        (5, 'Diaster'),
    )
    # expressions = models.ManyToManyField(TriggerExpression,verbose_name=u"条件表达式")
    severity = models.IntegerField(u'告警级别', choices=severity_choices)
    enabled = models.BooleanField(default=True)
    memo = models.TextField(u"备注", blank=True, null=True)

    def __str__(self):
        return "<serice:%s, severity:%s>" % (self.name, self.get_severity_display())


class Action(models.Model):
    """报警策略"""
    name = models.CharField(max_length=64, unique=True)
    host_groups = models.ManyToManyField('HostGroup', blank=True)
    hosts = models.ManyToManyField('Host', blank=True)
    triggers = models.ManyToManyField('Trigger', blank=True, help_text=u"想让哪些trigger触发当前报警动作")
    interval = models.IntegerField(u'告警间隔(s)', default=300)
    operations = models.ManyToManyField('ActionOperation',verbose_name="报警动作")

    recover_notice = models.BooleanField(u'故障恢复后发送通知消息', default=True)
    recover_subject = models.CharField(max_length=128, blank=True, null=True)
    recover_message = models.TextField(blank=True, null=True)

    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ActionOperation(models.Model):
    """报警动作"""
    name = models.CharField(max_length=64)
    step = models.SmallIntegerField(u"第n次告警", default=1, help_text="当trigger触发次数小于这个值时就执行这条记录里报警方式")
    action_type_choices = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('script', 'RunScript'),
    )
    action_type = models.CharField(u"动作类型", choices=action_type_choices, default='email', max_length=64)
    notifiers = models.ManyToManyField('UserProfile', verbose_name=u"通知对象", blank=True)
    _msg_format = '''Host({hostname},{ip}) service({service_name}) has issue,msg:{msg}'''

    msg_format = models.TextField(u"消息格式", default=_msg_format)

    def __str__(self):
        return self.name


class EventLog(models.Model):
    """存储报警及其它事件日志"""
    event_type_choices = ((0, '报警事件'), (1, '维护事件'))
    event_type = models.SmallIntegerField(choices=event_type_choices, default=0)
    host = models.ForeignKey("Host")
    trigger = models.ForeignKey("Trigger", blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "host%s  %s" % (self.host, self.log)


# class Trigger(models.Model):
#     """触发器"""
#     name = models.CharField(max_length=64, blank=True, null=True)
#     template = models.ForeignKey("Template")
#     severity_choice = (
#         (0, "info"),
#         (1, "Warning"),
#         (2, "Average"),
#         (3, "Critical"),
#         (4, "Diaster"),
#     )
#     severity = models.SmallIntegerField(default=0, choices=severity_choice)
#     enabled = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.name
#
#
# class TriggerExpression(models.Model):
#     """触发器表达式"""
#     trigger = models.ForeignKey("Trigger")
#     service = models.ForeignKey("Service")
#     service_index = models.CharField(max_length=64)
#     operator_choice = (
#         ("gt", ">"),
#         ("lt", "<"),
#         ("eq", "=")
#     )
#     operator = models.CharField(choices=operator_choice, max_length=32)
#     data_calc_func_choices = (
#         ("avg", "平均值"),
#         ("max", "最大值"),
#         ("min", "最小值"),
#         ("hit", "HIT"),
#         ("last", "最近的值"),
#     )
#     data_calc_func = models.CharField(max_length=64, choices=data_calc_func_choices)
#     calc_func_args = models.CharField(max_length=64, verbose_name="函数的非固定参数,json格式")
#     threshold = models.IntegerField(verbose_name="阈值")
#     logic_choices = (
#         (0, "AND"),
#         (1, "OR")
#     )
#     login_with_next = models.SmallIntegerField(choices=logic_choices)
#
#     def __str__(self):
#         return "%s" % self.trigger
#
#
# class Action(models.Model):
#     """报警策略"""
#     name = models.CharField(max_length=64)
#     triggers = models.ManyToManyField("Trigger")
#
#     recover_notice_subject = models.CharField(max_length=128)
#     recover_body = models.TextField()
#
#     interval = models.SmallIntegerField(verbose_name="报警间隔")
#
#     def __str__(self):
#         return "%s" % self.name
#
#
# class ActionOperation(models.Model):
#     """报警动作"""
#     action_type_choices = (
#         (0, "Email"),
#         (1, "WeiXin"),
#         (2, "Script"),
#     )
#     action_type = models.SmallIntegerField(default=action_type_choices)
#     step = models.SmallIntegerField(verbose_name="报警升级阈值")
#     notifiers = models.ManyToManyField("UserProfile", blank=Trigger)
#     script_name = models.CharField(max_length=128, blank=True, null=True)
