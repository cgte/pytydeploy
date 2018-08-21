import unittest


from tempfile import NamedTemporaryFile

from pytydeploy import yamlpath2dict, command_buckets, main as pytymain



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
        bucket = [{'cd': '',
                   'commands': ['ls'],
                   'host': ''}]
        import yaml
        with NamedTemporaryFile(delete=False) as f:
            f.file.write(yaml.dump(bucket).encode())

        pytymain(f.name, False)
        import os
        os.remove(f.name)


if __name__ == '__main__':
    unittest.main()
