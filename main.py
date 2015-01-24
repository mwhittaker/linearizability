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
            colors = [
                "#f17d80",
                "#737495",
                "#68a8ad",
                "#c4d4af",
                "#6c8672",
            ]
            return colors[i % len(colors)]

        style = {
                "linewidth": 2,
        }
        def line((x0, y0), (x1, y1), color):
            print (x0, y0)
            plt.plot([x0, x1], [y0, y1], color=color, **style)

        def point(x, y, s, color):
            plt.scatter([x], [y], color=color, marker="|", **style)
            plt.text(x, y + 0.1, s, size=8, family="monospace", ha="center")

        def ellipsis(x, y, color):
            plt.scatter([x + 0.2, x + 0.4, x + 0.6], [y] * 3, color=color, marker=".", alpha = 0.9)

        def pairwise(l):
            """http://stackoverflow.com/a/5389547/3187068"""
            if len(l) % 2 != 0:
                a = iter(l + [None])
            else:
                a = iter(l)
            return itertools.izip(a, a)

        plt.figure(figsize=(12.5, 5))

        procs  = enumerate_dict(sorted(dedup(e.proc for e in self.history)))
        colors = enumerate_dict(sorted(dedup(e.obj  for e in self.history)))
        colors = {obj: color(i) for (obj, i) in colors.iteritems()}

        if self.parent is None:
            history = list(enumerate(self.history))
        else:
            history = list(enumerate(self.parent.history))

        for (proc, y) in procs.iteritems():
            plt.text(-0.5, y, "process {}".format(proc), family="monospace", size="8", ha="right", va="center")

            subhistory = pairwise([(i, e) for (i, e) in history if e.proc == proc])

            for (a, b) in subhistory:
                (i0, e0) = a
                color = colors[e0.obj]

                if b is not None:
                    (i1, e1) = b
                    line((i0, y), (i1, y), color)
                    point(i0, y, str(e0), color)
                    point(i1, y, str(e1), color)
                else:
                    line((i0, y), (i0 + 2, y), color)
                    point(i0, y, str(e0), color)
                    ellipsis(i0 + 2, y, color)

        plt.axis("scaled")
        plt.axis("off")
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
        C.r.Enq(z),
        A.q.Fail(),
        B.q.Enq(x),
        C.r.Ok(),
    ])
    H.plot("example.svg")

if __name__ == "__main__":
    main()
