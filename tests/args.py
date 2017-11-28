from inspect import getfullargspec


def x(body, lol):
    print(lol)


print(getfullargspec(x))
