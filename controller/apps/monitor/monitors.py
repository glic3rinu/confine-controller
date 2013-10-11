import json
import re
from functools import partial

from django.utils import timezone

from controller.utils.system import run

from . import settings
from .models import TimeSerie


run = partial(run, display=False)


class Monitor(object):
    """ Base class for monitors """
    type = None
    verbose_name = None
    cmd = None
    num_processes = False
    has_graph = True
    relativity_fields = []
    average_fields = []
    
    def __init__(self, **kwargs):
        self.name = self.type
        if kwargs:
            self.verbose_name = self.verbose_name % kwargs
            if self.cmd:
                self.cmd = self.cmd % kwargs
            for key,value in kwargs.iteritems():
                setattr(self, key, value)
    
    @property
    def last(self):
        try:
            return TimeSerie.objects.last(name=self.name)
        except TimeSerie.DoesNotExist:
            return None
    
    @property
    def series(self):
        return TimeSerie.objects.filter(name=self.name)
    
    def execute(self):
        return json.loads(run(self.cmd).stdout), []
    
    def store(self, value):
        TimeSerie.objects.create(name=self.name, value=value)
    
    def apply_relativity(self, current, previous):
        if previous:
            seconds = (current.date-previous.date).total_seconds()
            previous_value = previous.value
        if self.relativity_fields:
            current_value = current.value
            for field in self.relativity_fields:
                current_value['current-%s' % field] = None
                if previous:
                    if field in current_value and field in previous_value:
                        c = current_value.get(field)
                        p = previous_value.get(field)
                        if p and c > p:
                            c = (c-p) / seconds
                            current_value['current-%s' % field] = c
            current.value = current_value
    
    def aggregate(self, series):
        value = {}
        num = {}
        for serie in series:
            for key in self.average_fields:
                # Work around null values
                if key in serie.value:
                    v = serie.value[key]
                    if not key in value:
                        value[key] = v
                        num[key] = 1
                    elif v:
                        value[key] = value[key]+v if value[key] else v
                        num[key] += 1
        for key in self.average_fields:
            try:
                if num[key] and value[key]:
                    value[key] = value[key]/num[key]
            except KeyError:
                value[key] = None
        for key in self.relativity_fields:
            try:
                value[key] = serie.value[key]
            except KeyError:
                value[key] = None
        processed_fields = self.relativity_fields+self.average_fields
        for key in set(serie.value.keys())-set(processed_fields):
            value[key] = serie.value[key]
        return TimeSerie(date=serie.date, name=serie.name, value=value)


class BasicNetMonitor(Monitor):
    type = 'basicnet'
    verbose_name = 'Network IO (%(iface)s)'
    relativity_fields = ['RX', 'TX']
    cmd = (
        'grep %(iface)s /proc/net/dev | awk {\'print "{'
        ' \\"RX\\": "$2",'
        ' \\"TX\\": "$10"'
        '}"\'}'
    )


class LoadAvgMonitor(Monitor):
    type = 'loadavg'
    verbose_name = 'CPU Load avg'
    average_fields = ['1min', '5min', '15min']
    cmd = (
        'cat /proc/loadavg | awk -F " |/" {\'print "{'
        ' \\"1min\\": "$1",'
        ' \\"5min\\": "$2",'
        ' \\"15min\\": "$3",'
        ' \\"scheduled\\": "$4", '
        ' \\"total\\": "$5" '
        '}"\'}'
    )


class FreeMonitor(Monitor):
    type = 'memory'
    verbose_name = 'Memory Usage'
    average_fields = ['total', 'real-used', 'shared', 'buffers', 'cached']
    cmd = (
        'DATA=$(free -k | tail -n3 | head -n2); '
        'echo $DATA | awk {\'print "{'
        ' \\"total\\": "$2",'
        ' \\"used\\": "$3",'
        ' \\"free\\": "$4",'
        ' \\"shared\\": "$5",'
        ' \\"buffers\\": "$6",'
        ' \\"cached\\": "$7",'
        ' \\"real-used\\": "$10",'
        ' \\"real-free\\": "$11" '
        '}"\'}'
    )


class NginxStatusMonitor(Monitor):
    type = 'nginxstatus'
    verbose_name = 'Nginx status'
    has_graph = False
    relativity_fields = ['accepted-connections', 'handled-connections', 'handled-requests']
    average_fields = ['active', 'reading', 'writing', 'waiting']
    cmd = (
        'DATA=$(wget --no-check -O - -q $(url)s); '
        'echo $DATA | awk {\'print "{'
         ' \\"accepted-connections\\": "$8",'
         ' \\"handled-connections\\": "$9",'
         ' \\"handled-requests\\": "$10",'
         ' \\"active\\": "$3",'
         ' \\"reading\\": "$12",'
         ' \\"writing\\": "$14",'
         ' \\"waiting\\": "$16" '
         '}"\'}'
    )


class Apache2StatusMonitor(Monitor):
    type = 'apache2status'
    verbose_name = 'Apache2 status'
    has_graph = False
    relativity_fields = ['handled-requests',]
    average_fields = ['active', 'reading', 'writing', 'waiting']
    cmd = (
        'DATA=$(www-browser -dump %(url)s |'
        ' awk \' /process$/ { print; exit } { print } \');'
        'SCOREBOARD=$(echo "$DATA" | egrep -v "[a,b,c,d,e,f,g,h,-]+ | ^$");'
        'echo "{'
        ' \\"handled-requests\\": $(echo "$DATA" | grep accesses | awk {\'print $3 \'}),'
        ' \\"traffic\\": \\"$(echo "$DATA" | grep Traffic | awk {\'print $7" "$8\'})\\",'
        ' \\"active\\": $(echo "$DATA" | grep idle | awk {\'print $1+$6 \'}),'
        ' \\"reading\\": $(echo $SCOREBOARD | tr -d -c "R" | wc -c),'
        ' \\"writing\\": $(echo $SCOREBOARD | tr -d -c "W" | wc -c),'
        ' \\"waiting\\": $(echo $SCOREBOARD | tr -d -c "_" | wc -c) '
        '}"'
    )


class DebugPageLoadTimeMonitor(Monitor):
    type = 'debugpageloadtime'
    verbose_name = 'Page load time (%(url)s)'
#    average_fields = ['elapsed', 'system', 'user', 'queries']
    cmd = (
        'DATA=$(wget -O - -q --no-check %(url)s --header "Accept:text/html"|grep -A1 "time</td>\|queries)");'
        'CELAPSED=$(echo "$DATA"|grep -A1 Elapsed|tail -n1|cut -d" " -f1|cut -d">" -f2);'
        'CUSER=$(echo "$DATA"|grep -A1 User|tail -n1|cut -d" " -f1|cut -d">" -f2);'
        'CSYSTEM=$(echo "$DATA"|grep -A1 System|tail -n1|cut -d" " -f1|cut -d">" -f2);'
        'QUERIES=$(echo "$DATA"|grep queries|cut -d">" -f2|cut -d" " -f1);'
        'echo "{'
        ' \\"elapsed\\": $([ $CELAPSED ] && echo $CELAPSED || echo null),'
        ' \\"user\\": $([ $CUSER ] && echo $CUSER || echo null),'
        ' \\"system\\": $([ $CSYSTEM ] && echo $CSYSTEM || echo null),'
        ' \\"queries\\": $([ $QUERIES ] && echo $QUERIES || echo null) '
        '}"'
    )


class CommandTimeMonitor(Monitor):
    type = 'commandtime'
    verbose_name = 'Command execution time'
    average_fields = ['real', 'user', 'system']
    cmd = (
        'TIMEFORMAT="%%R %%U %%S"; { time '
        '%(command)s; } 2>&1 | awk {\'print "{'
        ' \\"real\\": "$1*1000 ",'
        ' \\"user\\": "$2*1000 ",'
        ' \\"system\\": "$3*1000 " '
        '}"\'}'
    )


class NumPocessesMonitor(Monitor):
    type = 'numprocesses'
    verbose_name = 'Processes'
    num_processes = True
    has_graph = False
    
    def get_value_with_configuration(self):
        if not hasattr(self, 'value_with_configuration'):
            self.value_with_configuration = {}
            current = self.last.value
            for config in self.processes:
                name = config[0]
                self.value_with_configuration[name] = {}
                for value,config in zip(['regex', 'min', 'max'], config[1:]):
                    self.value_with_configuration[name][value] = config
                verbose = name.replace('-', ' ').replace('_', ' ').capitalize()
                self.value_with_configuration[name]['verbose'] = verbose
                self.value_with_configuration[name]['value'] = current[name]
        return self.value_with_configuration
    
    def execute(self):
        ps = run('ps -A -o pid,cmd')
        problems = []
        value = {}
        for name,regex,min_procs,max_procs in self.processes:
            processes = re.findall('\n\s*[0-9]* '+regex, ps.stdout)
            num = len(processes)
            if min_procs and num < min_procs:
                msg = 'Process %s has less than %i running instances (%i)'
                problems.append(msg % (name, min_procs, num))
            elif max_procs and num > max_procs:
                msg = 'Process %s has more than %i running instances (%i)'
                problems.append(msg % (name, man_procs, num))
            value[name] = num
        return value, problems


class ProcessesMemoryMonitor(Monitor):
    type = 'processesmemory'
    verbose_name = 'Memory consumption per process'
    cmd = 'cat /proc/{0}/statm|awk -v page="$(getconf PAGESIZE)" {{\'print $2*page\'}}'
    
    def execute(self):
        ps = run('ps -A -o pid,cmd')
        value = {}
        names = []
        for name, regex, min_procs, max_procs in self.processes:
            processes = re.findall('\n\s*[0-9]* '+regex, ps.stdout)
            value[name] = 0
            for process in processes:
                pid = int(process.strip().split(' ')[0])
                mem = run(self.cmd.format(pid)).stdout
                value[name] += int(mem) if mem else 0
            names.append(name)
        return value, []


class ProcessesCPUMonitor(ProcessesMemoryMonitor):
    type = 'processescpu'
    verbose_name = 'CPU consumption per process'
    cmd = "cat /proc/{0}/stat|awk {{'print $10+$11+$12'}}"
    
    def __init__(self, **kwargs):
        super(ProcessesCPUMonitor, self).__init__(**kwargs)
        self.relativity_fields = [ p[0] for p in self.processes ]

