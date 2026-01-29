
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from jose import jwt, JWTError
from app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        
        # Define protected paths (mostly HTML pages)
        protected_paths = ["/", "/salaries", "/historique", "/parametres"]
        # Define excluded paths
        excluded_paths = ["/login", "/api/auth/login", "/static", "/files"]

        # Check if the path should be protected
        is_protected = any(path == p for p in protected_paths)
        is_excluded = any(path.startswith(p) for p in excluded_paths)

        if is_protected and not is_excluded:
            token = request.cookies.get(settings.COOKIE_NAME)
            
            if not token:
                return RedirectResponse(url="/login")
            
            try:
                # Basic validation of the token (existence and expiration)
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                username: str = payload.get("sub")
                if username is None:
                    return RedirectResponse(url="/login")
            except JWTError:
                response = RedirectResponse(url="/login")
                response.delete_cookie(settings.COOKIE_NAME)
                return response

        response = await call_next(request)
        return response
