# models.py
class SearchQueryLog(models.Model):
    query_text = models.CharField(max_length=500)
    user_session = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField()
    results_count = models.IntegerField()
    zero_results = models.BooleanField(default=False)
    
class QueryTrends(models.Model):
    query_pattern = models.CharField(max_length=500)
    frequency = models.IntegerField()
    period = models.CharField(max_length=20)
    trend_direction = models.CharField(max_length=10, choices=[('up', 'Up'), ('down', 'Down'), ('stable', 'Stable')])
    
class RankingPerformance(models.Model):
    algorithm_version = models.CharField(max_length=50)
    query = models.CharField(max_length=500)
    expected_rank = models.IntegerField()
    actual_rank = models.IntegerField()
    user_feedback = models.IntegerField(null=True, blank=True)  # 1-5 rating