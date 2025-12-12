# app/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
from typing import Dict, Any, Optional, Callable
import time
import asyncio
from functools import wraps
from contextlib import contextmanager
import logging
from opentelemetry import trace
from opentelemetry.metrics import Meter

logger = logging.getLogger(__name__)

# Métriques de base
SEARCH_REQUESTS = Counter(
    'search_requests_total',
    'Total des requêtes de recherche',
    ['method', 'endpoint', 'status', 'domain', 'user_type']
)

SEARCH_DURATION = Histogram(
    'search_duration_seconds',
    'Durée des requêtes de recherche',
    ['method', 'endpoint', 'domain'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

SEARCH_CACHE = Counter(
    'search_cache_operations_total',
    'Opérations de cache',
    ['operation', 'status']
)

DOMAIN_VALIDATION = Counter(
    'domain_validation_total',
    'Validations de domaine',
    ['result', 'category']
)

# Métriques système
ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Requêtes actives en cours'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Utilisation mémoire de l\'application'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Utilisation CPU de l\'application'
)

# Métriques de performance détaillées
ELASTICSEARCH_LATENCY = Histogram(
    'elasticsearch_latency_seconds',
    'Latence des appels Elasticsearch',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

REDIS_LATENCY = Histogram(
    'redis_latency_seconds',
    'Latence des opérations Redis',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
)

EXTERNAL_SERVICE_LATENCY = Histogram(
    'external_service_latency_seconds',
    'Latence des appels aux services externes',
    ['service', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Métriques business
SEARCH_RESULT_QUALITY = Gauge(
    'search_result_quality',
    'Qualité des résultats de recherche',
    ['query_complexity']
)

USER_ENGAGEMENT = Counter(
    'user_engagement_events_total',
    'Événements d\'engagement utilisateur',
    ['event_type', 'user_segment']
)

# Info sur la version
APPLICATION_INFO = Info(
    'application_info',
    'Information sur l\'application'
)

class AdvancedMetrics:
    """Classe avancée pour la gestion des métriques"""
    
    def __init__(self):
        self.meter: Optional[Meter] = None
        self.tracer = trace.get_tracer(__name__)
        self._setup_application_info()
    
    def _setup_application_info(self):
        """Configure les informations de l'application"""
        APPLICATION_INFO.info({
            'version': '1.0.0',
            'name': 'search-service',
            'environment': 'production'
        })
    
    @contextmanager
    def track_request(self, method: str, endpoint: str, domain: str = "unknown", user_type: str = "anonymous"):
        """Context manager pour tracker les requêtes"""
        start_time = time.time()
        ACTIVE_REQUESTS.inc()
        
        try:
            yield
            status = "success"
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            ACTIVE_REQUESTS.dec()
            
            SEARCH_REQUESTS.labels(
                method=method,
                endpoint=endpoint,
                status=status,
                domain=domain,
                user_type=user_type
            ).inc()
            
            SEARCH_DURATION.labels(
                method=method,
                endpoint=endpoint,
                domain=domain
            ).observe(duration)
    
    @contextmanager
    def track_elasticsearch_operation(self, operation: str):
        """Context manager pour tracker les opérations Elasticsearch"""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            ELASTICSEARCH_LATENCY.labels(operation=operation).observe(duration)
    
    @contextmanager
    def track_redis_operation(self, operation: str):
        """Context manager pour tracker les opérations Redis"""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            REDIS_LATENCY.labels(operation=operation).observe(duration)
    
    @contextmanager
    def track_external_service_call(self, service: str, endpoint: str):
        """Context manager pour tracker les appels aux services externes"""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            EXTERNAL_SERVICE_LATENCY.labels(
                service=service,
                endpoint=endpoint
            ).observe(duration)
    
    def record_search_metric(self, metric_type: str, query: str, user_id: str = None, extra: Dict[str, Any] = None):
        """Enregistre une métrique de recherche avancée"""
        user_type = "authenticated" if user_id else "anonymous"
        extra = extra or {}
        
        if metric_type == "search_success":
            SEARCH_REQUESTS.labels(
                method="POST",
                endpoint="/api/v1/search",
                status="success",
                domain=extra.get('domain_category', 'unknown'),
                user_type=user_type
            ).inc()
            
            # Enregistrer la qualité des résultats si disponible
            if 'result_quality' in extra:
                SEARCH_RESULT_QUALITY.labels(
                    query_complexity=extra.get('query_complexity', 'medium')
                ).set(extra['result_quality'])
        
        elif metric_type == "search_failure":
            SEARCH_REQUESTS.labels(
                method="POST", 
                endpoint="/api/v1/search",
                status="failure",
                domain=extra.get('domain_category', 'unknown'),
                user_type=user_type
            ).inc()
        
        elif metric_type == "cache_hit":
            SEARCH_CACHE.labels(operation="get", status="hit").inc()
        
        elif metric_type == "cache_miss":
            SEARCH_CACHE.labels(operation="get", status="miss").inc()
        
        elif metric_type == "cache_set":
            SEARCH_CACHE.labels(operation="set", status="success").inc()
        
        elif metric_type == "domain_validation":
            result = "valid" if extra.get('is_valid') else "invalid"
            DOMAIN_VALIDATION.labels(
                result=result,
                category=extra.get('category', 'unknown')
            ).inc()
        
        elif metric_type == "user_engagement":
            USER_ENGAGEMENT.labels(
                event_type=extra.get('event_type', 'unknown'),
                user_segment=user_type
            ).inc()
    
    def record_performance_metric(self, component: str, operation: str, duration: float, success: bool = True):
        """Enregistre une métrique de performance générique"""
        # Utiliser le tracer OpenTelemetry si disponible
        with self.tracer.start_as_current_span(f"{component}.{operation}") as span:
            span.set_attribute("component", component)
            span.set_attribute("operation", operation)
            span.set_attribute("duration", duration)
            span.set_attribute("success", success)
            
            # Enregistrer aussi dans Prometheus
            if component == "elasticsearch":
                ELASTICSEARCH_LATENCY.labels(operation=operation).observe(duration)
            elif component == "redis":
                REDIS_LATENCY.labels(operation=operation).observe(duration)
    
    def update_system_metrics(self):
        """Met à jour les métriques système (à appeler périodiquement)"""
        try:
            import psutil
            process = psutil.Process()
            
            # Mémoire
            memory_info = process.memory_info()
            MEMORY_USAGE.set(memory_info.rss)
            
            # CPU
            cpu_percent = process.cpu_percent()
            CPU_USAGE.set(cpu_percent)
            
        except ImportError:
            logger.warning("psutil not available, system metrics disabled")
    
    def instrument_function(self, metric_name: str, labels: Dict[str, str] = None):
        """
        Décorateur pour instrumenter une fonction avec des métriques
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    success = False
                    raise
                finally:
                    duration = time.time() - start_time
                    self.record_performance_metric(
                        component=metric_name,
                        operation=func.__name__,
                        duration=duration,
                        success=success
                    )
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    success = False
                    raise
                finally:
                    duration = time.time() - start_time
                    self.record_performance_metric(
                        component=metric_name,
                        operation=func.__name__,
                        duration=duration,
                        success=success
                    )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

# Instance globale
metrics = AdvancedMetrics()

# Fonctions utilitaires
def record_search_time(domain: str = "unknown"):
    """Décorateur pour mesurer le temps de recherche"""
    return SEARCH_DURATION.labels(
        method="POST",
        endpoint="/api/v1/search",
        domain=domain
    ).time()

async def measure_elasticsearch_latency(func, *args, **kwargs):
    """Mesure la latence des appels Elasticsearch"""
    operation = func.__name__
    with metrics.track_elasticsearch_operation(operation):
        return await func(*args, **kwargs)

def start_search():
    """Démarre le compteur de recherches actives"""
    ACTIVE_REQUESTS.inc()

def end_search():
    """Termine le compteur de recherches actives"""
    ACTIVE_REQUESTS.dec()

def setup_metrics(app):
    """Configure les métriques pour l'application FastAPI"""
    from prometheus_client import make_asgi_app
    
    # Ajouter l'endpoint métriques
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Mettre à jour périodiquement les métriques système
    async def update_system_metrics_periodically():
        while True:
            metrics.update_system_metrics()
            await asyncio.sleep(30)  # Toutes les 30 secondes
    
    # Démarrer la tâche background
    @app.on_event("startup")
    async def start_metrics_task():
        asyncio.create_task(update_system_metrics_periodically())