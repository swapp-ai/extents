import importlib.metadata
import pathlib


__version__ = importlib.metadata.version("extents")
""" Package version -- read only value """


__version_tuple__ = tuple(__version__.split('.'))
""" Package version tuple -- read only value """


__package_root__ = pathlib.Path(__file__).parent.parent
""" Path of package root in filesystem -- read only value """


from .extents import *
