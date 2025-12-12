#!/usr/bin/env python3
import requests
import json
import subprocess
import time

def run_command(cmd):
    """Exécute une commande shell"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def test_elasticsearch():
    print("🔍 Testing Elasticsearch...")
    try:
        # Test connexion
        response = requests.get("http://localhost:9200")
        print(f"   ✅ Status: {response.status_code}")
        
        # Test indices
        response = requests.get("http://localhost:9200/_cat/indices?v")
        print("   📊 Indices:")
        print(response.text)
        
        # Test données
        response = requests.get(
            "http://localhost:9200/tech_docs/_search?size=3",
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        total_docs = data['hits']['total']['value']
        print(f"   📄 Documents dans tech_docs: {total_docs}")
        
        if total_docs > 0:
            for hit in data['hits']['hits']:
                doc = hit['_source']
                title = doc.get('title', 'Sans titre')[:50]
                url = doc.get('url', 'N/A')
                print(f"      • {title}... | {url}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_search_service():
    print("\n🔍 Testing Search Service...")
    try:
        # Test health
        response = requests.get("http://localhost:8002/health")
        print(f"   ✅ Health: {response.status_code}")
        
        # Test recherche
        response = requests.get("http://localhost:8002/search?q=python")
        data = response.json()
        print(f"   🔍 Recherche 'python': {len(data.get('results', []))} résultats")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_frontend():
    print("\n🔍 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_kafka():
    print("\n🔍 Testing Kafka...")
    try:
        # Vérifier si Kafka répond
        stdout, stderr = run_command(
            "docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092"
        )
        if "crawled_documents" in stdout:
            print("   ✅ Topic crawled_documents existe")
        else:
            print("   ⚠️  Topic crawled_documents non trouvé")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def check_services_status():
    print("\n🔍 Checking Services Status...")
    stdout, stderr = run_command("docker-compose ps")
    print(stdout)

def main():
    print("🚀 DIAGNOSTIC COMPLET DU MOTEUR DE RECHERCHE")
    print("=" * 50)
    
    # Vérifier l'état des services Docker
    check_services_status()
    
    # Tests individuels
    tests = [
        test_elasticsearch,
        test_search_service,
        test_frontend,
        test_kafka
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
            time.sleep(1)
        except Exception as e:
            print(f"   💥 Test crashé: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC:")
    print(f"   ✅ Tests passés: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 Tous les tests sont passés !")
        print("\n🔍 Prochaines étapes:")
        print("   1. Améliorer la qualité du contenu crawlé")
        print("   2. Optimiser le mapping Elasticsearch") 
        print("   3. Améliorer l'algorithme de recherche")
    else:
        print("❌ Certains services ont des problèmes")
        print("\n🔧 Actions recommandées:")
        if not results[0]:  # Elasticsearch
            print("   • Vérifier Elasticsearch: curl http://localhost:9200")
        if not results[1]:  # Search service
            print("   • Vérifier Search Service: curl http://localhost:8002/health")
        if not results[2]:  # Frontend
            print("   • Vérifier Frontend: curl http://localhost:3000")

if __name__ == "__main__":
    main()