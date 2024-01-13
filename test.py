
from types import MethodType


class Container:

    class MethodWrapper:

        def __call__(self, container, *args, **kwargs):
            print(f'{container} {args} {kwargs}')

    def method(self):
        print(str(self))

    method2 = MethodWrapper()

container = Container()
container.method2 = MethodType(container.method2, container)
container.method2('arg1', 'arg2', flag=5)
import ipdb
ipdb.set_trace()
