urlpatterns = [
    # ...
    path('metrics/query/', prometheus_query, name='prometheus-query'),
]