# encoding: UTF-8
from glob import glob
import operator
import sys
import subprocess
import time
from optparse import OptionParser, BadOptionError

usage = "usage: %prog [options] pid"
parser = OptionParser(usage=usage)
parser.add_option('-p','--packages',default='java',help="package names seperated by comma [default=%default]")
parser.add_option('-j', '--jdk', help='Location of JDK')
parser.add_option('-c', '--count', default=500, type='int', help='number of stacktraces to read [default=%default]')
parser.add_option('-d', '--delay', default=3, type='float', help='delay between each stacktrace in seconds [default=%default]')
parser.add_option('-s', '--show', action="store_true", help='show method usage after each stacktrace [default=%default]')

(options, args) = parser.parse_args()

patterns = options.packages.split(',')
jdk_dir = options.jdk
if options.show:
    show = True
else:
    show = False

if len(args) == 0:
    parser.print_help()
    sys.exit(2)

pid = args[0];

stack_count = options.count
stack_delay = options.delay

def print_results(results, reverse):
    blocks = [' ', '=', '-']
    all_counts = sum([v for v in results.itervalues()])
    top = sorted(results.iteritems(), key=operator.itemgetter(1), reverse=reverse)
    for method, count in top:
        resolution = 20
        num_blocks = float(count)/all_counts * resolution
        num_eights = int((int(num_blocks) - num_blocks) * len(blocks))
        print ( "(%4.1f%%) %s") % (num_blocks, method)
    time.sleep(stack_delay)
results = {}

for num_stacks in range(stack_count):
    p = subprocess.Popen([jdk_dir + '/bin/jstack', pid], stdout=subprocess.PIPE)
    threads = "".join(p.stdout.readlines()).split('\n\n')
    for thread in threads:
        if thread.find('java.lang.Thread.State: RUNNABLE') == -1:
            continue
        last_pattern = None
        last_pos = -1
        for pattern in patterns:
            start = thread.find('at ' + pattern)
            if (start != -1) and ((last_pos == -1) or (last_pos > start)):
                last_pattern = pattern
                last_pos = start

        if last_pos != -1:
            start = last_pos + len('at ')
            method = thread[start:thread.find('(', start)]
            if method not in results:
                results[method] = 0
            results[method] += 1
    if show:
        print '\n'*500
        print_results(results, False)

if not show:
	print_results(results, True)
