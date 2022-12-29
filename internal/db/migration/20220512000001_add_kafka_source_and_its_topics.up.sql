INSERT INTO public.sources (id, name, cluster_name, owner)
VALUES
    ('5b7ef038-be20-45b2-acc0-08fef0e9b19d', 'kafka', '', '');

INSERT INTO public.topics (id, source_id, name)
VALUES
    ('bff9819a-6e18-40d3-9bd4-923d93c7c4e7', '5b7ef038-be20-45b2-acc0-08fef0e9b19d', 'user-attributes-analytics'),
    ('36bf91e9-f983-4a64-8b5a-f318c10fe8b4', '5b7ef038-be20-45b2-acc0-08fef0e9b19d', 'user-events-analytics');