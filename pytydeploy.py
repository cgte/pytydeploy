""" Reads content from configuration and run commands on given hosts """

import shlex
import argparse

from subprocess import check_output

import yaml

parser = argparse.ArgumentParser(description="Read file and run commands on"
                                             " specified machines")

parser.add_argument('--dry-run', dest='dry_run', action='store_const',
                    default=False, const=True,
                    help="Only print what commands should be run")

parser.add_argument('-f', '--file', dest='filepath', default='example.yaml',
                    help='The file to use')


args = parser.parse_args()
dry_run = args.dry_run

with open(args.filepath, 'r') as f:
    content = f.read()

targets = yaml.load(content)

for target in targets:

    cd_ = target['cd']
    host = target['host']
    commands = target['commands']

    for command in commands:
        if cd_:
            cd = 'cd %s ;' % cd_
        else:
            cd = ''
        cmd = 'ssh %s %s %s' % (host, cd, command)
        print cmd
        if not dry_run:
            output = check_output(shlex.split(cmd))
            print output
            print '  ran %s' % command

