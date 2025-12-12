INSERT INTO django_migrations (app, name, applied) 
VALUES ('core', '0001_initial', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
