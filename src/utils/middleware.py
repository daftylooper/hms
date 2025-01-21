from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
import threading

class AuditLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        request.client_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
        # Get user from JWT
        try:
            jwt_auth = JWTAuthentication()
            header = jwt_auth.get_header(request)
            if header:
                raw_token = jwt_auth.get_raw_token(header)
                if raw_token:
                    validated_token = jwt_auth.get_validated_token(raw_token)
                    request.jwt_user = jwt_auth.get_user(validated_token)
        except Exception:
            request.jwt_user = None

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Store request in thread local storage
        threading.current_thread()._current_request = request
        response = self.get_response(request)
        # Clean up
        delattr(threading.current_thread(), '_current_request')
        return response