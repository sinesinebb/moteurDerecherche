# src/services/pagerank_service.py
import logging
from typing import Dict, List, Tuple
import numpy as np
from scipy.sparse import csr_matrix
from fast_pagerank import pagerank
from src.core.config import settings

logger = logging.getLogger(__name__)

def _dict_to_sparse(graph: Dict[str, List[str]]) -> Tuple[csr_matrix, List[str]]:
    """
    Convertit graph: {node: [neigh1, neigh2, ...]} en matrice creuse CSR.
    Retourne (A, index_to_node) où A[i,j] = 1 si node_i -> node_j.
    """
    # Construire mapping node -> idx
    nodes = set(graph.keys())
    for dests in graph.values():
        nodes.update(dests)
    index_to_node = list(nodes)
    node_to_index = {n: i for i, n in enumerate(index_to_node)}
    n = len(index_to_node)
    rows, cols, data = [], [], []

    for src, dests in graph.items():
        i = node_to_index[src]
        if not dests:
            continue
        for dst in dests:
            j = node_to_index.get(dst)
            if j is None:
                # si dst inattendu (défensive) — l'ignorer
                continue
            rows.append(i)
            cols.append(j)
            data.append(1.0)

    if len(data) == 0:
        # graphe vide -> matrice 0x0
        A = csr_matrix((n, n), dtype=float)
    else:
        A = csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)

    return A, index_to_node

def compute(graph: Dict[str, List[str]],
            d: float = None,
            tol: float = None,
            max_iter: int = None) -> Dict[str, float]:
    """
    Calcule PageRank à partir d'un dict adjacency list.
    Retourne dict { url: score }.
    """
    # utiliser paramètres depuis settings si non fournis
    if d is None:
        d = settings.page_rank_d
    # tol et max_iter ne sont pas utilisés directement par fast_pagerank signature
    # on expose d (p) et on laisse pagerank gérer la convergence interne.

    logger.info("Conversion du graphe en matrice creuse...")
    A, index_to_node = _dict_to_sparse(graph)
    logger.info("Matrice construite : %s x %s, nnz=%s", A.shape[0], A.shape[1], A.nnz)

    # fast_pagerank signature: pagerank(A, p=0.85, personalize=None, reverse=False)
    logger.info("Appel de fast_pagerank.pagerank avec p=%s", d)
    scores_array = pagerank(A, p=d)

    # scores_array est un vecteur numpy aligné avec index_to_node
    if len(scores_array) != len(index_to_node):
        logger.warning("Taille scores != nombre de noeuds (%d != %d)",
                       len(scores_array), len(index_to_node))

    # Construire dict url -> score
    scores = {index_to_node[i]: float(scores_array[i]) for i in range(len(index_to_node))}
    return scores
