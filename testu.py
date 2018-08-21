import unittest
import os


from tempfile import NamedTemporaryFile

from pytydeploy import yamlpath2dict, command_buckets, main as pytymain

def buckets2file(buckets):
    import yaml
    with NamedTemporaryFile(delete=False) as f:
        f.file.write(yaml.dump(buckets).encode())
    return f


class SimpleTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        filecontent=b'''
        -
            host: "user@host"
            commands:
                - "ls"
                - "foo"
            cd: "remote_directory"

        '''
        with NamedTemporaryFile(delete=False) as f:
            f.file.write(filecontent)
        cls.path = f.name

        cls.buckets = [{'cd': 'remote_directory',
                        'commands': ['ls', 'foo'],
                        'host': 'user@host'}]

    def test1_yamlpath2dict(self):

        self.assertEqual(yamlpath2dict(self.path),
                         [{'cd': 'remote_directory',
                           'commands': ['ls', 'foo'],
                           'host': 'user@host'}])
        self.assertEqual(yamlpath2dict(self.path), self.buckets)

    def test_commands_building(self):
        self.assertEqual(command_buckets(self.buckets),
                         ['ssh user@host cd remote_directory ; ls',
                          'ssh user@host cd remote_directory ; foo']
                         )
    def test_falsee_cd(self):
        bucket = [{'cd': '',
                   'commands': ['ls', 'foo'],
                   'host': 'user@host'}]
        self.assertEqual(command_buckets(bucket),
                         ['ssh user@host ls',
                          'ssh user@host foo']
                         )
    def test_ls(self):
        """Hack to get proper coverage, if you don't specify a host runs local
        """
        buckets = [{'cd': '',
                   'commands': ['ls'],
                   'host': ''}]
        f = buckets2file(buckets)
        pytymain(f.name, False)
        os.remove(f.name)

    def test_tuning_lasthost(self):
        buckets = [{'cd': 'nevergohere',
                    'commands': ['ls', 'foo'],
                    'host': 'yazoo@dontgo'},
                   {'cd': 'there',
                    'commands': ['setup', 'install'],
                    'host': 'but'},
                    ]
        f = buckets2file(buckets)
        commands = pytymain(f.name, dry_run=True, lasthost=True)
        self.assertEqual(commands,
                         ['ssh but cd there ; setup',
                          'ssh but cd there ; install'])
        os.remove(f.name)

    def test_tuning_lastcommand(self):
        buckets = [{'cd': 'nevergohere',
                    'commands': ['ls', 'foo'],
                    'host': 'yazoo@dontgo'},
                   {'cd': 'there',
                    'commands': ['alreadyworks', 'gottafixthis'],
                    'host': 'dogo'},
                    ]
        f = buckets2file(buckets)
        commands = pytymain(f.name, dry_run=True, lastcommand=True)
        self.assertEqual(commands,
                         ['ssh dogo cd there ; gottafixthis'])
        os.remove(f.name)

    def test_tuning_lastcommand(self):
        buckets = [{'cd': 'stack',
                    'commands': ['head', 'configfile'],
                    'host': 'i@thinkbackwards'},
                   {'cd': 'icopy',
                    'commands': ['getinspration', 'laizyness'],
                    'host': 'dogo'},
                    ]
        f = buckets2file(buckets)
        commands = pytymain(f.name, dry_run=True, lastcommand=True,
                            reverse=True)
        self.assertEqual(commands,
                         ['ssh i@thinkbackwards cd stack ; configfile'])
        os.remove(f.name)

if __name__ == '__main__':
    unittest.main()
