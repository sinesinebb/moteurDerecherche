from redis import Redis
from redisgraph import Graph
from src.core.config import settings

def load_graph():
    r = Redis(host=settings.redis_host, port=settings.redis_port)
    g = Graph(settings.graph_name, r)
    query = "MATCH (u)-[r]->(v) RETURN u.url AS src, v.url AS dst"
    result = g.query(query)
    graph = {}
    for src, dst in result.result_set:
        graph.setdefault(src, []).append(dst)
    return graph
