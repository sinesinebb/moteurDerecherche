# app/utils/helpers.py
import asyncio
import time
from typing import Any, Callable, Dict, List, Optional
from functools import wraps
from contextlib import asynccontextmanager
import hashlib
import json
from datetime import datetime, timedelta

def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Décorateur pour réessayer les fonctions asynchrones avec backoff exponentiel.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        return wrapper
    return decorator

@asynccontextmanager
async def async_timeout(seconds: float):
    """
    Context manager pour timeout asynchrone.
    """
    try:
        await asyncio.wait_for(asyncio.sleep(0), timeout=seconds)
        yield
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Génère une clé de cache unique basée sur les arguments.
    """
    key_data = {
        'args': args,
        'kwargs': {k: v for k, v in kwargs.items() if not k.startswith('_')}
    }
    key_string = json.dumps(key_data, sort_keys=True)
    hash_object = hashlib.md5(key_string.encode())
    return f"{prefix}:{hash_object.hexdigest()}"

def format_bytes(size: int) -> str:
    """
    Formate une taille en bytes en unités lisibles.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def format_duration(seconds: float) -> str:
    """
    Formate une durée en secondes en unités lisibles.
    """
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes)} min {seconds:.1f} s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)} h {int(minutes)} min"

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Divise une liste en chunks de taille spécifiée.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get(dictionary: Dict, keys: List[str], default: Any = None) -> Any:
    """
    Récupère une valeur nested d'un dictionnaire de manière sécurisée.
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Fusionne deux dictionnaires récursivement.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if (key in result and isinstance(result[key], dict) 
            and isinstance(value, dict)):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

class RateLimiter:
    """
    Limiteur de taux pour contrôler les appels API.
    """
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps: List[float] = []
    
    async def acquire(self):
        """Attend jusqu'à ce qu'un appel soit autorisé."""
        now = time.time()
        
        # Supprimer les timestamps expirés
        self.timestamps = [ts for ts in self.timestamps 
                          if now - ts < self.period]
        
        if len(self.timestamps) >= self.calls:
            # Calculer le temps à attendre
            oldest = self.timestamps[0]
            wait_time = self.period - (now - oldest)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                now = time.time()
        
        self.timestamps.append(now)
        
        # Garder seulement les timestamps récents
        self.timestamps = [ts for ts in self.timestamps 
                          if now - ts < self.period]

class PerformanceTimer:
    """
    Timer pour mesurer les performances.
    """
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Retourne le temps écoulé en secondes."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

def validate_email(email: str) -> bool:
    """
    Valide le format d'un email.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text: str) -> str:
    """
    Nettoie les entrées utilisateur pour prévenir les injections.
    """
    if not text:
        return ""
    
    # Supprimer les caractères dangereux
    dangerous_chars = ['<', '>', 'script', 'javascript', 'onload']
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def parse_date_range(date_string: str) -> tuple:
    """
    Parse une chaîne de période en dates de début et fin.
    """
    now = datetime.now()
    
    if date_string == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif date_string == "week":
        start = now - timedelta(days=7)
        end = now
    elif date_string == "month":
        start = now - timedelta(days=30)
        end = now
    elif date_string == "year":
        start = now - timedelta(days=365)
        end = now
    else:
        # Essayer de parser comme date spécifique
        try:
            start = datetime.fromisoformat(date_string)
            end = now
        except ValueError:
            start = now - timedelta(days=30)
            end = now
    
    return start, end