import os


class Engine:
    def __init__(self, libraries=None, string_if_invalid='', templates_path=''):
        if libraries is None:
            self.libraries = []
        else:
            if not isinstance(libraries, list):
                raise Exception  # TODO:Not a list
            self.libraries = libraries
        self.string_if_invalid = string_if_invalid
        if templates_path == '':
            self.templates_path = os.getcwd() + '/templates'
        else:
            if not os.path.isdir(templates_path):
                raise Exception  # TODO:Not a directory

            self.templates_path = templates_path

    def load_template(self, name):
        if name.find('.') == -1:
            name += '.ptm'
        name = os.path.join(self.templates_path, name)
        if not os.path.isfile(name):
            raise Exception  # TODO:File doesn't exist
        template_contents = ''
        with open(name, 'r') as f:
            template_contents = f.read()
        return template_contents


class DefaultEngine(Engine):
    def __init__(self, path=''):
        from Strana.builtin import builtin
        super().__init__([builtin], 'Invalid method call', path)
