from authentication.services import jwt_login


class CookieMiddleware:
    """This class makes sure there is an access cookie present and set at login
    It also gets deleted at logout. This cookie is used by Neuroglancer to authenticate
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        if request.user.is_authenticated and not request.COOKIES.get('access'):
            response = jwt_login(response=response, user=request.user)
        elif not request.user.is_authenticated and request.COOKIES.get('access'):
            response.delete_cookie("access")

        return response