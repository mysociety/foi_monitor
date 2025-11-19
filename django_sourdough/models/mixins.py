"""
Compatibility shim for django_sourdough.models.mixins.

This provides the model mixins that migrations reference without requiring
the full django_sourdough package.
"""

# Import from our local implementation
from pi_monitor.model_mixins import StockModelHelpers

__all__ = ['StockModelHelpers']
