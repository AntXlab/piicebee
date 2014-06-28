from tornado.web import Application, RequestHandler
from werkzeug.utils import find_modules, import_string
from ..util import Config, Singleton
import miitus.defs


class App(Singleton):
    """
    tornado application container
    """

    @staticmethod
    def __gen_route(kls):
        ret = []
        for path in kls.__route__:
            ret.append((path, kls))
        return ret

    @staticmethod
    def __routes(package_name=None):
        """
        generating route by scanning modules in package(by package_name)

        Note: only modules would be scanned, handlers declared in package's
        __init__.py won't be scannd.
        """
        package_name = '.'.join(__name__.split('.')[:-1])

        ret = []
        for name in find_modules(package_name, recursive=True):
            mod = import_string(name)
            for item_name in dir(mod):
                item = getattr(mod, item_name)
                if type(item) == type and issubclass(item, RequestHandler) and hasattr(item, miitus.defs.ROUTE_ATTR_NAME):
                    ret.extend(App.__gen_route(item))

        return ret

    def __init__(self, package_name=None):
        self.__app = Application(
            App.__routes(package_name),
            **(Config().to_dict(miitus.defs.TORNADO_CONFIG_PREFIX))
        )

    @property
    def app(self):
        """
        access tornado app instance
        """
        return self.__app
