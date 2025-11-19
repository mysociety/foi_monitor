"""
Compatibility shim for django_sourdough.views.

This provides the decorators that research_common needs without requiring
the full django_sourdough package.
"""

# Import from our local implementation
from pi_monitor.base_views import postlogic, prelogic

__all__ = ['prelogic', 'postlogic']
