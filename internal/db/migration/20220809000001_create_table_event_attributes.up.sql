ALTER TABLE events
    ALTER COLUMN origin TYPE json USING to_jsonb(origin)::json;

ALTER TABLE attributes_count
    ADD COLUMN event_id uuid NOT NULL CONSTRAINT attributes_count_events_id__fk REFERENCES events (id);

ALTER TABLE attributes_count
    DROP CONSTRAINT attributes_count_attribute_id_date_count_key;

ALTER TABLE attributes_count
    ADD CONSTRAINT attributes_count_attribute_id_event_id_date_count_key UNIQUE (attribute_id, event_id, date_count);