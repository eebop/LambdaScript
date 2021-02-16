import sys
import PY

class Cancel(Exception):
    pass

class py_interface:
    def __init__(self, args):
        self.args = args

    def function(self, values, parser):
        pass

    def run(self, names):
        values = {}
        for name in self.args:
            var = names[name]
            values[name] = var
        return self.function(values, sys.modules['__main__'].parser)

    def __str__(self):
        return f'PyInterface{list(self.args)} = ' + '{}'

    def __repr__(self):
        return str(self)

class import_LScript(py_interface):
    def function(self, values, parser):
        answer = values['name']
        try:
            with open(answer) as f:
                text = f.read()
            if text[-1] == '\n':
                text = text[:-1]
            name = type(parser)(text)
            answer = parser.call(name, ())
            parser.names.update(name.names)
            return answer
        except FileNotFoundError:
            print('cannot find file %s' % answer)
            raise Cancel

    def __str__(self):
        return 'import[name] = {}'

class Exec(py_interface):
    def function(self, values, parser):
        namespace = values['namespace']
        if not namespace in ['__main__', 'py_interface']:
            namespace = 'PY'
        exec(values['code'], sys.modules[namespace].__dict__)

    def __str__(self):
        return 'exec_py[code, namespace] = {}'

class print_obj(py_interface):
    def function(self, values, parser):
        print(values['object'], end='', flush=True)

class get_input(py_interface):
    def function(self, values, parser):
        return input(values['object'])

class callable_list(py_interface):
    def __init__(self, l):
        self._list = list(l)
        py_interface.__init__(self, ('index', 'new'))

    def function(self, values, parser):
        try:
            answer = self._list[int(values['index'])]
        except ValueError:
            print('Invalid index')
        if values['new'] != None:
            self._list[int(values['index'])] = values['new']
        return answer

    def __str__(self):
        return str(self._list)

    def __add__(self, other):
        try:
            o = list(other)
        except:
            if hasattr(other, '_list'):
                o = other._list
            else:
                print('Invalid argument')
                raise Cancel
        return type(self)(self._list + o)
