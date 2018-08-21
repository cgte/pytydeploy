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



def main(filepath=None, dry_run=True, lastcommand=False, lasthost=False,
         reverse=False):

    targets = yamlpath2dict(filepath)[:: -1 if reverse else 1]
    if lasthost or lastcommand:
        targets = targets[-1:]
    commands = command_buckets(targets)
    if lastcommand:
        commands = commands[-1:]
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
    parser.add_argument('--lastcommand', action='store_const', default=False,
                        const=True,
                        help='Only run the last command, mostly fo tuning')
    parser.add_argument('--lasthost', action='store_const', default=False,
                        const=True,
                        help='Only run commands for the last host, mostly for tuning')
    parser.add_argument('--reverse', '-r', action='store_const', default=False,
                        const=True, help="Reverses the target list. but not commands")

    args = parser.parse_args()
    main(**args.__dict__)
