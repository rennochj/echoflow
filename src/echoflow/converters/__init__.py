"""Document conversion engines and interfaces."""

from .base import BaseConverter, ConversionOptions, ConversionResult, converter_registry
from .docling_converter import DoclingConverter

# Register DoclingConverter as the primary converter
try:
    docling_converter = DoclingConverter()
    converter_registry.register(docling_converter)

except Exception as e:
    # If DoclingConverter fails to initialize, log but don't fail the module import
    import logging

    logging.warning(f"Failed to register DoclingConverter: {e}")

__all__ = [
    "BaseConverter",
    "ConversionOptions",
    "ConversionResult",
    "DoclingConverter",
    "converter_registry",
]
