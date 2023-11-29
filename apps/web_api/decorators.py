from functools import wraps
from datetime import datetime
from http.cookies import CookieError
import urllib.parse
from common.exceptions import NotLoginError
from common.libs.tokenize_util import decrypt_web_token


def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            uid = 0
            login_time = 0
            try:
                token = request.cookies.get('Ttm-Token')

                token = urllib.parse.unquote(token)


                if token:
                    data = decrypt_web_token(token)

                    if data:
                        uid = data['uid']
                        login_time = data.get('time', 0)
                if datetime.now().timestamp() - login_time >= 86400*91:
                    raise NotLoginError()
            except CookieError:
                raise NotLoginError()

            kwargs['uid'] = uid
            # request['uid'] = uid
            response = await f(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator
