import json
import re
from functools import partial

from controller.utils.system import run

from .settings import MONITOR_DISK_FREE_LIMIT, MONITOR_DISK_WARN_RATIO
from .models import TimeSerie
from .utils import PsTree

run = partial(run, display=False)


class Monitor(object):
    """ Base class for monitors """
    type = None
    verbose_name = None
    cmd = None
    num_processes = False
    has_graph = True
    graph = None
    relativity_fields = []
    average_fields = []
    
    def __init__(self, **kwargs):
        self.name = self.type
        if self.graph is None:
            self.graph = self.type
        if kwargs:
            self.verbose_name = self.verbose_name % kwargs
            if self.cmd:
                self.cmd = self.cmd % kwargs
            for key,value in kwargs.iteritems():
                setattr(self, key, value)
    
    @property
    def last(self):
        try:
            return TimeSerie.objects.filter(name=self.name).latest()
        except TimeSerie.DoesNotExist:
            return None
    
    @property
    def series(self):
        return TimeSerie.objects.filter(name=self.name)
    
    def execute(self):
        env = "export LINES=1000; export COLUMNS=1000; "
        result = {}
        problems = []
        try:
            result = json.loads(run(env + self.cmd).stdout)
        except ValueError as error:
            msg = "Error on monitor '%s': %s ('%s')" % (self.type, error, self.cmd)
            problems.append(msg)
            # TODO(santiago) configure logging and log this error
            #import logging
            #logger = logging.getLogger('ERROR')
            #logger.error(msg)
        return result, problems
    
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
    graph = 'basicnet'
    relativity_fields = ['RX', 'TX']
    cmd = (
       'grep %(iface)s /proc/net/dev | sed "s/^\s*//" | awk -F "[ :]*" {\'print "{'
       ' \\"RX\\": "$2",'
       ' \\"TX\\": "$10"'
       '}"\'}'
    )


class LoadAvgMonitor(Monitor):
    type = 'loadavg'
    verbose_name = 'CPU load avg'
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
    verbose_name = 'Memory usage'
    average_fields = ['total', 'real-used', 'shared', 'buffers', 'cached']
    # There is a bug in some systems and free -b does not return correct total memory
    cmd = (
        'DATA=$(free -k | tail -n3 | head -n2); '
        'echo $DATA | awk {\'print "{'
        ' \\"total\\": "$2*1024",'
        ' \\"used\\": "$3*1024",'
        ' \\"free\\": "$4*1024",'
        ' \\"shared\\": "$5*1024",'
        ' \\"buffers\\": "$6*1024",'
        ' \\"cached\\": "$7*1024",'
        ' \\"real-used\\": "$10*1024",'
        ' \\"real-free\\": "$11*1024" '
        '}"\'}'
    )


class NginxStatusMonitor(Monitor):
    type = 'nginxstatus'
    verbose_name = 'Nginx status'
    graph = 'webserverstatus'
    relativity_fields = ['accepted-connections', 'handled-connections', 'handled-requests']
    average_fields = ['active', 'reading', 'writing', 'waiting']
    cmd = (
        'DATA=$(wget --no-check -O - -q %(url)s); '
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
    graph = 'webserverstatus'
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


class NumProcessesMonitor(Monitor):
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
        problems = []
        value = {}
        for name,regex,min_procs,max_procs in self.processes:
            ps = run('ps -A -o pid,cmd | grep -E "%s" | grep -v "grep" | wc -l' % regex )
            num = int(ps.stdout)
            if min_procs and num < min_procs:
                msg = 'Process %s has less than %i running instances (%i)'
                problems.append(msg % (name, min_procs, num))
            elif max_procs and num > max_procs:
                msg = 'Process %s has more than %i running instances (%i)'
                problems.append(msg % (name, max_procs, num))
            value[name] = num
        return value, problems


class NumPocessesMonitor(NumProcessesMonitor):
    """ Typo renaming workaround (#343) """
    # FIXME: remove when confine-dist testing is merged into master
    pass


class ProcessesMemoryMonitor(Monitor):
    type = 'processesmemory'
    verbose_name = 'Memory consumption per process'
    cmd = 'cat /proc/{0}/statm|awk -v page="$(getconf PAGESIZE)" {{\'print $2*page\'}}'
    
    def execute(self):
        ps = run('ps -A -o pid,cmd')
        value = {}
        for name, regex, __, __ in self.processes:
            processes = re.findall('\n\s*([0-9]+) '+regex, ps.stdout)
            value[name] = 0
            for pid in processes:
                pid = int(pid)
                mem = run(self.cmd.format(pid)).stdout
                value[name] += int(mem) if mem else 0
        return value, []


class ProcessesCPUMonitor(ProcessesMemoryMonitor):
    type = 'processescpu'
    verbose_name = 'CPU consumption per process'
    cmd = 'cat /proc/{0}/stat|awk {{\'print $14+$15 " " $16+$17\'}}'
    
    def __init__(self, **kwargs):
        super(ProcessesCPUMonitor, self).__init__(**kwargs)
        self.relativity_fields = [ p[0] for p in self.processes ]
    
    def execute(self):
        ps = run('ps -A -o pid,ppid,cmd')
        ticks = {}
        for name, regex, __, __ in self.processes:
            processes = re.findall('\n\s*([0-9]+)\s*([0-9]+) '+regex, ps.stdout)
            pstree = PsTree()
            for pid, ppid in processes:
                pid = int(pid)
                ppid = int(ppid)
                stat = run(self.cmd.format(pid)).stdout.split(' ')
                correct = (len(stat) == 2)
                worked = int(stat[0]) if correct else 0
                waited = int(stat[1]) if correct else 0
                pstree.insert(pid, ppid, worked, waited)
            ticks[name] = pstree.total_ticks()
        return ticks, []


class DiskFreeMonitor(Monitor):
    """
        Show the disk usage and warn when free is near to the limit
        defined by rabbitmq (#326, #337)
    """

    type = 'diskfree'
    verbose_name = 'Disk free space'
    average_fields = ['total', 'used', 'free', 'use_per_cent']
    cmd = (
        'DATA=$(df -k / | tail -n 1 | sed "s/%//"); '
        'echo $DATA | awk {\'print "{'
        ' \\"total\\": "$2",'
        ' \\"used\\": "$3",'
        ' \\"free\\": "$4",'
        ' \\"use_per_cent\\": "$5"'
        '}"\'}'
    )

    def execute(self):
        problems = []
        value = json.loads(run(self.cmd).stdout)
        limit = MONITOR_DISK_FREE_LIMIT * MONITOR_DISK_WARN_RATIO
        if value['free'] < limit:
            msg = 'Low disk space left (%i), potential Rabbitiqm alarm that '\
                'will block the producer! (more info on issue report #326)'
            problems.append(msg % value['free'])
        return value, problems
