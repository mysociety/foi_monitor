# Migration Guide: From django-sourdough to Standard Django

This document explains the changes made to convert from django-sourdough's non-standard view approach to standard Django class-based views.

## Summary of Changes

### 1. Django Version Upgrade
- **Before:** Django 3.1.6
- **After:** Django 4.2+ (LTS)
- **Reason:** Modern Django with better security, performance, and features

### 2. Removed Dependencies
- **django-sourdough** - Removed entirely, replaced with local implementations

### 3. New Files Created

#### `pi_monitor/urls.py`
Standard Django URL configuration file that defines all routes:
```python
urlpatterns = [
    re_path(r"^$", views.OverviewView.as_view(), name="overview"),
    re_path(r"^(?P<jurisdiction_slug>.*)/...", views.HomeView.as_view(), name="home"),
    # ... more routes
]
```

#### `pi_monitor/base_views.py`
Local implementations of view functionality:
- `LogicalViewMixin` - Provides prelogic/logic/postlogic pattern
- `SocialViewMixin` - Handles social media metadata
- `StandardLogicalView` - Combined view extending Django's TemplateView
- `prelogic` and `postlogic` decorators

#### `pi_monitor/model_mixins.py`
Local implementations of model mixins:
- `EasyBulkModel` - Bulk creation with queuing
- `StockModelHelpers` - Common model helpers
- `FlexiBulkModel` - Combined model class

#### `django_sourdough/` (Compatibility Shims)
Provides compatibility layer for:
- Existing migrations that reference django_sourdough.models.mixins
- research_common submodule that imports from django_sourdough.views

### 4. Modified Files

#### `pi_monitor/views.py`
**Before:**
```python
class HomeView(LocalView):
    template = "pi_monitor/home.html"
    url_patterns = [r"^(.*)/"]
    url_name = "pi.home"
    args = ["jurisdiction_slug"]
```

**After:**
```python
class HomeView(LocalView):
    template_name = "pi_monitor/home.html"
    # URL patterns now in urls.py
    # Arguments come from URL kwargs automatically
```

#### `proj/urls.py`
**Before:**
```python
from django_sourdough.views import include_view

url(r"^sites/{0}/".format(settings.SITE_SLUG),
    include_view("{0}.views".format(settings.CORE_APP_NAME)))
```

**After:**
```python
from django.urls import include, path

path(f"sites/{settings.SITE_SLUG}/",
     include(f"{settings.CORE_APP_NAME}.urls"))
```

#### `proj/settings.py`
- Removed `django_sourdough` from `INSTALLED_APPS`

#### `pyproject.toml`
- Removed `django-sourdough` dependency
- Updated Django to `^4.2`
- Updated django-pipeline to `^3.0`
- Updated markdown and six versions

## How Views Work Now

### URL Configuration
URLs are now defined in `pi_monitor/urls.py` using standard Django patterns:

```python
from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^(?P<jurisdiction_slug>.*)/", views.HomeView.as_view(), name="home"),
]
```

### View Structure
Views inherit from `StandardLogicalView` which extends Django's `TemplateView`:

```python
class HomeView(LocalView):
    template_name = "pi_monitor/home.html"
    
    def logic(self):
        # Access URL parameters as self.jurisdiction_slug (from kwargs)
        self.jurisdiction = Jurisdiction.objects.get(slug=self.jurisdiction_slug)
        # Set attributes that become template context
        self.desc = self.jurisdiction.adapter().get_description()
```

### Key Differences
1. **URL Parameters:** Now come from URL kwargs, not from `args` attribute
2. **Template:** Use `template_name` instead of `template`
3. **URL Patterns:** Defined in `urls.py` not in view classes
4. **Base Class:** Inherit from `StandardLogicalView` instead of `LogicalSocialView`

## Testing Instructions

### 1. Install Dependencies
```bash
poetry install
```

### 2. Run Migrations
```bash
poetry run python manage.py migrate
```

### 3. Create Superuser (if needed)
```bash
poetry run python manage.py createsuperuser
```

### 4. Run Development Server
```bash
poetry run python manage.py runserver
```

### 5. Test Routes
Visit these URLs to verify the application works:
- `http://127.0.0.1:8000/sites/foi-monitor/` - Overview page
- Admin interface should work as before

### 6. Run Linter
```bash
poetry run ruff check .
```

## Backward Compatibility

### Migrations
Existing migrations reference `django_sourdough.models.mixins.StockModelHelpers`. This still works because:
1. We created a compatibility shim at `django_sourdough/models/mixins.py`
2. The shim re-exports `StockModelHelpers` from our local implementation

### Submodules
The `research_common` submodule imports `prelogic` and `postlogic` from django_sourdough. This works because:
1. We created a compatibility shim at `django_sourdough/views/__init__.py`
2. The shim re-exports the decorators from our local implementation

## What About Baking (Static Site Generation)?

The static site generation functionality (`bake.py`) has been marked as legacy. If you need static site generation:

1. The baking commands won't work without django-sourdough
2. You would need to either:
   - Re-add django-sourdough as a dependency
   - Implement a new static site generation approach using Django's built-in capabilities
   - Use a third-party static site generator

For a standard Django web application (non-static), baking is not needed.

## Rollback Plan

If you need to rollback:
1. Restore `django-sourdough` to `pyproject.toml`
2. Downgrade Django to 3.1.6
3. Revert changes to views.py, urls.py, etc.
4. Remove the new files (base_views.py, model_mixins.py, etc.)

## Benefits of This Migration

1. **Standard Django Patterns** - Easier for new developers to understand
2. **Modern Django** - Access to latest features and security updates
3. **Better IDE Support** - Standard patterns work better with autocomplete
4. **Community Support** - Standard Django has extensive documentation
5. **Maintainability** - No dependency on unmaintained django-sourdough package
6. **Testability** - Standard views are easier to test

## Next Steps

1. Update any documentation that references the old view structure
2. Train team members on the new standard Django patterns
3. Consider removing the compatibility shims once all migrations are squashed
4. Update the README with new setup instructions if needed
