#!/usr/bin/env python3
import requests
import json
import time

class SearchEvaluator:
    def __init__(self, search_url, nlp_url):
        self.search_url = search_url
        self.nlp_url = nlp_url
        
    def test_queries(self):
        test_cases = [
            {
                "query": "apprendre Python programmation",
                "expected_terms": ["python", "tutoriel", "débutant", "code"]
            },
            {
                "query": "base données SQL", 
                "expected_terms": ["mysql", "postgresql", "requête", "table"]
            },
            {
                "query": "machine learning",
                "expected_terms": ["ai", "intelligence", "algorithm", "données"]
            }
        ]
        
        results = []
        for test in test_cases:
            result = self.evaluate_query(test)
            results.append(result)
            
        return results
    
    def evaluate_query(self, test_case):
        # Test sans NLP
        response_basic = requests.post(
            f"{self.search_url}/search",
            json={"query": test_case["query"], "use_nlp": False, "size": 10}
        )
        
        # Test avec NLP
        response_nlp = requests.post(
            f"{self.search_url}/search", 
            json={"query": test_case["query"], "use_nlp": True, "size": 10}
        )
        
        basic_results = response_basic.json().get("results", [])
        nlp_results = response_nlp.json().get("results", [])
        
        # Calcul des métriques
        basic_score = self.calculate_relevance(basic_results, test_case["expected_terms"])
        nlp_score = self.calculate_relevance(nlp_results, test_case["expected_terms"])
        
        return {
            "query": test_case["query"],
            "basic_search": {
                "score": basic_score,
                "top_results": [r["title"] for r in basic_results[:3]]
            },
            "nlp_search": {
                "score": nlp_score,
                "top_results": [r["title"] for r in nlp_results[:3]]
            },
            "improvement": nlp_score - basic_score
        }
    
    def calculate_relevance(self, results, expected_terms):
        if not results:
            return 0
            
        total_score = 0
        for result in results[:5]:  # On regarde les 5 premiers résultats
            content = f"{result.get('title', '')} {result.get('content', '')}".lower()
            score = sum(1 for term in expected_terms if term in content)
            total_score += score
            
        return total_score / len(results[:5])

if __name__ == "__main__":
    evaluator = SearchEvaluator("http://localhost:8002", "http://localhost:8003")
    results = evaluator.test_queries()
    
    print("=== RÉSULTATS DE L'ÉVALUATION ===")
    for result in results:
        print(f"\nRequête: {result['query']}")
        print(f"Score sans NLP: {result['basic_search']['score']:.2f}")
        print(f"Score avec NLP: {result['nlp_search']['score']:.2f}")
        print(f"Amélioration: {result['improvement']:+.2f}")
        print(f"Top résultats NLP: {result['nlp_search']['top_results']}")