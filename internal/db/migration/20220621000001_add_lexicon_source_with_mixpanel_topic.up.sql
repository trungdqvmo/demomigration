INSERT INTO public.sources (id, name, cluster_name, owner)
VALUES
    ('77272535-9320-4fd3-9224-3d68ad50e890', 'lexicon', 'lexicon', '');

INSERT INTO public.topics (id, source_id, name)
VALUES
    ('4cd5ec32-d774-4e8b-b3a4-7729274bd972', '77272535-9320-4fd3-9224-3d68ad50e890', 'mixpanel');