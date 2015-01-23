import matplotlib.pyplot as plt

def line((x0, y0), (x1, y1)):
    plt.plot([x0, x1], [y0, y1], color="r")

class Event(object):
    def __init__(self, obj, method, args, proc):
        self.obj    = obj
        self.method = method
        self.args   = args
        self.proc   = proc

    def __str__(self):
        return "{}.{}({})".format(self.obj, self.method, ", ".join(map(str, self.args)))

    def __repr__(self):
        return "{}.{}".format(self.proc, str(self))

class Object(object):
    def __init__(self, proc, obj):
        self.proc = proc
        self.obj  = obj

    def __getattr__(self, method):
        def f(*args):
            return Event(self.obj, method, args, self.proc)
        return f

    def __str__(self):
        return self.obj

class Process(object):
    def __init__(self, proc):
        self.proc = proc

    def __getattr__(self, obj):
       return Object(self.proc, obj)

    def __str__(self):
        return self.proc

class ProcType(type):
    def __getattr__(cls, proc):
        return Process(proc)

class Proc:
    __metaclass__ = ProcType

class ArgType(type):
    def __getattr__(cls, arg):
        return arg

class Arg:
    __metaclass__ = ArgType

class History(object):
    def __init__(self, history, parent=None):
        self.history = history
        self.parent  = parent

    def __or__(self, x):
        parent = self if self.parent is None else self.parent

        if type(x) == Process:
            return History([e for e in self.history if e.proc == x.proc], parent)
        else:
            return History([e for e in self.history if e.obj == x.obj], parent)

    def __str__(self):
        return "[" + ", ".join([repr(e) for e in self.history]) + "]"

    def plot(self, filename):
        def dedup(l):
            return list(set(l))

        def enumerate_dict(l):
            return {x: i for (i, x) in enumerate(l)}

        def color(i):
            colors = "bgrcmykw"
            return colors[i % len(colors)]

        procs = enumerate_dict(sorted(dedup(e.proc for e in self.history)))
        objs  = enumerate_dict(sorted(dedup(e.obj  for e in self.history)))
        objs  = {obj: color(i) for (obj, i) in objs.iteritems()}
        print procs
        print objs

        for (proc, i) in procs.iteritems():
            subhistory = [e for e in self.history if e.proc == proc]
            print subhistory

def main():
    A, B, C = Proc.A, Proc.B, Proc.C
    p, q    = A.p, A.q
    x, y, z = Arg.x, Arg.y, Arg.z

    H = History([A.p.Enq(x), B.p.Enq(y), B.p.Ok(), A.p.Ok()])
    print H
    H.plot("foo")

if __name__ == "__main__":
    main()
