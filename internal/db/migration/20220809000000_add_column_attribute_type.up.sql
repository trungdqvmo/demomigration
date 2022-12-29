ALTER TABLE attributes
    ADD COLUMN property_type varchar(50);

ALTER TABLE attributes
    ADD COLUMN reference_name varchar(255);

ALTER TABLE attributes
    DROP CONSTRAINT attributes_name_topic_id_key;

ALTER TABLE attributes
    ADD CONSTRAINT attributes_reference_name_topic_id_key UNIQUE (reference_name, topic_id);