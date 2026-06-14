import time, httpx
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt, ExpiredSignatureError, JWTError
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

resource = Resource.create({"service.name": "service-a"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318/v1/traces")
))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("iam.auth")

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
bearer = HTTPBearer()

JWKS_URL = "http://keycloak.keycloak.svc.cluster.local/realms/iam-observability-lab/protocol/openid-connect/certs"
_jwks = None

def get_jwks():
    global _jwks
    if not _jwks:
        _jwks = httpx.get(JWKS_URL).json()
    return _jwks

async def verify_token(token=Security(bearer)):
    with tracer.start_as_current_span("iam.token.validation") as span:
        start = time.time()
        try:
            payload = jwt.decode(token.credentials, get_jwks(), algorithms=["RS256"], options={"verify_aud": False})
            span.set_attribute("token.valid", True)
            span.set_attribute("token.validation_latency_ms", round((time.time()-start)*1000, 2))
            span.set_attribute("token.failure_reason", "NONE")
            span.set_attribute("auth.protocol", "OIDC")
            return payload
        except ExpiredSignatureError:
            span.set_attribute("token.valid", False)
            span.set_attribute("token.failure_reason", "EXPIRED")
            raise HTTPException(401, "Token expired")
        except JWTError:
            span.set_attribute("token.valid", False)
            span.set_attribute("token.failure_reason", "INVALID_SIGNATURE")
            raise HTTPException(401, "Invalid token")

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/protected")
async def protected(claims=Depends(verify_token)):
    return {"status": "ok", "client": claims.get("clientId")}
