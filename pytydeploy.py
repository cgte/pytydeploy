""" Reads content from configuration and run commands on given hosts """

import shlex
import argparse

from subprocess import check_output

import yaml



def yamlpath2dict(path):
    with open(path, 'r') as f:
        content = f.read()
    return  yaml.load(content)

def generate_command(target):
    cd_ = target.get('cd', '')
    host = target['host']
    commandlist = []
    for command in target['commands']:
        if cd_:
            cd = ' cd %s ;' % cd_
        else:
            cd = ''
        if not host:
            ssh = ''
        else:
            ssh = 'ssh '
        commandlist.append('%s%s%s %s' % (ssh, host, cd, command))
    return commandlist

def command_buckets(targets):
    res=[]
    [res.extend(generate_command(target)) for target in targets]
    return res



def main(filepath=None, dry_run=True):
    targets = yamlpath2dict(filepath)
    commands = command_buckets(targets)
    for command in commands:
        print(command)
        if not dry_run:
            output = check_output(shlex.split(command))
            print(output)
            print('  ran %s' % command)
    return commands

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read file and run commands on"
                                                 " specified machines")
    parser.add_argument('--dry-run', dest='dry_run', action='store_const',
                        default=False, const=True,
                        help="Only print what commands should be run")
    parser.add_argument('-f', '--file', dest='filepath', default='example.yaml',
                        help='The file to use')
    args = parser.parse_args()
    main(**args.__dict__)
