"""
Base view classes that provide the functionality previously from django-sourdough
but using standard Django class-based views.
"""
from django.views.generic import TemplateView
from django.template import Template, Context
from django.conf import settings


class LogicalViewMixin:
    """
    Provides logic-based view processing similar to django-sourdough's LogicalView.
    
    Views can define:
    - logic() method: Contains the main view logic
    - prelogic_*() methods: Run before logic() in order
    - postlogic_*() methods: Run after logic() in order
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
        """Override to add logic processing to context."""
        context = super().get_context_data(**kwargs)
        
        # Store URL kwargs as instance attributes
        self.record_new = True
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        # Run prelogic, logic, postlogic
        self._prelogic()
        self.logic()
        self._postlogic()
        
        # Add all recorded values to context
        for k in self.values:
            context[k] = getattr(self, k)
        
        # Add extra params
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
    
    def _prelogic(self):
        return self._logic_processing("prelogic")
    
    def _postlogic(self):
        return self._logic_processing("postlogic")
    
    def logic(self):
        """Override this method to add view logic."""
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
        
        process = lambda x: Template(x).render(c_context)
            
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
    Standard Django TemplateView with logical processing and social metadata support.
    
    This replaces the non-standard django-sourdough LogicalSocialView with a 
    standard Django class-based view approach.
    """
    pass
