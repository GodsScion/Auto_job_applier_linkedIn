from __future__ import division

import math

try:
    from typing import List, Tuple, Union
except ImportError:
    pass  # This is fine; it happens on Python 2.6 and before, but type hints aren't supported there anyway.

__version__ = '1.2.0'


# from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
def getLine(x1, y1, x2, y2):  # type: (int, int, int, int) -> List[Tuple[int, int]]
    """Returns a list of (x, y) tuples of every point on a line between
    (x1, y1) and (x2, y2). The x and y values inside the tuple are integers.

    Line generated with the Bresenham algorithm.

    Args:
      x1 (int, float): The x coordinate of the line's start point.
      y1 (int, float): The y coordinate of the line's start point.
      x2 (int, float): The x coordinate of the line's end point.
      y2 (int, float): The y coordiante of the line's end point.

    Returns:
      [(x1, y1), (x2, y2), (x3, y3), ...]

    Example:
    >>> getLine(0, 0, 6, 6)
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
    >>> getLine(0, 0, 3, 6)
    [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
    >>> getLine(3, 3, -3, -3)
    [(3, 3), (2, 2), (1, 1), (0, 0), (-1, -1), (-2, -2), (-3, -3)]
    """
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    points = []
    issteep = abs(y2 - y1) > abs(x2 - x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def getPointOnLine(
    startX, startY, endX, endY, n
):  # type: (Union[int, float], Union[int, float], Union[int, float], Union[int, float], Union[int, float]) -> Tuple[Union[int, float], Union[int, float]]
    """Returns the (x, y) tuple of the point that has progressed a proportion
    n along the line defined by the two x, y coordinates.

    Args:
      startX (int, float): The x coordinate of the line's start point.
      startY (int, float): The y coordinate of the line's start point.
      endX (int, float): The x coordinate of the line's end point.
      endY (int, float): The y coordinate of the line's end point.
      n (int, float): Progress along the line. 0.0 is the start point, 1.0 is the end point. 0.5 is the midpoint. This value can be less than 0.0 or greater than 1.0.

    Returns:
      Tuple of floats for the x, y coordinate of the point.

    Example:
    >>> getPointOnLine(0, 0, 6, 6, 0)
    (0, 0)
    >>> getPointOnLine(0, 0, 6, 6, 1)
    (6, 6)
    >>> getPointOnLine(0, 0, 6, 6, 0.5)
    (3.0, 3.0)
    >>> getPointOnLine(0, 0, 6, 6, 0.75)
    (4.5, 4.5)
    >>> getPointOnLine(3, 3, -3, -3, 0.5)
    (0.0, 0.0)
    >>> getPointOnLine(3, 3, -3, -3, 0.25)
    (1.5, 1.5)
    >>> getPointOnLine(3, 3, -3, -3, 0.75)
    (-1.5, -1.5)
    """
    return (((endX - startX) * n) + startX, ((endY - startY) * n) + startY)


def _iterTween(startX, startY, endX, endY, intervalSize, tweeningFunc, *args):
    ti = tweeningFunc(0.0, *args)
    yield (((endX - startX) * ti) + startX, ((endY - startY) * ti) + startY)

    n = intervalSize

    # The weird number is to prevent 0.999999 from being used in addition to 1.0 at the end of the function (i.e. rounding error prevention):
    while n + 1.1102230246251565e-16 < 1.0:
        ti = tweeningFunc(n, *args)
        yield (((endX - startX) * ti) + startX, ((endY - startY) * ti) + startY)
        n += intervalSize

    ti = tweeningFunc(1.0, *args)
    yield (((endX - startX) * ti) + startX, ((endY - startY) * ti) + startY)


def linear(n):  # type: (Union[int, float]) -> Union[int, float]
    """Constant speed tween function.

    Example:
    >>> linear(0.0)
    0.0
    >>> linear(0.2)
    0.2
    >>> linear(0.4)
    0.4
    >>> linear(0.6)
    0.6
    >>> linear(0.8)
    0.8
    >>> linear(1.0)
    1.0
    """
    return n


def iterLinear(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a linear tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, linear))


def easeInQuad(n):  # type: (Union[int, float]) -> Union[int, float]
    """Start slow and accelerate (Quadratic function).

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return n**2


def iterEaseInQuad(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInQuad tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInQuad))


def easeOutQuad(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates to stop. (Quadratic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return -n * (n - 2)


def iterEaseOutQuad(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutQuad tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutQuad))


def easeInOutQuad(n):  # type: (Union[int, float]) -> Union[int, float]
    """Accelerates, reaches the midpoint, and then decelerates. (Quadratic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if n < 0.5:
        return 2 * n**2
    else:
        n = n * 2 - 1
        return -0.5 * (n * (n - 2) - 1)


def iterEaseInOutQuad(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutQuad tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutQuad))


def easeInCubic(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates. (Cubic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return n**3


def iterEaseInCubic(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInCubic tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInCubic))


def easeOutCubic(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates to stop. (Cubic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n -= 1
    return n**3 + 1


def iterEaseOutCubic(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutCubic tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutCubic))


def easeInOutCubic(n):  # type: (Union[int, float]) -> Union[int, float]
    """Accelerates, reaches the midpoint, and then decelerates. (Cubic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n *= 2
    if n < 1:
        return 0.5 * n**3
    else:
        n -= 2
        return 0.5 * (n**3 + 2)


def iterEaseInOutCubic(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutCubic tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutCubic))


def easeInQuart(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates. (Quartic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return n**4


def iterEaseInQuart(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInQuart tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInQuart))


def easeOutQuart(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates to stop. (Quartic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n -= 1
    return -(n**4 - 1)


def iterEaseOutQuart(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutQuart tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutQuart))


def easeInOutQuart(n):  # type: (Union[int, float]) -> Union[int, float]
    """Accelerates, reaches the midpoint, and then decelerates. (Quartic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)


def iterEaseInOutQuart(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutQuart tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutQuart))


def easeInQuint(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates. (Quintic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return n**5


def iterEaseInQuint(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInQuint tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInQuint))


def easeOutQuint(n):  # type: (Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates to stop. (Quintic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n -= 1
    return n**5 + 1


def iterEaseOutQuint(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutQuint tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutQuint))


def easeInOutQuint(n):  # type: (Union[int, float]) -> Union[int, float]
    """Accelerates, reaches the midpoint, and then decelerates. (Quintic function.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)


def iterEaseInOutQuint(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutQuint tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutQuint))


def easeInPoly(n, degree=2):  # type: (Union[int, float], Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates. (Polynomial function with custom degree.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.
      degree (int, float): The degree of the polynomial function.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if not isinstance(degree, (int, float)) or degree < 0:
        raise ValueError('degree argument must be a positive number.')
    return n**degree


def iterEaseInPoly(startX, startY, endX, endY, intervalSize, degree=2):
    """Returns an iterator of a easeInPoly tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInPoly, degree))


def easeOutPoly(n, degree=2):  # type: (Union[int, float], Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates to stop. (Polynomial function with custom degree.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.
      degree (int, float): The degree of the polynomial function.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if not isinstance(degree, (int, float)) or degree < 0:
        raise ValueError('degree argument must be a positive number.')
    return 1 - abs((n - 1) ** degree)


def iterEaseOutPoly(startX, startY, endX, endY, intervalSize, degree=2):
    """Returns an iterator of a easeOutPoly tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutPoly, degree))


def easeInOutPoly(n, degree=2):  # type: (Union[int, float], Union[int, float]) -> Union[int, float]
    """Starts fast and decelerates to stop. (Polynomial function with custom degree.)

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.
      degree (int, float): The degree of the polynomial function.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if not isinstance(degree, (int, float)) or degree < 0:
        raise ValueError('degree argument must be a positive number.')

    n *= 2
    if n < 1:
        return 0.5 * n**degree
    else:
        n -= 2
        return 1 - 0.5 * abs(n**degree)


def iterEaseInOutPoly(startX, startY, endX, endY, intervalSize, degree=2):
    """Returns an iterator of a easeInOutPoly tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutPoly, degree))


def easeInSine(n):  # type: (Union[int, float]) -> Union[int, float]
    """A sinusoidal tween function that begins slow and then accelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return -1 * math.cos(n * math.pi / 2) + 1


def iterEaseInSine(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInSine tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInSine))


def easeOutSine(n):  # type: (Union[int, float]) -> Union[int, float]
    """A sinusoidal tween function that begins fast and then decelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return math.sin(n * math.pi / 2)


def iterEaseOutSine(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutSine tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutSine))


def easeInOutSine(n):  # type: (Union[int, float]) -> Union[int, float]
    """A sinusoidal tween function that accelerates, reaches the midpoint, and then decelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return -0.5 * (math.cos(math.pi * n) - 1)


def iterEaseInOutSine(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutSine tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutSine))


def easeInExpo(n):  # type: (Union[int, float]) -> Union[int, float]
    """An exponential tween function that begins slow and then accelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if n == 0:
        return 0
    else:
        return 2 ** (10 * (n - 1))


def iterEaseInExpo(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInExpo tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInExpo))


def easeOutExpo(n):  # type: (Union[int, float]) -> Union[int, float]
    """An exponential tween function that begins fast and then decelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if n == 1:
        return 1
    else:
        return -(2 ** (-10 * n)) + 1


def iterEaseOutExpo(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutExpo tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutExpo))


def easeInOutExpo(n):  # type: (Union[int, float]) -> Union[int, float]
    """An exponential tween function that accelerates, reaches the midpoint, and then decelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        n *= 2
        if n < 1:
            return 0.5 * 2 ** (10 * (n - 1))
        else:
            n -= 1
            # 0.5 * (-() + 2)
            return 0.5 * (-1 * (2 ** (-10 * n)) + 2)


def iterEaseInOutExpo(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutExpo tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutExpo))


def easeInCirc(n):  # type: (Union[int, float]) -> Union[int, float]
    """A circular tween function that begins slow and then accelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return -1 * (math.sqrt(1 - n * n) - 1)


def iterEaseInCirc(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInCirc tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInCirc))


def easeOutCirc(n):  # type: (Union[int, float]) -> Union[int, float]
    """A circular tween function that begins fast and then decelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n -= 1
    return math.sqrt(1 - (n * n))


def iterEaseOutCirc(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutCirc tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutCirc))


def easeInOutCirc(n):  # type: (Union[int, float]) -> Union[int, float]
    """A circular tween function that accelerates, reaches the midpoint, and then decelerates.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n -= 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)


def iterEaseInOutCirc(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutCirc tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutCirc))


def easeInElastic(
    n, amplitude=1, period=0.3
):  # type: (Union[int, float], Union[int, float], Union[int, float]) -> Union[int, float]
    """An elastic tween function that begins with an increasing wobble and then snaps into the destination.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return 1 - easeOutElastic(1 - n, amplitude=amplitude, period=period)


def iterEaseInElastic(startX, startY, endX, endY, intervalSize, amplitude=1, period=0.3):
    """Returns an iterator of a easeInElastic tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInElastic, amplitude, period))


def easeOutElastic(
    n, amplitude=1, period=0.3
):  # type: (Union[int, float], Union[int, float], Union[int, float]) -> Union[int, float]
    """An elastic tween function that overshoots the destination and then "rubber bands" into the destination.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """

    if amplitude < 1:
        amplitude = 1
        s = period / 4
    else:
        s = period / (2 * math.pi) * math.asin(1 / amplitude)

    return amplitude * 2 ** (-10 * n) * math.sin((n - s) * (2 * math.pi / period)) + 1


def iterEaseOutElastic(startX, startY, endX, endY, intervalSize, amplitude=1, period=0.3):
    """Returns an iterator of a easeOutElastic tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutElastic, amplitude, period))


def easeInOutElastic(
    n, amplitude=1, period=0.5
):  # type: (Union[int, float], Union[int, float], Union[int, float]) -> Union[int, float]
    """An elastic tween function wobbles towards the midpoint.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n *= 2
    if n < 1:
        return easeInElastic(n, amplitude=amplitude, period=period) / 2
    else:
        return easeOutElastic(n - 1, amplitude=amplitude, period=period) / 2 + 0.5


def iterEaseInOutElastic(startX, startY, endX, endY, intervalSize, amplitude=1, period=0.5):
    """Returns an iterator of a easeInOutElastic tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutElastic, amplitude, period))


def easeInBack(n, s=1.70158):  # type: (Union[int, float], Union[int, float]) -> Union[int, float]
    """A tween function that backs up first at the start and then goes to the destination.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return n * n * ((s + 1) * n - s)


def iterEaseInBack(startX, startY, endX, endY, intervalSize, s=1.70158):
    """Returns an iterator of a easeInBack tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInBack, s))


def easeOutBack(n, s=1.70158):  # type: (Union[int, float], Union[int, float]) -> Union[int, float]
    """A tween function that overshoots the destination a little and then backs into the destination.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n -= 1
    return n * n * ((s + 1) * n + s) + 1


def iterEaseOutBack(startX, startY, endX, endY, intervalSize, s=1.70158):
    """Returns an iterator of a easeOutBack tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutBack, s))


def easeInOutBack(n, s=1.70158):  # type: (Union[int, float], Union[int, float]) -> Union[int, float]
    """A "back-in" tween function that overshoots both the start and destination.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    n *= 2
    if n < 1:
        s *= 1.525
        return 0.5 * (n * n * ((s + 1) * n - s))
    else:
        n -= 2
        s *= 1.525
        return 0.5 * (n * n * ((s + 1) * n + s) + 2)


def iterEaseInOutBack(startX, startY, endX, endY, intervalSize, s=1.70158):
    """Returns an iterator of a easeInOutBack tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutBack, s))


def easeInBounce(n):  # type: (Union[int, float]) -> Union[int, float]
    """A bouncing tween function that begins bouncing and then jumps to the destination.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    return 1 - easeOutBounce(1 - n)


def iterEaseInBounce(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInBounce tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInBounce))


def easeOutBounce(n):  # type: (Union[int, float]) -> Union[int, float]
    """A bouncing tween function that hits the destination and then bounces to rest.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if n < (1 / 2.75):
        return 7.5625 * n * n
    elif n < (2 / 2.75):
        n -= 1.5 / 2.75
        return 7.5625 * n * n + 0.75
    elif n < (2.5 / 2.75):
        n -= 2.25 / 2.75
        return 7.5625 * n * n + 0.9375
    else:
        n -= 2.65 / 2.75
        return 7.5625 * n * n + 0.984375


def iterEaseOutBounce(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeOutBounce tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeOutBounce))


def easeInOutBounce(n):  # type: (Union[int, float]) -> Union[int, float]
    """A bouncing tween function that bounces at the start and end.

    Args:
      n (int, float): The time progress, starting at 0.0 and ending at 1.0.

    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    if n < 0.5:
        return easeInBounce(n * 2) * 0.5
    else:
        return easeOutBounce(n * 2 - 1) * 0.5 + 0.5


def iterEaseInOutBounce(startX, startY, endX, endY, intervalSize):
    """Returns an iterator of a easeInOutBounce tween between the start and end points, incrementing the
    interpolation factor by intervalSize each time. Guaranteed to return the point for 0.0 first
    and 1.0 last no matter the intervalSize."""
    return iter(_iterTween(startX, startY, endX, endY, intervalSize, easeInOutBounce))
