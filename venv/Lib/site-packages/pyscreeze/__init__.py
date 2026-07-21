# PyScreeze - PyScreeze is a simple, cross-platform screenshot module for Python 2 and 3.
# By Al Sweigart al@inventwithpython.com

__version__ = '1.0.1'

import collections
import datetime
import functools
import os
import subprocess
import sys
import time
import errno

from contextlib import contextmanager

from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from PIL import __version__ as PIL__version__
from PIL import ImageGrab

PILLOW_VERSION = tuple([int(x) for x in PIL__version__.split('.')])

_useOpenCV: bool = False
try:
    import cv2
    import numpy

    _useOpenCV = True
except ImportError:
    pass  # This is fine, useOpenCV will stay as False.

RUNNING_PYTHON_2 = sys.version_info[0] == 2

_PYGETWINDOW_UNAVAILABLE = True
if sys.platform == 'win32':
    # On Windows, the monitor scaling can be set to something besides normal 100%.
    # PyScreeze and Pillow needs to account for this to make accurate screenshots.
    # TODO - How does macOS and Linux handle monitor scaling?
    import ctypes

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass  # Windows XP doesn't support monitor scaling, so just do nothing.

    try:
        import pygetwindow
    except ImportError:
        _PYGETWINDOW_UNAVAILABLE = True
    else:
        _PYGETWINDOW_UNAVAILABLE = False


GRAYSCALE_DEFAULT = True

# For version 0.1.19 I changed it so that ImageNotFoundException was raised
# instead of returning None. In hindsight, this change came too late, so I'm
# changing it back to returning None. But I'm also including this option for
# folks who would rather have it raise an exception.
# For version 1.0.0, USE_IMAGE_NOT_FOUND_EXCEPTION is set to True by default.
USE_IMAGE_NOT_FOUND_EXCEPTION = True

GNOMESCREENSHOT_EXISTS = False
try:
    if sys.platform.startswith('linux'):
        whichProc = subprocess.Popen(['which', 'gnome-screenshot'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GNOMESCREENSHOT_EXISTS = whichProc.wait() == 0
except OSError as ex:
    if ex.errno == errno.ENOENT:
        # if there is no "which" program to find gnome-screenshot, then assume there
        # is no gnome-screenshot.
        pass
    else:
        raise

SCROT_EXISTS = False
try:
    if sys.platform.startswith('linux'):
        whichProc = subprocess.Popen(['which', 'scrot'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        SCROT_EXISTS = whichProc.wait() == 0
except OSError as ex:
    if ex.errno == errno.ENOENT:
        # if there is no "which" program to find scrot, then assume there
        # is no scrot.
        pass
    else:
        raise

# On Linux, figure out which window system is being used.
if sys.platform.startswith('linux'):
    RUNNING_X11 = False
    RUNNING_WAYLAND = False
    if os.environ.get('XDG_SESSION_TYPE') == 'x11':
        RUNNING_X11 = True
        RUNNING_WAYLAND = False
    elif os.environ.get('XDG_SESSION_TYPE') == 'wayland':
        RUNNING_WAYLAND = True
        RUNNING_X11 = False
    elif 'WAYLAND_DISPLAY' in os.environ:
        RUNNING_WAYLAND = True
        RUNNING_X11 = False


if sys.platform == 'win32':
    from ctypes import windll

    # win32 DC(DeviceContext) Manager
    @contextmanager
    def __win32_openDC(hWnd=0):
        """
        A context manager for handling calling GetDC() and ReleaseDC().

        This is used for win32 API calls, used by the pixel() function
        on Windows.

        Args:
            hWnd (int): The handle for the window to get a device context
        of, defaults to 0
        """
        hDC = windll.user32.GetDC(hWnd)
        if hDC == 0:  # NULL
            raise WindowsError("windll.user32.GetDC failed : return NULL")
        try:
            yield hDC
        finally:
            windll.user32.ReleaseDC.argtypes = [ctypes.c_ssize_t, ctypes.c_ssize_t]
            if windll.user32.ReleaseDC(hWnd, hDC) == 0:
                raise WindowsError("windll.user32.ReleaseDC failed : return 0")


Box = collections.namedtuple('Box', 'left top width height')
Point = collections.namedtuple('Point', 'x y')
RGB = collections.namedtuple('RGB', 'red green blue')


class PyScreezeException(Exception):
    """PyScreezeException is a generic exception class raised when a
    PyScreeze-related error happens. If a PyScreeze function raises an
    exception that isn't PyScreezeException or a subclass, assume it is
    a bug in PyScreeze."""

    pass


class ImageNotFoundException(PyScreezeException):
    """ImageNotFoundException is an exception class raised when the
    locate functions fail to locate an image. You must set
    pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION to True to enable this feature.
    Otherwise, the locate functions will return None."""

    pass


def requiresPyGetWindow(wrappedFunction):
    """
    A decorator that marks a function as requiring PyGetWindow to be installed.
    This raises PyScreezeException if Pillow wasn't imported.
    """

    @functools.wraps(wrappedFunction)
    def wrapper(*args, **kwargs):
        if _PYGETWINDOW_UNAVAILABLE:
            raise PyScreezeException('The PyGetWindow package is required to use this function.')
        return wrappedFunction(*args, **kwargs)

    return wrapper


def _load_cv2(img, grayscale=None):
    """
    TODO
    """
    # load images if given filename, or convert as needed to opencv
    # Alpha layer just causes failures at this point, so flatten to RGB.
    # RGBA: load with -1 * cv2.CV_LOAD_IMAGE_COLOR to preserve alpha
    # to matchTemplate, need template and image to be the same wrt having alpha

    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT
    if isinstance(img, str):
        # The function imread loads an image from the specified file and
        # returns it. If the image cannot be read (because of missing
        # file, improper permissions, unsupported or invalid format),
        # the function returns an empty matrix
        # http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html
        if grayscale:
            img_cv = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        else:
            img_cv = cv2.imread(img, cv2.IMREAD_COLOR)
        if img_cv is None:
            raise IOError(
                "Failed to read %s because file is missing, "
                "has improper permissions, or is an "
                "unsupported or invalid format" % img
            )
    elif isinstance(img, numpy.ndarray):
        # don't try to convert an already-gray image to gray
        if grayscale and len(img.shape) == 3:  # and img.shape[2] == 3:
            img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_cv = img
    elif hasattr(img, 'convert'):
        # assume its a PIL.Image, convert to cv format
        img_array = numpy.array(img.convert('RGB'))
        img_cv = img_array[:, :, ::-1].copy()  # -1 does RGB -> BGR
        if grayscale:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        raise TypeError('expected an image filename, OpenCV numpy array, or PIL image')
    return img_cv


def _locateAll_opencv(needleImage, haystackImage, grayscale=None, limit=10000, region=None, step=1, confidence=0.999):
    """
    TODO - rewrite this
        faster but more memory-intensive than pure python
        step 2 skips every other row and column = ~3x faster but prone to miss;
            to compensate, the algorithm automatically reduces the confidence
            threshold by 5% (which helps but will not avoid all misses).
        limitations:
          - OpenCV 3.x & python 3.x not tested
          - RGBA images are treated as RBG (ignores alpha channel)
    """
    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT

    confidence = float(confidence)

    needleImage = _load_cv2(needleImage, grayscale)
    needleHeight, needleWidth = needleImage.shape[:2]
    haystackImage = _load_cv2(haystackImage, grayscale)

    if region:
        haystackImage = haystackImage[region[1] : region[1] + region[3], region[0] : region[0] + region[2]]
    else:
        region = (0, 0)  # full image; these values used in the yield statement
    if haystackImage.shape[0] < needleImage.shape[0] or haystackImage.shape[1] < needleImage.shape[1]:
        # avoid semi-cryptic OpenCV error below if bad size
        raise ValueError('needle dimension(s) exceed the haystack image or region dimensions')

    if step == 2:
        confidence *= 0.95
        needleImage = needleImage[::step, ::step]
        haystackImage = haystackImage[::step, ::step]
    else:
        step = 1

    # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
    match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
    matches = numpy.unravel_index(match_indices[:limit], result.shape)

    if len(matches[0]) == 0:
        if USE_IMAGE_NOT_FOUND_EXCEPTION:
            raise ImageNotFoundException('Could not locate the image (highest confidence = %.3f)' % result.max())
        else:
            return

    # use a generator for API consistency:
    matchx = matches[1] * step + region[0]  # vectorized
    matchy = matches[0] * step + region[1]
    for x, y in zip(matchx, matchy):
        yield Box(x, y, needleWidth, needleHeight)


def _locateAll_pillow(needleImage, haystackImage, grayscale=None, limit=None, region=None, step=1, confidence=None):
    """
    TODO
    """
    if confidence is not None:
        raise NotImplementedError('The confidence keyword argument is only available if OpenCV is installed.')

    # setup all the arguments
    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT

    needleFileObj = None
    if isinstance(needleImage, str):
        # 'image' is a filename, load the Image object
        needleFileObj = open(needleImage, 'rb')
        needleImage = Image.open(needleFileObj)

    haystackFileObj = None
    if isinstance(haystackImage, str):
        # 'image' is a filename, load the Image object
        haystackFileObj = open(haystackImage, 'rb')
        haystackImage = Image.open(haystackFileObj)

    if region is not None:
        haystackImage = haystackImage.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))
    else:
        region = (0, 0)  # set to 0 because the code always accounts for a region

    if grayscale:  # if grayscale mode is on, convert the needle and haystack images to grayscale
        needleImage = ImageOps.grayscale(needleImage)
        haystackImage = ImageOps.grayscale(haystackImage)
    else:
        # if not using grayscale, make sure we are comparing RGB images, not RGBA images.
        if needleImage.mode == 'RGBA':
            needleImage = needleImage.convert('RGB')
        if haystackImage.mode == 'RGBA':
            haystackImage = haystackImage.convert('RGB')

    # setup some constants we'll be using in this function
    needleWidth, needleHeight = needleImage.size
    haystackWidth, haystackHeight = haystackImage.size

    needleImageData = tuple(needleImage.getdata())
    haystackImageData = tuple(haystackImage.getdata())

    needleImageRows = [
        needleImageData[y * needleWidth : (y + 1) * needleWidth] for y in range(needleHeight)
    ]  # LEFT OFF - check this
    needleImageFirstRow = needleImageRows[0]

    assert (
        len(needleImageFirstRow) == needleWidth
    ), 'The calculated width of first row of the needle image is not the same as the width of the image.'
    assert [len(row) for row in needleImageRows] == [
        needleWidth
    ] * needleHeight, 'The needleImageRows aren\'t the same size as the original image.'

    numMatchesFound = 0

    # NOTE: After running tests/benchmarks.py on the following code, it seem that having a step
    # value greater than 1 does not give *any* significant performance improvements.
    # Since using a step higher than 1 makes for less accurate matches, it will be
    # set to 1.
    step = 1  # hard-code step as 1 until a way to improve it can be figured out.

    if step == 1:
        firstFindFunc = _kmp
    else:
        firstFindFunc = _steppingFind

    for y in range(haystackHeight):  # start at the leftmost column
        for matchx in firstFindFunc(
            needleImageFirstRow, haystackImageData[y * haystackWidth : (y + 1) * haystackWidth], step
        ):
            foundMatch = True
            for searchy in range(1, needleHeight, step):
                haystackStart = (searchy + y) * haystackWidth + matchx
                if (
                    needleImageData[searchy * needleWidth : (searchy + 1) * needleWidth]
                    != haystackImageData[haystackStart : haystackStart + needleWidth]
                ):
                    foundMatch = False
                    break
            if foundMatch:
                # Match found, report the x, y, width, height of where the matching region is in haystack.
                numMatchesFound += 1
                yield Box(matchx + region[0], y + region[1], needleWidth, needleHeight)
                if limit is not None and numMatchesFound >= limit:
                    # Limit has been reached. Close file handles.
                    if needleFileObj is not None:
                        needleFileObj.close()
                    if haystackFileObj is not None:
                        haystackFileObj.close()
                    return

    # There was no limit or the limit wasn't reached, but close the file handles anyway.
    if needleFileObj is not None:
        needleFileObj.close()
    if haystackFileObj is not None:
        haystackFileObj.close()

    if numMatchesFound == 0:
        if USE_IMAGE_NOT_FOUND_EXCEPTION:
            raise ImageNotFoundException('Could not locate the image.')
        else:
            return


def locate(needleImage, haystackImage, **kwargs):
    """
    TODO
    """
    # Note: The gymnastics in this function is because we want to make sure to exhaust the iterator so that
    # the needle and haystack files are closed in locateAll.
    kwargs['limit'] = 1
    points = tuple(locateAll(needleImage, haystackImage, **kwargs))
    if len(points) > 0:
        return points[0]
    else:
        if USE_IMAGE_NOT_FOUND_EXCEPTION:
            raise ImageNotFoundException('Could not locate the image.')
        else:
            return None


def locateOnScreen(image, minSearchTime=0, **kwargs):
    """TODO - rewrite this
    minSearchTime - amount of time in seconds to repeat taking
    screenshots and trying to locate a match.  The default of 0 performs
    a single search.
    """
    start = time.time()
    while True:
        try:
            # the locateAll() function must handle cropping to return accurate coordinates,
            # so don't pass a region here.
            screenshotIm = screenshot(region=None)
            retVal = locate(image, screenshotIm, **kwargs)
            try:
                screenshotIm.fp.close()
            except AttributeError:
                # Screenshots on Windows won't have an fp since they came from
                # ImageGrab, not a file. Screenshots on Linux will have fp set
                # to None since the file has been unlinked
                pass
            if retVal or time.time() - start > minSearchTime:
                return retVal
        except ImageNotFoundException:
            if time.time() - start > minSearchTime:
                if USE_IMAGE_NOT_FOUND_EXCEPTION:
                    raise
                else:
                    return None


def locateAllOnScreen(image, **kwargs):
    """
    TODO
    """

    # TODO - Should this raise an exception if zero instances of the image can be found on the
    # screen, instead of always returning a generator?
    # the locateAll() function must handle cropping to return accurate coordinates, so don't pass a region here.
    screenshotIm = screenshot(region=None)
    retVal = locateAll(image, screenshotIm, **kwargs)
    try:
        screenshotIm.fp.close()
    except AttributeError:
        # Screenshots on Windows won't have an fp since they came from
        # ImageGrab, not a file. Screenshots on Linux will have fp set
        # to None since the file has been unlinked
        pass
    return retVal


def locateCenterOnScreen(image, **kwargs):
    """
    TODO
    """
    coords = locateOnScreen(image, **kwargs)
    if coords is None:
        return None
    else:
        return center(coords)


def locateOnScreenNear(image, x, y):
    """
    TODO
    """

    foundMatchesBoxes = list(locateAllOnScreen(image))

    distancesSquared = []  # images[i] is related to distancesSquared[i]
    shortestDistanceIndex = 0  # The index of the shortest distance in `distances`

    # getting distance of all points from given point
    for foundMatchesBox in foundMatchesBoxes:
        foundMatchX, foundMatchY = center(foundMatchesBox)
        xDistance = abs(x - foundMatchX)
        yDistance = abs(y - foundMatchY)
        distancesSquared.append(xDistance * xDistance + yDistance * yDistance)

        if distancesSquared[-1] < distancesSquared[shortestDistanceIndex]:
            shortestDistanceIndex = len(distancesSquared) - 1

    # Returns the Box object of the match closest to x, y
    return foundMatchesBoxes[shortestDistanceIndex]


def locateCenterOnScreenNear(image, x, y, **kwargs):
    """
    TODO
    """
    coords = locateOnScreenNear(image, x, y, **kwargs)
    if coords is None:
        return None
    else:
        return center(coords)


@requiresPyGetWindow
def locateOnWindow(image, title, **kwargs):
    """
    TODO
    """
    matchingWindows = pygetwindow.getWindowsWithTitle(title)
    if len(matchingWindows) == 0:
        raise PyScreezeException('Could not find a window with %s in the title' % (title))
    elif len(matchingWindows) > 1:
        raise PyScreezeException(
            'Found multiple windows with %s in the title: %s' % (title, [str(win) for win in matchingWindows])
        )

    win = matchingWindows[0]
    win.activate()
    return locateOnScreen(image, region=(win.left, win.top, win.width, win.height), **kwargs)


@requiresPyGetWindow
def screenshotWindow(title):
    """
    TODO
    """
    pass  # Not implemented yet.


def showRegionOnScreen(region, outlineColor='red', filename='_showRegionOnScreen.png'):
    """
    TODO
    """
    # TODO - This function is useful! Document it!
    screenshotIm = screenshot()
    draw = ImageDraw.Draw(screenshotIm)
    region = (
        region[0],
        region[1],
        region[2] + region[0],
        region[3] + region[1],
    )  # convert from (left, top, right, bottom) to (left, top, width, height)
    draw.rectangle(region, outline=outlineColor)
    screenshotIm.save(filename)


def _screenshot_win32(imageFilename=None, region=None, allScreens=False):
    """
    TODO
    """
    # TODO - Use the winapi to get a screenshot, and compare performance with ImageGrab.grab()
    # https://stackoverflow.com/a/3586280/1893164
    im = ImageGrab.grab(all_screens=allScreens)
    if region is not None:
        assert len(region) == 4, 'region argument must be a tuple of four ints'
        assert isinstance(region[0], int) and isinstance(region[1], int) and isinstance(region[2], int) and isinstance(region[3], int), 'region argument must be a tuple of four ints'
        im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
    if imageFilename is not None:
        im.save(imageFilename)
    return im


def _screenshot_osx(imageFilename=None, region=None):
    """
    TODO
    """
    # TODO - use tmp name for this file.
    if PILLOW_VERSION < (6, 2, 1):
        # Use the screencapture program if Pillow is older than 6.2.1, which
        # is when Pillow supported ImageGrab.grab() on macOS. (It may have
        # supported it earlier than 6.2.1, but I haven't tested it.)
        if imageFilename is None:
            tmpFilename = 'screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
        else:
            tmpFilename = imageFilename
        subprocess.call(['screencapture', '-x', tmpFilename])
        im = Image.open(tmpFilename)

        if region is not None:
            assert len(region) == 4, 'region argument must be a tuple of four ints'
            assert isinstance(region[0], int) and isinstance(region[1], int) and isinstance(region[2], int) and isinstance(region[3], int), 'region argument must be a tuple of four ints'
            im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
            os.unlink(tmpFilename)  # delete image of entire screen to save cropped version
            im.save(tmpFilename)
        else:
            # force loading before unlinking, Image.open() is lazy
            im.load()

        if imageFilename is None:
            os.unlink(tmpFilename)
    else:
        # Use ImageGrab.grab() to get the screenshot if Pillow version 6.3.2 or later is installed.
        if region is not None:
            im = ImageGrab.grab(bbox=(region[0], region[1], region[2] + region[0], region[3] + region[1]))
        else:
            # Get full screen for screenshot
            im = ImageGrab.grab()
    return im


def _screenshot_linux(imageFilename=None, region=None):
    """
    TODO
    """

    if imageFilename is None:
        tmpFilename = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
    else:
        tmpFilename = imageFilename

    # Version 9.2.0 introduced using gnome-screenshot for ImageGrab.grab()
    # on Linux, which is necessary to have screenshots work with Wayland
    # (the replacement for x11.) Therefore, for 3.7 and later, PyScreeze
    # uses/requires 9.2.0.
    if PILLOW_VERSION >= (9, 2, 0) and GNOMESCREENSHOT_EXISTS:
        # Pillow doesn't need tmpFilename because it works entirely in memory and doesn't
        # need to save an image file to disk.
        im = ImageGrab.grab()  # use Pillow's grab() for Pillow 9.2.0 and later.

        if imageFilename is not None:
            im.save(imageFilename)

        if region is None:
            # Return the full screenshot.
            return im
        else:
            # Return just a region of the screenshot.
            assert len(region) == 4, 'region argument must be a tuple of four ints'  # TODO fix this
            assert isinstance(region[0], int) and isinstance(region[1], int) and isinstance(region[2], int) and isinstance(region[3], int), 'region argument must be a tuple of four ints'
            im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
            return im
    elif RUNNING_X11 and SCROT_EXISTS:  # scrot only runs on X11, not on Wayland.
        # Even if gnome-screenshot exists, use scrot on X11 because gnome-screenshot
        # has this annoying screen flash effect that you can't disable, but scrot does not.
        subprocess.call(['scrot', '-z', tmpFilename])
    elif GNOMESCREENSHOT_EXISTS:  # gnome-screenshot runs on Wayland and X11.
        subprocess.call(['gnome-screenshot', '-f', tmpFilename])
    elif RUNNING_WAYLAND and SCROT_EXISTS and not GNOMESCREENSHOT_EXISTS:
        raise PyScreezeException(
            'Your computer uses the Wayland window system. Scrot works on the X11 window system but not Wayland. You must install gnome-screenshot by running `sudo apt install gnome-screenshot`'  # noqa
        )
    else:
        raise Exception(
            'To take screenshots, you must install Pillow version 9.2.0 or greater and gnome-screenshot by running `sudo apt install gnome-screenshot`'  # noqa
        )

    im = Image.open(tmpFilename)

    if region is not None:
        assert len(region) == 4, 'region argument must be a tuple of four ints'
        assert isinstance(region[0], int) and isinstance(region[1], int) and isinstance(region[2], int) and isinstance(region[3], int), 'region argument must be a tuple of four ints'
        im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
        os.unlink(tmpFilename)  # delete image of entire screen to save cropped version
        im.save(tmpFilename)
    else:
        # force loading before unlinking, Image.open() is lazy
        im.load()

    if imageFilename is None:
        os.unlink(tmpFilename)
    return im


def _kmp(needle, haystack, _dummy):  # Knuth-Morris-Pratt search algorithm implementation (to be used by screen capture)
    """
    TODO
    """
    # build table of shift amounts
    shifts = [1] * (len(needle) + 1)
    shift = 1
    for pos in range(len(needle)):
        while shift <= pos and needle[pos] != needle[pos - shift]:
            shift += shifts[pos - shift]
        shifts[pos + 1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in haystack:
        while matchLen == len(needle) or matchLen >= 0 and needle[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(needle):
            yield startPos


def _steppingFind(needle, haystack, step):
    """
    TODO
    """
    for startPos in range(0, len(haystack) - len(needle) + 1):
        foundMatch = True
        for pos in range(0, len(needle), step):
            if haystack[startPos + pos] != needle[pos]:
                foundMatch = False
                break
        if foundMatch:
            yield startPos


def center(coords):
    """
    Returns a `Point` object with the x and y set to an integer determined by the format of `coords`.

    The `coords` argument is a 4-integer tuple of (left, top, width, height).

    For example:

    >>> center((10, 10, 6, 8))
    Point(x=13, y=14)
    >>> center((10, 10, 7, 9))
    Point(x=13, y=14)
    >>> center((10, 10, 8, 10))
    Point(x=14, y=15)
    """

    # TODO - one day, add code to handle a Box namedtuple.
    return Point(coords[0] + int(coords[2] / 2), coords[1] + int(coords[3] / 2))


def pixelMatchesColor(x, y, expectedRGBColor, tolerance=0):
    """
    Return True if the pixel at x, y is matches the expected color of the RGB
    tuple, each color represented from 0 to 255, within an optional tolerance.
    """

    # TODO DEPRECATE THIS FUNCTION

    # Note: Automate the Boring Stuff 2nd edition documented that you could call
    # pixelMatchesColor((x, y), rgb) instead of pixelMatchesColor(x, y, rgb).
    # Lets correct that for the 1.0 release.
    if isinstance(x, collections.abc.Sequence) and len(x) == 2:
        raise TypeError('pixelMatchesColor() has updated and no longer accepts a tuple of (x, y) values for the first argument. Pass these arguments as two separate arguments instead: pixelMatchesColor(x, y, rgb) instead of pixelMatchesColor((x, y), rgb)')

    pix = pixel(x, y)
    if len(pix) == 3 or len(expectedRGBColor) == 3:  # RGB mode
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4:  # RGBA mode
        r, g, b, a = pix
        exR, exG, exB, exA = expectedRGBColor
        return (
            (abs(r - exR) <= tolerance)
            and (abs(g - exG) <= tolerance)
            and (abs(b - exB) <= tolerance)
            and (abs(a - exA) <= tolerance)
        )
    else:
        assert False, (
            'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s'  # noqa
            % (len(pix), len(expectedRGBColor))
        )


def pixel(x, y):
    """
    Returns the color of the screen pixel at x, y as an RGB tuple, each color represented from 0 to 255.
    """

    # Note: Automate the Boring Stuff 2nd edition documented that you could call
    # pixel((x, y), rgb) instead of pixel(x, y, rgb).
    # Lets correct that for the 1.0 release.
    if isinstance(x, collections.abc.Sequence) and len(x) == 2:
        raise TypeError('pixel() has updated and no longer accepts a tuple of (x, y) values for the first argument. Pass these arguments as two separate arguments instead: pixel(x, y) instead of pixel((x, y))')


    if sys.platform == 'win32':
        # On Windows, calling GetDC() and GetPixel() is twice as fast as using our screenshot() function.
        with __win32_openDC() as hdc:  # handle will be released automatically
            color = windll.gdi32.GetPixel(hdc, x, y)
            if color < 0:
                raise WindowsError("windll.gdi32.GetPixel failed : return {}".format(color))
            # color is in the format 0xbbggrr https://msdn.microsoft.com/en-us/library/windows/desktop/dd183449(v=vs.85).aspx
            bbggrr = "{:0>6x}".format(color)  # bbggrr => 'bbggrr' (hex)
            b, g, r = (int(bbggrr[i : i + 2], 16) for i in range(0, 6, 2))
            return (r, g, b)
    else:
        # Need to select only the first three values of the color in
        # case the returned pixel has an alpha channel
        return RGB(*(screenshot().getpixel((x, y))[:3]))


# set the screenshot() function based on the platform running this module
if sys.platform == 'darwin':
    screenshot = _screenshot_osx
elif sys.platform == 'win32':
    screenshot = _screenshot_win32
elif sys.platform.startswith('linux'):
    # Everything else is considered to be Linux.
    screenshot = _screenshot_linux
else:
    raise NotImplementedError('PyScreeze is not supported on platform ' + sys.platform)


# set the locateAll function to use opencv if possible; python 3 needs opencv 3.0+
# TODO - Should this raise an exception if zero instances of the image can be found
# on the screen, instead of always returning a generator?
locateAll = _locateAll_pillow
if _useOpenCV:
    locateAll = _locateAll_opencv
    if not RUNNING_PYTHON_2 and cv2.__version__ < '3':
        locateAll = _locateAll_pillow
