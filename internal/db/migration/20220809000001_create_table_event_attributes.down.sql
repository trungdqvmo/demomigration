ALTER TABLE attributes_count
    DROP CONSTRAINT attributes_count_attribute_id_event_id_date_count_key;

ALTER TABLE attributes_count
    ADD CONSTRAINT attributes_count_attribute_id_date_count_key UNIQUE (attribute_id, date_count);

ALTER TABLE attributes_count
    DROP COLUMN event_id;

ALTER TABLE events
    ALTER COLUMN origin TYPE varchar(255) USING to_jsonb(origin)::json;