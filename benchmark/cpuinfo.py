import subprocess
import re


cpu_info = frozenset(subprocess.check_output('cat /proc/cpuinfo |grep -i "model name"', shell=True).decode().strip().split('\n'))
if len(cpu_info) == 1:
    cpu_info = next(iter(cpu_info))
    cpu_name = re.match(r'^.+: +(.+)$', cpu_info).group(1)
else:
    cpu_name = None
