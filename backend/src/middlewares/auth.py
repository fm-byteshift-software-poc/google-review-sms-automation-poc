from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, expected_key: str):
        super().__init__(app)
        self.expected_key = expected_key.strip()
        self.ALLOWED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):       
        if request.method == "OPTIONS" or \
           request.url.path in self.ALLOWED_PATHS or \
           request.url.path.startswith("/docs/") or \
           request.url.path.startswith("/redoc/"):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "API key required."}
            )

        clean_key = api_key.strip()
        if len(clean_key) != 12:
            return JSONResponse(
                status_code=400,
                content={"error": "Bad Request", "message": "API key must be exactly 12 characters."}
            )

        if clean_key != self.expected_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid API key."}
            )

        return await call_next(request)
    
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import JSONResponse

# class APIKeyMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, expected_key: str):
#         super().__init__(app)
#         self.expected_key = expected_key.strip()
#         self.ALLOWED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
#         # Log na inicialização do middleware
#         print(f"🔐 MIDDLEWARE INIT: Expected key loaded = '{self.expected_key}'")

#     async def dispatch(self, request: Request, call_next):
#         path = request.url.path
        
#         # 1. Bypass docs/health
#         if path in self.ALLOWED_PATHS or path.startswith("/docs/") or path.startswith("/redoc/"):
#             return await call_next(request)

#         # 2. Captura raw do header
#         raw_header = request.headers.get("X-API-Key")
#         print(f"📥 REQUEST RECEIVED: Path='{path}' | Raw Header='[{raw_header}]'")

#         if not raw_header:
#             return JSONResponse(status_code=401, content={"error": "Unauthorized", "message": "API key required."})

#         clean_key = raw_header.strip()
#         print(f"🧹 CLEANED KEY    : '{clean_key}' | Length={len(clean_key)}")
#         print(f" COMPARING     : '{clean_key}' == '{self.expected_key}'")

#         if len(clean_key) != 12:
#             return JSONResponse(status_code=400, content={"error": "Bad Request", "message": "API key must be exactly 12 characters."})

#         if clean_key != self.expected_key:
#             print("❌ AUTH FAILED: Keys do not match.")
#             return JSONResponse(status_code=401, content={"error": "Unauthorized", "message": "Invalid API key."})

#         print("✅ AUTH PASSED: Forwarding request.")
#         return await call_next(request)