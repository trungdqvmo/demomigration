create table sources
(
    id           uuid          not null
        constraint sources_pk
            primary key,
    name         varchar(255)                           not null,
    description  varchar(500),
    cluster_name varchar(255) not null,
    owner        varchar(50) not null,
    created_at   timestamp    default now()             not null,
    updated_at   timestamp    default now()             not null
);

--alter table sources
--    owner to postgres;

create unique index source_id_uindex
    on sources (id);

create table topics
(
    id          uuid       not null
        constraint topics_pk
            primary key,
    source_id   uuid                                not null
        constraint topics_source_id__fk
            references sources (id),
    name        varchar(255)                        not null,
    description varchar(500),
    created_at  timestamp default now()             not null,
    updated_at  timestamp default now()             not null,
    tag         json,
    owner       json,
    UNIQUE (name, source_id)
);

--alter table topics
--    owner to postgres;

create unique index topic_id_uindex
    on topics (id);

create table events
(
    id                       uuid      not null
        constraint events_pk
            primary key,
    name                     varchar(255)                        not null,
    topic_id                 uuid                                not null
        constraint events_topic_id__fk
            references topics,
    description              varchar(500),
    display_name             varchar(255),
    event_struct             json                                not null,
    event_struct_description varchar(500),
    created_at               timestamp default now()             not null,
    updated_at               timestamp default now()             not null,
    event_type               varchar(50),
    origin                   varchar(50),
    destination              json,
    UNIQUE (name, topic_id)
);

--alter table events
--    owner to postgres;

create unique index event_id_uindex
    on events (id);

create table attributes
(
    id         uuid   not null
        constraint attributes_pk
            primary key,
    name       varchar(255)                        not null,
    topic_id   uuid                                not null
        constraint attributes_topic_id__fk
            references topics,
    created_at timestamp default now()             not null,
    updated_at timestamp default now()             not null,
    UNIQUE (name, topic_id)
);

--alter table attributes
--    owner to postgres;

create unique index attributes_id_uindex
    on attributes (id);

create table events_count
(
    id          uuid      not null
        constraint events_count_pk primary key,
    event_id    uuid                                not null
        constraint events_count_event_id___fk
            references events,
    date_count  date      default now(),
    event_count integer   default 0                 not null,
    created_at  timestamp default now()             not null,
    updated_at  timestamp default now()             not null,
    UNIQUE (event_id, date_count)
);

--alter table events_count
--    owner to postgres;

create unique index events_count_id_uindex
    on events_count (id);

create table attributes_count
(
    id              uuid  not null
        constraint attributes_count_pk
            primary key,
    attribute_id    uuid                                not null
        constraint attributes_count_attribute_id__fk
            references attributes,
    date_count      date      default now()             not null,
    attribute_count integer   default 0                 not null,
    created_at      timestamp default now()             not null,
    updated_at      timestamp default now()             not null,
    UNIQUE (attribute_id, date_count)
);

--alter table attributes_count
--    owner to postgres;

create unique index attributes_count_id_uindex
    on attributes_count (id);

create function sync_updated_at() returns trigger
    language plpgsql
as
$$
BEGIN
    NEW.updated_at
:= NOW();
RETURN NEW;
END;
$$;

--alter function sync_updated_at() owner to postgres;

create trigger updated_at_sources
    before update
    on sources
    for each row
    execute procedure sync_updated_at();

create trigger updated_topics
    before update
    on topics
    for each row
    execute procedure sync_updated_at();

create trigger updated_at_events
    before update
    on events
    for each row
    execute procedure sync_updated_at();

create trigger updated_at_attributes
    before update
    on attributes
    for each row
    execute procedure sync_updated_at();

create trigger updated_at_event_count
    before update
    on events_count
    for each row
    execute procedure sync_updated_at();

create trigger updated_at_attributes_count
    before update
    on attributes_count
    for each row
    execute procedure sync_updated_at();
