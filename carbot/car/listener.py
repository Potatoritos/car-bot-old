import asyncio


__all__ = [
    'Listener',
    'ListenerList',
    'listener'
]

class Listener(object):
    def __init__(self, func):
        self.func = func
        self.event = func.__name__
        self.parent = None

class ListenerList(object):
    def __init__(self):
        self.listeners = {}

    def add(self, listener):
        if listener.event not in self.listeners:
            self.listeners[listener.event] = {}

        self.listeners[listener.event][listener.parent] = listener

    def remove(self, listener):
        del self.listeners[listener.event][listener.parent]

    def run(self, event, *args, **kwargs):
        if event not in self.listeners:
            return

        for _, lis in self.listeners[event].items():
            if lis.parent is None:
                asyncio.create_task(lis.func(*args, **kwargs))
            else:
                asyncio.create_task(lis.func(lis.parent, *args, **kwargs))

def listener(func):
    return Listener(func)

