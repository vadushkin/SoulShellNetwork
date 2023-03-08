from django.http import HttpResponseBadRequest


def ajax_required(function):
    """Decorator to validate than a request is AJAX"""

    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
