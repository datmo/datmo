from datmo.util.exceptions import ClassMethodNotFound

class CLIBaseCommand(object):
    def __init__(self, cli_helper, parser):
        self.cli = cli_helper
        self.parser = parser

    def parse(self, args):
        self.args =  self.parser.parse_args(args)

    def execute(self):
        """
        Calls the method if it exists on this object, otherwise
        call a default method name (module name)

        Raises
        ------
        ClassMethodNotFound
            If the Class method is not found

        """
        command_args = vars(self.args).copy()
        # use command name if it exists,
        # otherwise use the module name
        method = getattr(self, getattr(self.args, 'command', self.args.command))
        # remove extraneous options that the method should need to care about
        if 'module' in command_args:
            del command_args['module']
        if 'command' in command_args:
            del command_args['command']

        if method is None:
            raise ClassMethodNotFound('Method %s.%s not found' % (self.args.command, method))

        method(**command_args)