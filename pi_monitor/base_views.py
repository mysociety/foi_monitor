"""
Base view classes that provide the functionality previously from django-sourdough
but using standard Django class-based views.
"""
from django.conf import settings
from django.template import Context, Template
from django.views.generic import TemplateView


class GenericDecorator:
    """
    Base class for creating decorators with arguments.
    Used for prelogic and postlogic decorators.
    """
    prefix = ""
    args_map = []
    default_kwargs = {}

    def __init__(self, *args, **kwargs):
        # Map args to kwargs based on args_map
        for i, arg in enumerate(args):
            if i < len(self.args_map):
                kwargs[self.args_map[i]] = arg
        
        # Apply default kwargs
        for k, v in self.default_kwargs.items():
            if k not in kwargs:
                kwargs[k] = v
        
        # Store kwargs as attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __call__(self, func):
        return self.modify_function(func)

    def modify_function(self, obj):
        return obj


class prelogic(GenericDecorator):
    """
    Decorates a function to run before the logic view.
    Accepts an order kwarg to manage competing functions.
    """
    prefix = "prelogic"
    args_map = ["order"]
    default_kwargs = {"order": 5}

    def modify_function(self, obj):
        obj._prefix = self.__class__.prefix
        obj.order = self.order
        return obj


class postlogic(GenericDecorator):
    """
    Decorates a function to run after the logic view.
    Accepts an order kwarg to manage competing functions.
    """
    prefix = "postlogic"
    args_map = ["order"]
    default_kwargs = {"order": 5}

    def modify_function(self, obj):
        obj._prefix = self.__class__.prefix
        obj.order = self.order
        return obj


class LogicalViewMixin:
    """
    Compatibility mixin that provides support for legacy prelogic/postlogic/logic pattern.
    
    For new code, prefer overriding get_context_data() directly (standard Django).
    
    This mixin supports legacy views that use:
    - logic() method: Contains the main view logic
    - @prelogic decorated methods: Run before logic() in order
    - @postlogic decorated methods: Run after logic() in order
    
    The logic() method and decorators are automatically called during get_context_data().
    Any attributes set on self during these methods are automatically added to the context.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.record_new = False
        self.values = []
    
    def __setattr__(self, key, value):
        if hasattr(self, "record_new") and self.record_new:
            self.values.append(key)
        super().__setattr__(key, value)
    
    def get_context_data(self, **kwargs):
        """
        Override to add logic processing to context.
        
        Standard Django pattern: Override this method directly in your views.
        Legacy pattern: Override logic() method instead (for compatibility).
        """
        context = super().get_context_data(**kwargs)
        
        # Store URL kwargs as instance attributes for compatibility
        self.record_new = True
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        # Run legacy prelogic/logic/postlogic pattern
        self._run_prelogic()
        self._run_logic()
        self._run_postlogic()
        
        # Add all recorded values to context
        for k in self.values:
            context[k] = getattr(self, k)
        
        # Add extra params (can be overridden for customization)
        context = self.extra_params(context)
        
        return context
    
    def _logic_processing(self, prefix):
        """Run all pre and post logic functions in order."""
        def keying(v):
            if hasattr(v, "order"):
                return v.order
            else:
                return 5
        
        def ga(k):
            return getattr(self, k)
        
        def passes_func_test(k):
            return hasattr(k, "_prefix") and k._prefix == prefix
        
        def passes_test(k):
            return prefix + "_" in k or passes_func_test(ga(k))
        
        funcs = [k for k in dir(self) if passes_test(k)]
        funcs = [ga(k) for k in funcs]
        funcs.sort(key=lambda x: keying(x))
        for f in funcs:
            f()
    
    def _run_prelogic(self):
        """Run all prelogic methods. For internal use."""
        return self._logic_processing("prelogic")
    
    def _run_postlogic(self):
        """Run all postlogic methods. For internal use."""
        return self._logic_processing("postlogic")
    
    def _run_logic(self):
        """Run the main logic method. For internal use."""
        self.logic()
    
    def logic(self):
        """
        Legacy method for view logic. For compatibility only.
        
        For new code, override get_context_data() directly instead:
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['my_data'] = MyModel.objects.all()
            return context
        """
        pass
    
    def extra_params(self, context):
        """Override to add extra parameters to context."""
        return context


class SocialViewMixin:
    """
    Provides social media metadata functionality.
    Uses class properties for social arguments with template language support.
    """
    share_image = ""
    share_site_name = ""
    share_image_alt = ""
    share_description = ""
    share_title = ""
    share_twitter = ""
    share_url = ""
    twitter_share_image = ""
    page_title = ""

    def extra_params(self, context):
        params = super().extra_params(context)
        if hasattr(settings, "SITE_ROOT"):
            params["SITE_ROOT"] = settings.SITE_ROOT
        extra = {
            "social_settings": self.social_settings(params),
            "page_title": self._page_title(params),
        }
        params.update(extra)
        return params
    
    def _page_title(self, context):
        c_context = Context(context)
        return Template(self.__class__.page_title).render(c_context)
    
    def social_settings(self, context):
        """Run class social settings against template."""
        cls = self.__class__
        
        c_context = Context(context)
        
        def process(x):
            return Template(x).render(c_context)
            
        if cls.twitter_share_image:
            twitter_img = cls.twitter_share_image
        else:
            twitter_img = cls.share_image
            
        di = {
            'share_site_name': process(cls.share_site_name),
            'share_image': process(cls.share_image),
            'twitter_share_image': process(twitter_img),
            'share_image_alt': process(cls.share_image_alt),
            'share_description': process(cls.share_description),
            'share_title': process(cls.share_title),
            'url': process(cls.share_url),
        }
        
        return di


class StandardLogicalView(LogicalViewMixin, SocialViewMixin, TemplateView):
    """
    Standard Django TemplateView with optional legacy logic pattern support.
    
    This view extends Django's TemplateView with:
    - Social metadata handling (share_title, share_description, etc.)
    - Legacy compatibility for prelogic/logic/postlogic pattern
    
    ## Standard Django Pattern (Recommended for new code):
    
    Override get_context_data() directly:
    
        class MyView(StandardLogicalView):
            template_name = "my_template.html"
            
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['items'] = Item.objects.all()
                context['count'] = context['items'].count()
                return context
    
    ## Legacy Pattern (For compatibility with existing code):
    
    Use the logic() method where attributes set on self are auto-added to context:
    
        class MyView(StandardLogicalView):
            template_name = "my_template.html"
            
            def logic(self):
                self.items = Item.objects.all()
                self.count = self.items.count()
                # items and count are automatically added to template context
    
    The legacy pattern is maintained for backward compatibility but new code
    should use standard Django's get_context_data() pattern.
    """
    pass
