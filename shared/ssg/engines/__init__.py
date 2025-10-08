"""
SSG Engines Package

Contains individual SSG engine implementations organized by technology.
Each engine defines its build process, templates, and optimization features.
"""

from .eleventy import EleventyConfig
from .hugo import HugoConfig
from .astro import AstroConfig
from .jekyll import JekyllConfig
from .nextjs import NextJSConfig
from .nuxt import NuxtConfig
from .gatsby import GatsbyConfig

__all__ = [
    "EleventyConfig",
    "HugoConfig", 
    "AstroConfig",
    "JekyllConfig",
    "NextJSConfig",
    "NuxtConfig", 
    "GatsbyConfig"
]