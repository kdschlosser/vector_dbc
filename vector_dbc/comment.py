

class Comment(str):
    _fmt = 'CM_ "{comment}" ;'

    def format(self, *args, **kwargs):
        return self._fmt.format(comment=self.replace('"', '\\"'))


class NodeComment(Comment):
    _fmt = 'CM_ BU_ {name} "{comment}" ;'

    def __init__(self, value):
        self._node = None

        try:
            super(NodeComment, self).__init__(value)
        except TypeError:
            super(NodeComment, self).__init__()

    def format(self, *args, **kwargs):
        return self._fmt.format(
            name=self._node.name,
            comment=self.replace('"', '\\"')
        )

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value


class MessageComment(Comment):
    _fmt = 'CM_ BO_ {frame_id} "{comment}" ;'

    def __init__(self, value):
        self._message = None

        try:
            super(MessageComment, self).__init__(value)
        except TypeError:
            super(MessageComment, self).__init__()

    def format(self, *args, **kwargs):
        return self._fmt.format(
            frame_id=self._message.dbc_frame_id,
            comment=self.replace('"', '\\"')
        )

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value


class SignalComment(Comment):
    _fmt = 'CM_ SG_ {frame_id} {name} "{comment}";'

    def __init__(self, value):
        self._signal = None

        try:
            super(SignalComment, self).__init__(value)
        except TypeError:
            super(SignalComment, self).__init__()

    def format(self, *args, **kwargs):
        return self._fmt.format(
            frame_id=self._signal.message.dbc_frame_id,
            name=self._signal.name,
            comment=self.replace('"', '\\"')
        )

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, value):
        self._signal = value


class EnvironmentVariableComment(Comment):
    _fmt = 'CM_ EV_ {name} "{comment}";'

    def __init__(self, value):
        self._environment_variable = None

        try:
            super(EnvironmentVariableComment, self).__init__(value)
        except TypeError:
            super(EnvironmentVariableComment, self).__init__()

    def format(self, *args, **kwargs):
        return self._fmt.format(
            name=self._environment_variable.name,
            comment=self.replace('"', '\\"')
        )

    @property
    def environment_variable(self):
        return self._environment_variable

    @environment_variable.setter
    def environment_variable(self, value):
        self._environment_variable = value
