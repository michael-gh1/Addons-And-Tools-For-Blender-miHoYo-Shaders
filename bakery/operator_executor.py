import bpy  # IDE flags this as unused, but this is used when executing Operators


class OperatorExecutor:
    def __init__(self, operator_name, **kwargs):
        self.operator_name = operator_name
        print(kwargs)
        self.parameters = kwargs if kwargs else {}

    def execute(self):
        operator_to_execute = eval(self.operator_name)
        print(operator_to_execute)

        operator_to_execute(
            'EXEC_DEFAULT',
            **self.parameters
        )
