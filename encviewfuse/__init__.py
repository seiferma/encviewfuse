from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from pkg_resources import declare_namespace
declare_namespace('encviewfuse')