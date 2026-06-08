"""
Safe EMF backend stub.

Original backend_emf.py depends on pyemf, which is not available on macOS
in this environment. This module keeps the application importable and
disables EMF export with a clear runtime error.

Use PNG/PDF/SVG export on macOS.
"""

from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import FigureManagerBase, FigureCanvasBase
from matplotlib.figure import Figure


EMF_AVAILABLE = False


class EMFUnavailableError(RuntimeError):
    pass


def _raise_emf_unavailable():
    raise EMFUnavailableError(
        "EMF export is unavailable because pyemf is not installed. "
        "On macOS use PNG/PDF/SVG export instead."
    )


class RendererEMF:
    """
    Stub renderer.

    Exists only so imports like `from app.utils.backend_emf import RendererEMF`
    do not crash on macOS.
    """

    def __init__(self, *args, **kwargs):
        _raise_emf_unavailable()


class FigureCanvasEMF(FigureCanvasBase):
    """
    Stub canvas for EMF export.

    Matplotlib/custom code may import this backend, but actual EMF printing
    is disabled on macOS.
    """

    filetypes = {"emf": "Enhanced Metafile"}

    def draw(self):
        pass

    def print_emf(self, filename, dpi=300, **kwargs):
        _raise_emf_unavailable()

    def get_default_filetype(self):
        return "emf"


class FigureManagerEMF(FigureManagerBase):
    pass


def draw_if_interactive():
    pass


def show():
    for manager in Gcf.get_all_fig_managers():
        pass


def new_figure_manager(num, *args, **kwargs):
    FigureClass = kwargs.pop("FigureClass", Figure)
    figure = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, figure)


def new_figure_manager_given_figure(num, figure):
    canvas = FigureCanvasEMF(figure)
    manager = FigureManagerEMF(canvas, num)
    return manager


FigureCanvas = FigureCanvasEMF
FigureManager = FigureManagerEMF