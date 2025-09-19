"""
Enhanced Metafile backend.  See http://pyemf.sourceforge.net for the EMF
driver library.
"""
import pyemf

import math, re

from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import RendererBase, GraphicsContextBase, \
    FigureManagerBase, FigureCanvasBase
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from matplotlib.font_manager import findfont, FontProperties
from matplotlib.ft2font import FT2Font, KERNING_UNFITTED, KERNING_DEFAULT, KERNING_UNSCALED

from matplotlib.path import Path
from matplotlib.transforms import Affine2D

# Font handling stuff snarfed from backend_ps, but only using TTF fonts
# from numpy import long

_fontd = {}

# Debug print stuff
debugHandle = False
debugPrint = False
debugText = False


# TODO compatibility
def quad2cubic(q0x, q0y, q1x, q1y, q2x, q2y):
    """
    Converts a quadratic Bezier curve to a cubic approximation.

    The inputs are the *x* and *y* coordinates of the three control
    points of a quadratic curve, and the output is a tuple of *x* and
    *y* coordinates of the four control points of the cubic curve.
    """
    # TODO: Candidate for deprecation -- no longer used internally

    # c0x, c0y = q0x, q0y
    c1x, c1y = q0x + 2. / 3. * (q1x - q0x), q0y + 2. / 3. * (q1y - q0y)
    c2x, c2y = c1x + 1. / 3. * (q2x - q0x), c1y + 1. / 3. * (q2y - q0y)
    # c3x, c3y = q2x, q2y
    return q0x, q0y, c1x, c1y, c2x, c2y, q2x, q2y


# Hashable font properties class.  In EMF, angle of rotation is a part
# of the font properties, so a handle to a new font must be obtained
# if the rotation changes.
class EMFFontProperties(FontProperties):
    def __init__(self, other, angle):
        FontProperties.__init__(self,
                                other.get_family(),
                                other.get_style(),
                                other.get_variant(),
                                other.get_weight(),
                                other.get_stretch(),
                                other.get_size())
        self._angle = angle

    def __hash__(self):
        return hash((FontProperties.__hash__(self), self._angle))

    def __str__(self):
        return str((FontProperties.__str__(self), self._angle))

    def set_angle(self, angle):
        self._angle = angle

    def get_angle(self):
        return self._angle


class EMFPen:
    """Hashable pen (line style) properties."""

    def __init__(self, emf, gc):
        self.emf = emf
        self.gc = gc

        r, g, b = gc.get_rgb()[:3]
        self.r = int(r * 255)
        self.g = int(g * 255)
        self.b = int(b * 255)
        self.width = int(gc.get_linewidth())

        self.style = 0
        self.set_linestyle()
        if debugHandle: print(
            "EMFPen: style=%d width=%d rgb=(%d,%d,%d)" % (self.style, self.width, self.r, self.g, self.b))

    def __hash__(self):
        return hash((self.style, self.width, self.r, self.g, self.b))

    def set_linestyle(self):
        # Hack.  Negative width lines will not get drawn.
        if self.width < 0:
            self.style = pyemf.PS_NULL
        else:
            styles = {'solid': pyemf.PS_SOLID, 'dashed': pyemf.PS_DASH,
                      'dashdot': pyemf.PS_DASHDOT, 'dotted': pyemf.PS_DOT}
            # TODO
            # style=styles.get(self.gc.get_linestyle('solid'))
            # style=self.gc.get_linestyle('solid')
            # if debugHandle: print("EMFPen: style=%s" % style)
            # if style in styles:
            #     self.style=styles[style]
            # else:
            self.style = pyemf.PS_SOLID

    def get_handle(self):
        handle = self.emf.CreatePen(self.style, self.width, (self.r, self.g, self.b))
        return handle


class EMFBrush:
    """Hashable brush (fill style) properties."""

    def __init__(self, emf, rgb):
        self.emf = emf
        r, g, b = rgb[:3]
        self.r = int(r * 255)
        self.g = int(g * 255)
        self.b = int(b * 255)

    def __hash__(self):
        return hash((self.r, self.g, self.b))

    def get_handle(self):
        return self.emf.CreateSolidBrush((self.r, self.g, self.b))


class RendererEMF(RendererBase):
    """
    The renderer handles drawing/rendering operations through a
    pyemf.EMF instance.
    """

    fontweights = {
        100: pyemf.FW_NORMAL,
        200: pyemf.FW_NORMAL,
        300: pyemf.FW_NORMAL,
        400: pyemf.FW_NORMAL,
        500: pyemf.FW_NORMAL,
        600: pyemf.FW_BOLD,
        700: pyemf.FW_BOLD,
        800: pyemf.FW_BOLD,
        900: pyemf.FW_BOLD,
        'ultralight': pyemf.FW_ULTRALIGHT,
        'light': pyemf.FW_LIGHT,
        'normal': pyemf.FW_NORMAL,
        'medium': pyemf.FW_MEDIUM,
        'semibold': pyemf.FW_SEMIBOLD,
        'bold': pyemf.FW_BOLD,
        'heavy': pyemf.FW_HEAVY,
        'ultrabold': pyemf.FW_ULTRABOLD,
        'black': pyemf.FW_BLACK,
    }

    def __init__(self, outfile, width, height, dpi):
        """Initialize the renderer with a gd image instance."""
        self.outfile = outfile

        # a map from get_color args to colors
        self._cached = {}

        # dict of hashed properties to already created font handles
        self._fontHandle = {}

        self.lastHandle = {'font': -1, 'pen': -1, 'brush': -1}

        self.emf = pyemf.EMF(width, height, dpi, 'in')

        self.width = int(width * dpi)
        self.height = int(height * dpi)
        self.dpi = dpi
        self.pointstodpi = dpi / 72.0
        self.hackPointsForMathExponent = 2.0

        # set background transparent for text
        self.emf.SetBkMode(pyemf.TRANSPARENT)
        # set baseline for text to be bottom left corner
        self.emf.SetTextAlign(pyemf.TA_BOTTOM | pyemf.TA_LEFT)

        self._lastClipRect = None

        if debugPrint: print("RendererEMF: (%f,%f) %s dpi=%f" % (self.width, self.height, outfile, dpi))

    def save(self):
        self.emf.save(self.outfile)

    def draw_arc(self, gcEdge, rgbFace, x, y, width, height, angle1, angle2, rotation):
        """
        Draw an arc using GraphicsContext instance gcEdge, centered at x,y,
        with width and height and angles from 0.0 to 360.0
        0 degrees is at 3-o'clock
        positive angles are anti-clockwise

        If the color rgbFace is not None, fill the arc with it.
        """
        if debugPrint: print("draw_arc: (%f,%f) angles=(%f,%f) w,h=(%f,%f)" % (x, y, angle1, angle2, width, height))
        pen = self.select_pen(gcEdge)
        brush = self.select_brush(rgbFace)

        # This algorithm doesn't work very well on small circles
        # because of rounding error.  This shows up most obviously on
        # legends where the circles are small anyway, and it is
        # compounded by the fact that it puts several circles right
        # next to each other so the differences are obvious.
        hw = width / 2
        hh = height / 2
        x1 = int(x - width / 2)
        y1 = int(y - height / 2)
        if brush:
            self.emf.Pie(int(x - hw), int(self.height - (y - hh)), int(x + hw), int(self.height - (y + hh)),
                         int(x + math.cos(angle1 * math.pi / 180.0) * hw),
                         int(self.height - (y + math.sin(angle1 * math.pi / 180.0) * hh)),
                         int(x + math.cos(angle2 * math.pi / 180.0) * hw),
                         int(self.height - (y + math.sin(angle2 * math.pi / 180.0) * hh)))
        else:
            self.emf.Arc(int(x - hw), int(self.height - (y - hh)), int(x + hw), int(self.height - (y + hh)),
                         int(x + math.cos(angle1 * math.pi / 180.0) * hw),
                         int(self.height - (y + math.sin(angle1 * math.pi / 180.0) * hh)),
                         int(x + math.cos(angle2 * math.pi / 180.0) * hw),
                         int(self.height - (y + math.sin(angle2 * math.pi / 180.0) * hh)))

    def handle_clip_rectangle(self, gc):
        new_bounds = gc.get_clip_rectangle()
        if new_bounds is not None:
            new_bounds = new_bounds.bounds
        if self._lastClipRect != new_bounds:
            self._lastClipRect = new_bounds
            if new_bounds is None:
                # use the maximum rectangle to disable clipping
                x, y, width, height = (0, 0, self.width, self.height)
            else:
                x, y, width, height = new_bounds
            self.emf.BeginPath()
            self.emf.MoveTo(int(x), int(self.height - y))
            self.emf.LineTo(int(x) + int(width), int(self.height - y))
            self.emf.LineTo(int(x) + int(width), int(self.height - y) - int(height))
            self.emf.LineTo(int(x), int(self.height - y) - int(height))
            self.emf.CloseFigure()
            self.emf.EndPath()
            self.emf.SelectClipPath()

    def convert_path(self, tpath):
        self.emf.BeginPath()
        last_points = None
        for points, code in tpath.iter_segments():
            points = [int(point) for point in points]
            if code == Path.MOVETO:
                self.emf.MoveTo(*points)
            elif code == Path.CLOSEPOLY:
                self.emf.CloseFigure()
            elif code == Path.LINETO:
                self.emf.LineTo(*points)
            elif code == Path.CURVE3:
                points = quad2cubic(*(tuple(last_points[-2:]) + tuple(points)))
                points = [int(point) for point in points]
                self.emf.PolyBezierTo(tuple(zip(points[2::2], points[3::2])))
            elif code == Path.CURVE4:
                self.emf.PolyBezierTo(tuple(zip(points[::2], points[1::2])))
            last_points = points
        self.emf.EndPath()

    def draw_path(self, gc, path, transform, rgbFace=None):
        """
        Draws a :class:`~matplotlib.path.Path` instance using the
        given affine transform.
        """
        self.handle_clip_rectangle(gc)
        gc._rgb = gc._rgb[:3]
        self.select_pen(gc)
        self.select_brush(rgbFace)
        transform = transform + Affine2D().scale(1.0, -1.0).translate(0.0, self.height)
        tpath = transform.transform_path(path)
        self.convert_path(tpath)
        if rgbFace is None:
            self.emf.StrokePath()
        else:
            self.emf.StrokeAndFillPath()

    def draw_image(self, x, y, im, bbox, clippath=None, clippath_trans=None):
        """
        Draw the Image instance into the current axes; x is the
        distance in pixels from the left hand side of the canvas. y is
        the distance from the origin.  That is, if origin is upper, y
        is the distance from top.  If origin is lower, y is the
        distance from bottom

        bbox is a matplotlib.transforms.BBox instance for clipping, or
        None
        """

        # pyemf2 currently doesn't support bitmaps.

        pass

    def draw_line(self, gc, x1, y1, x2, y2):
        """Draw a single line from x1,y1 to x2,y2."""
        if debugPrint: print("draw_line: (%f,%f) - (%f,%f)" % (x1, y1, x2, y2))

        if self.select_pen(gc):
            self.emf.Polyline(((x1, self.height - y1), (x2, self.height - y2)))
        else:
            if debugPrint: print("draw_line: optimizing away (%f,%f) - (%f,%f)" % (x1, y1, x2, y2))

    def draw_lines(self, gc, x, y):
        """
        x and y are equal length arrays, draw lines connecting each
        point in x, y
        """
        if debugPrint: print("draw_lines: %d points" % len(str(x)))

        # optimize away anything that won't actually be drawn.  Edge
        # style must not be PS_NULL for it to appear on screen.
        if self.select_pen(gc):
            points = [(x[i], self.height - y[i]) for i in range(len(x))]
            self.emf.Polyline(points)

    def draw_point(self, gc, x, y):
        """
        Draw a single point at x,y
        Where 'point' is a device-unit point (or pixel), not a matplotlib point
        """
        pen = EMFPen(self.emf, gc)
        self.emf.SetPixel(x, self.height - y, (pen.r, pen.g, pen.b))

    def draw_polygon(self, gcEdge, rgbFace, points):
        """
        Draw a polygon using the GraphicsContext instance gc.
        points is a len vertices tuple, each element
        giving the x,y coords a vertex

        If the color rgbFace is not None, fill the polygon with it
        """
        if debugPrint: print("draw_polygon: %d points" % len(points))

        # optimize away anything that won't actually draw.  Either a
        # face color or edge style must be defined
        pen = self.select_pen(gcEdge)
        brush = self.select_brush(rgbFace)
        if pen or brush:
            points = [(x, self.height - y) for x, y in points]
            self.emf.Polygon(points)
        else:
            points = [(x, self.height - y) for x, y in points]
            if debugPrint: print("draw_polygon: optimizing away polygon: %d points = %s" % (len(points), str(points)))

    def draw_rectangle(self, gcEdge, rgbFace, x, y, width, height):
        """
        Draw a non-filled rectangle using the GraphicsContext instance gcEdge,
        with lower left at x,y with width and height.

        If rgbFace is not None, fill the rectangle with it.
        """
        if debugPrint: print("draw_rectangle: (%f,%f) w=%f,h=%f" % (x, y, width, height))

        # optimize away anything that won't actually draw.  Either a
        # face color or edge style must be defined
        pen = self.select_pen(gcEdge)
        brush = self.select_brush(rgbFace)
        if pen or brush:
            self.emf.Rectangle(int(x), int(self.height - y), int(x) + int(width), int(self.height - y) - int(height))
        else:
            if debugPrint: print("draw_rectangle: optimizing away (%f,%f) w=%f,h=%f" % (x, y, width, height))

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
        """
        Draw the text.Text instance s at x,y (display coords) with font
        properties instance prop at angle in degrees, using GraphicsContext gc
        """
        self.handle_clip_rectangle(gc)
        self.emf.SetTextColor(gc.get_rgb()[:3])
        self.select_font(prop, angle)

        # Заменяем специальные символы на ASCII эквиваленты
        s = s.replace('\u2212', '-')  # Математический минус на обычный
        s = s.replace('\u2013', '-')  # En dash на минус
        s = s.replace('\u2014', '-')  # Em dash на минус
        s = s.replace('\u00d7', 'x')  # Знак умножения на x
        s = s.replace('\u00b0', '*')  # Градус на звездочку
        s = s.replace('\u03bc', 'u')  # мю на u
        s = s.replace('\u03b1', 'a')  # альфа на a
        s = s.replace('\u03b2', 'b')  # бета на b
        s = s.replace('\u03b3', 'y')  # гамма на y

        try:
            text_bytes = s.encode('cp1251')
            self.emf.TextOut(int(x), int(y), text_bytes)
        except UnicodeEncodeError:
            # Если все еще не удается закодировать, используем только ASCII символы
            text_bytes = s.encode('ascii', errors='replace')
            self.emf.TextOut(int(x), int(y), text_bytes)

    def draw_plain_text(self, gc, x, y, s, prop, angle):
        """Draw a text string verbatim; no conversion is done."""
        self.select_font(prop, angle)

        hackoffsetper300dpi = 10
        xhack = math.sin(angle * math.pi / 180.0) * hackoffsetper300dpi * self.dpi / 300.0
        yhack = math.cos(angle * math.pi / 180.0) * hackoffsetper300dpi * self.dpi / 300.0

        # Заменяем специальные символы на ASCII эквиваленты
        s = s.replace('\u2212', '-')  # Математический минус на обычный
        s = s.replace('\u2013', '-')  # En dash на минус
        s = s.replace('\u2014', '-')  # Em dash на минус
        s = s.replace('\u00d7', 'x')  # Знак умножения на x
        s = s.replace('\u00b0', '*')  # Градус на звездочку
        s = s.replace('\u03bc', 'u')  # мю на u
        s = s.replace('\u03b1', 'a')  # альфа на a
        s = s.replace('\u03b2', 'b')  # бета на b
        s = s.replace('\u03b3', 'y')  # гамма на y

        try:
            text_bytes = s.encode('cp1251')
            self.emf.TextOut(int(x + xhack), int(y + yhack), text_bytes)
        except UnicodeEncodeError:
            # Если все еще не удается закодировать, используем только ASCII символы
            text_bytes = s.encode('ascii', errors='replace')
            self.emf.TextOut(int(x + xhack), int(y + yhack), text_bytes)

    def draw_math_text(self, gc, x, y, s, prop, angle):
        """
        Draw a subset of TeX, currently handles exponents only.  Since
        pyemf doesn't have any raster functionality yet, the
        texmanager.get_rgba won't help.
        """
        if debugText: print("draw_math_text: (%f,%f) %d degrees: '%s'" % (x, y, angle, s))

        s = s[1:-1]  # strip the $ from front and back
        match = re.match("10\^\{(.+)\}", s)
        if match:
            exp = match.group(1)
            if debugText: print(" exponent=%s" % exp)
            font = self._get_font_ttf(prop)
            font.set_text("10", 0.0)
            w, h = font.get_width_height()
            w /= 64.0  # convert from subpixels
            h /= 64.0
            self.draw_plain_text(gc, x, y, "10", prop, angle)
            propexp = prop.copy()
            propexp.set_size(prop.get_size_in_points() * .8)
            self.draw_plain_text(gc, x + w + self.points_to_pixels(self.hackPointsForMathExponent), y - (h / 2), exp,
                                 propexp, angle)
        else:
            # if it isn't an exponent, then render the raw TeX string.
            self.draw_plain_text(gc, x, y, s, prop, angle)
            # TODO

    def get_math_text_width_height(self, s, prop):
        """
        get the width and height in display coords of the string s
        with FontPropertry prop, ripped right out of backend_ps.  This
        method must be kept in sync with draw_math_text.
        """
        # TODO
        if debugText: print("get_math_text_width_height:")
        s = s[1:-1]  # strip the $ from front and back
        match = re.match("10\^\{(.+)\}", s)
        if match:
            exp = match.group(1)
            if debugText: print(" exponent=%s" % exp)
            font = self._get_font_ttf(prop)
            font.set_text("10", 0.0)
            w1, h1 = font.get_width_height()

            propexp = prop.copy()
            propexp.set_size(prop.get_size_in_points() * .8)
            fontexp = self._get_font_ttf(propexp)
            fontexp.set_text(exp, 0.0)
            w2, h2 = fontexp.get_width_height()
            w = w1 + w2
            h = h1 + (h2 / 2)
            w /= 64.0  # convert from subpixels
            h /= 64.0
            w += self.points_to_pixels(self.hackPointsForMathExponent)
            if debugText: print(" math string=%s w,h=(%f,%f)" % (s, w, h))
        else:
            w, h = self.get_text_width_height(s, prop, False)
        return w, h

    def get_text_width_height_descent(self, s, prop, ismath):
        """Get the width and height in display coords of the string s with FontPropertry prop."""
        # if ismath: s = self.strip_math(s)  # TODO
        font = self._get_font_ttf(prop)
        font.set_text(s, 0.0)
        w, h = font.get_width_height()
        w /= 64.0  # convert from subpixels
        h /= 64.0
        d = font.get_descent()
        d /= 64.0
        return w, h, d

    def flipy(self):
        """return true if y small numbers are top for renderer
        Is used for drawing text (text.py) and images (image.py) only
        """
        return True

    def get_canvas_width_height(self):
        """
        return the canvas width and height in display coords
        """
        return self.width, self.height

    def set_handle(self, type, handle):
        """
        Update the EMF file with the current handle, but only if it
        isn't the same as the last one.  Don't want to flood the file
        with duplicate info.
        """
        if self.lastHandle[type] != handle:
            self.emf.SelectObject(handle)
            self.lastHandle[type] = handle

    def get_font_handle(self, prop, angle):
        """
        Look up the handle for the font based on the dict of
        properties *and* the rotation angle, since in EMF the font
        rotation is a part of the font definition.
        """
        prop = EMFFontProperties(prop, angle)
        size = int(prop.get_size_in_points() * self.pointstodpi)
        # Явно используем Arial для поддержки кириллицы
        face = "Arial"
        key = hash(prop)
        handle = self._fontHandle.get(key)
        if handle is None:
            handle = self.emf.CreateFont(-size, 0, int(angle) * 10, int(angle) * 10,
                                         self.fontweights.get(prop.get_weight(), pyemf.FW_NORMAL),
                                         int(prop.get_style() == 'italic'),
                                         0, 0,
                                         pyemf.RUSSIAN_CHARSET,  # Используем русскую кодировку
                                         pyemf.OUT_DEFAULT_PRECIS,
                                         pyemf.CLIP_DEFAULT_PRECIS,
                                         pyemf.DEFAULT_QUALITY,
                                         pyemf.DEFAULT_PITCH | pyemf.FF_DONTCARE,
                                         face)
            if debugHandle: print("get_font_handle: creating handle=%d for face=%s size=%d" % (handle, face, size))
            self._fontHandle[key] = handle
        if debugHandle: print(" found font handle %d for face=%s size=%d" % (handle, face, size))
        self.set_handle("font", handle)
        return handle

    def select_font(self, prop, angle):
        handle = self.get_font_handle(prop, angle)
        self.set_handle("font", handle)

    def select_pen(self, gc):
        """
        Select a pen that includes the color, line width and line
        style.  Return the pen if it will draw a line, or None if the
        pen won't produce any output (i.e. the style is PS_NULL)
        """
        pen = EMFPen(self.emf, gc)
        key = hash(pen)
        handle = self._fontHandle.get(key)
        if handle is None:
            handle = pen.get_handle()
            self._fontHandle[key] = handle
        if debugHandle: print(" found pen handle %d" % handle)
        self.set_handle("pen", handle)
        if pen.style != pyemf.PS_NULL:
            return pen
        else:
            return None

    def select_brush(self, rgb):
        """
        Select a fill color, and return the brush if the color is
        valid or None if this won't produce a fill operation.
        """
        if rgb is not None:
            brush = EMFBrush(self.emf, rgb)
            key = hash(brush)
            handle = self._fontHandle.get(key)
            if handle is None:
                handle = brush.get_handle()
                self._fontHandle[key] = handle
            if debugHandle: print(" found brush handle %d" % handle)
            self.set_handle("brush", handle)
            return brush
        else:
            return None

    def _get_font_ttf(self, prop):
        """
        get the true type font properties, used because EMFs on
        windows will use true type fonts.
        """
        key = hash(prop)
        font = _fontd.get(key)
        if font is None:
            fname = findfont(prop)
            if debugText: print("_get_font_ttf: name=%s" % fname)
            font = FT2Font(str(fname))
            _fontd[key] = font
        font.clear()
        size = prop.get_size_in_points()
        font.set_size(size, self.dpi)

        return font

    def get_text_width_height(self, s, prop, ismath):
        """
        get the width and height in display coords of the string s
        with FontPropertry prop, ripped right out of backend_ps
        """
        if debugText: print("get_text_width_height: ismath=%s properties: %s" % (str(ismath), str(prop)))
        if ismath:
            if debugText: print(" MATH TEXT! = %s" % str(ismath))
            w, h = self.get_math_text_width_height(s, prop)
            return w, h

        font = self._get_font_ttf(prop)
        font.set_text(s, 0.0)
        w, h = font.get_width_height()
        w /= 64.0  # convert from subpixels
        h /= 64.0
        if debugText: print(" text string=%s w,h=(%f,%f)" % (s, w, h))
        return w, h

    def new_gc(self):
        return GraphicsContextEMF()

    def points_to_pixels(self, points):
        # if backend doesn't have dpi, eg, postscript or svg
        # return points
        # elif backend assumes a value for pixels_per_inch
        # return points/72.0 * self.dpi.get() * pixels_per_inch/72.0
        # else
        return points / 72.0 * self.dpi


class GraphicsContextEMF(GraphicsContextBase):
    """
    The graphics context provides the color, line styles, etc...  See the gtk
    and postscript backends for examples of mapping the graphics context
    attributes (cap styles, join styles, line widths, colors) to a particular
    backend.  In GTK this is done by wrapping a gtk.gdk.GC object and
    forwarding the appropriate calls to it using a dictionary mapping styles
    to gdk constants.  In Postscript, all the work is done by the renderer,
    mapping line styles to postscript calls.

    If it's more appropriate to do the mapping at the renderer level (as in
    the postscript backend), you don't need to override any of the GC methods.
    If it's more appropriate to wrap an instance (as in the GTK backend) and
    do the mapping here, you'll need to override several of the setter
    methods.

    The base GraphicsContext stores colors as a RGB tuple on the unit
    interval, eg, (0.5, 0.0, 1.0). You may need to map this to colors
    appropriate for your backend.
    """
    pass


########################################################################
#
# The following functions and classes are for pylab and implement
# window/figure managers, etc...
#
########################################################################


def draw_if_interactive():
    """
    For image backends - is not required
    For GUI backends - this should be overriden if drawing should be done in
    interactive python mode
    """
    pass


def show():
    """
    For image backends - is not required
    For GUI backends - show() is usually the last line of a pylab script and
    tells the backend that it is time to draw.  In interactive mode, this may
    be a do nothing func.  See the GTK backend for an example of how to handle
    interactive versus batch mode
    """
    for manager in Gcf.get_all_fig_managers():
        # do something to display the GUI
        pass


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    # if a main-level app must be created, this is the usual place to
    # do it -- see backend_wx, backend_wxagg and backend_tkagg for
    # examples.  Not all GUIs require explicit instantiation of a
    # main-level app (egg backend_gtk, backend_gtkagg) for pylab
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """Create a new figure manager instance for the given figure."""
    canvas = FigureCanvasEMF(figure)
    manager = FigureManagerEMF(canvas, num)
    return manager


class FigureCanvasEMF(FigureCanvasBase):
    """
    The canvas the figure renders into.  Calls the draw and print fig
    methods, creates the renderers, etc...

    Public attribute

      figure - A Figure instance
    """

    def draw(self):
        """
        Draw the figure using the renderer
        """
        pass

    filetypes = {'emf': 'Enhanced Metafile'}

    def print_emf(self, filename, dpi=300, **kwargs):
        width, height = self.figure.get_size_inches()
        renderer = RendererEMF(filename, width, height, dpi)
        self.figure.draw(renderer)
        renderer.save()

    def get_default_filetype(self):
        return 'emf'


class FigureManagerEMF(FigureManagerBase):
    """
    Wrap everything up into a window for the pylab interface

    For non interactive backends, the base class does all the work
    """
    pass


########################################################################
#
# Now just provide the standard names that backend.__init__ is expecting
#
########################################################################


FigureManager = FigureManagerEMF
