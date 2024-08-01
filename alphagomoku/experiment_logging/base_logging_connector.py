from abc import abstractmethod


class BaseLoggingConnector:
    @abstractmethod
    def start(self, config: dict | None = None):
        raise NotImplementedError

    @abstractmethod
    def log(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def log_array(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def finish(self):
        raise NotImplementedError


class NoopLoggingConnector(BaseLoggingConnector):
    """Dummy logging connector that does nothing."""
    def start(self, config: dict | None = None):
        pass

    def log(self, *args, **kwargs):
        pass

    def log_array(self, *args, **kwargs):
        pass

    def finish(self):
        pass
