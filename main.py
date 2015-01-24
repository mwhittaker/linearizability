import itertools
import matplotlib.pyplot as plt

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

        def line((x0, y0), (x1, y1), color):
            plt.plot([x0, x1], [y0, y1], color=color, alpha=0.9)

        def point(x, y, color):
            plt.scatter([x], [y], color=color, alpha=0.9, marker="|")

        def ellipsis(x, y, color):
            plt.scatter([x + 0.2, x + 0.4, x + 0.6], [y] * 3, color=color, alpha=0.9, marker=".")

        def pairwise(iterable):
            """http://stackoverflow.com/a/5389547/3187068"""
            a = iter(iterable)
            return itertools.izip(a, a)

        plt.figure()
        plt.axis("off")

        procs  = enumerate_dict(sorted(dedup(e.proc for e in self.history)))
        colors = enumerate_dict(sorted(dedup(e.obj  for e in self.history)))
        colors = {obj: color(i) for (obj, i) in colors.iteritems()}

        if self.parent is None:
            history = list(enumerate(self.history))
        else:
            history = list(enumerate(self.parent.history))

        for (proc, i) in procs.iteritems():
            subhistory = [(i, e) for (i, e) in history if e.proc == proc]
            if len(subhistory) % 2 != 0:
                subhistory.append(None)
            subhistory = pairwise(subhistory)

            for (a, b) in subhistory:
                if b is not None:
                    (i0, e0) = a
                    (i1, e1) = b
                    line((i0, procs[proc]), (i1, procs[proc]), "r")
                    point(i0, procs[proc], "r")
                    point(i1, procs[proc], "r")
                else:
                    (i0, e0) = a
                    line((i0, procs[proc]), (i0 + 1, procs[proc]), "r")
                    ellipsis(i0 + 1, procs[proc], "r")

        plt.savefig(filename, bbox_inches="tight")

def main():
    A, B, C = Process("A"), Process("B"), Process("C")
    p, q    = A.p, A.q
    x, y, z = "x", "y", "z"

    H = History([
        A.p.Enq(x),
        B.p.Enq(y),
        B.p.Ok(),
        A.p.Ok(),
        A.q.Deq(),
        A.q.Fail(),
        B.q.Enq(x)
    ])
    H.plot("example.svg")

if __name__ == "__main__":
    main()
