
from __future__ import annotations
from contextlib import contextmanager

try:
    from opentelemetry import trace  # type: ignore
    tracer = trace.get_tracer("nexusnet")
except Exception:  # SDK absent
    tracer = None

@contextmanager
def start_span(name: str, **attrs):
    if tracer is None:
        yield None
        return
    with tracer.start_as_current_span(name) as span:  # type: ignore
        try:
            for k,v in attrs.items():
                try:
                    span.set_attribute(k, v)  # type: ignore
                except Exception:
                    pass
            yield span
        except Exception:
            raise
