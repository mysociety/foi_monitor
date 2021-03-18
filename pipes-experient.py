
class PipeEnd:
    pass

class PipeFunc:
    """
    Like functools partial, but puts the new object at the start
    or at any arbitary point defined by either position (for an arg)
    or key (for a keyword)
    """
    def __init__(self, func, *args, position=0, key=None, **kwargs):
        self.func = func
        self.args = list(args)
        self.kwargs = kwargs
        self.position = position
        self.key = key

    def __call__(self, value):
        args = self.args
        kwargs = self.kwargs
        if self.key:
            kwargs[self.key] = value
        else:
            args.insert(self.position, value)
        return self.func(*args, **kwargs)

class PipeStart:

    def __init__(self, value, *args):
        self.value = value
        self.operations = []

    def process(self):
        value = self.root
        for o in self.operations:
            value = o(value)
        return value

    def __add__(self, other):
        if isinstance(other, PipeEnd):
            return self.value
        self.value = other(self.value)
        return self

    def __or__(self, other):
        pass

class Pipe:
    start = PipeStart
    func = PipeFunc
    end = PipeEnd()

    def __new__(cls, *args, **kwargs):
        value = Pipe.start(args[0])
        for operation in args[1:]:
            value += operation
        return value + Pipe.end


times_by_five = lambda x: x*5

times = lambda x,y:x*y

result = Pipe.start(5) +\
         times_by_five +\
         Pipe.func(times, 2) +\
         Pipe.end

print (result)

print (Pipe(2,
            times_by_five,
            Pipe.func(times, 2)))

if __name__ == "__main__":
    pass