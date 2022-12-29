ALTER TABLE attributes
    DROP CONSTRAINT attributes_reference_name_topic_id_key;

ALTER TABLE attributes
    ADD CONSTRAINT attributes_name_topic_id_key UNIQUE (name, topic_id);

ALTER TABLE attributes
    DROP COLUMN reference_name;

ALTER TABLE attributes
    DROP COLUMN property_type;
