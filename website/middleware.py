import sys
from re import compile

from django.http.response import HttpResponseRedirect
from django.conf import settings

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote


class HttpRedirectException(Exception):
    def __init__(self, url, message=""):
        super(self.__class__, self).__init__()
        self.message = message
        self.url = url


class RedirectionMiddleware(object):
    """ Redirect user if RedirectException is raised """
    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, HttpRedirectException):
            return HttpResponseRedirect(exception.url)
        return None


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    if isinstance(settings.LOGIN_EXEMPT_URLS, str):
        EXEMPT_URLS.append(compile(settings.LOGIN_EXEMPT_URLS))
    else:
        EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    Origin:
    http://stackoverflow.com/questions/3214589/django-how-can-i-apply-the-login-required-decorator-to-my-entire-site-excludin
    """
    def process_request(self, request):
        redirect_url = settings.LOGIN_URL + '?next=%s' % quote(request.build_absolute_uri())
        is_authenticated = request.user.is_authenticated() if hasattr(request, "user") else False

        if not is_authenticated:
            path = request.path_info.lstrip('/')

            if not any(m.match(path) for m in EXEMPT_URLS):
                print("Failed to match \"" + str(path) + "\" to " + str(EXEMPT_URLS))
                return HttpResponseRedirect(redirect_url)
