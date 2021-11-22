class Test:
    def __init__(self, function):
        self.f = function
        self.a = 1

    def doFunction(self):
        self.a += 1
        return self.f(self)

def f(instance):
    print(instance.a)

t = Test(f)
t.doFunction()

for i in range(2):
    t.doFunction()
