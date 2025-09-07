CREATE TABLE agency (
   agency_id VARCHAR(255) NOT NULL PRIMARY KEY,
   agency_name VARCHAR(255) NOT NULL,
   agency_url VARCHAR(255) NOT NULL,
   agency_timezone VARCHAR(255) NOT NULL,
   agency_lang VARCHAR(255),
   agency_phone VARCHAR(255),
   agency_fare_url VARCHAR(255),
   agency_email VARCHAR(255)
);

CREATE TABLE calendar (
   service_id VARCHAR(255) NOT NULL PRIMARY KEY,
   monday BOOLEAN NOT NULL,
   tuesday BOOLEAN NOT NULL,
   wednesday BOOLEAN NOT NULL,
   thursday BOOLEAN NOT NULL,
   friday BOOLEAN NOT NULL,
   saturday BOOLEAN NOT NULL,
   sunday BOOLEAN NOT NULL,
   start_date DATE NOT NULL,
   end_date DATE NOT NULL
);

CREATE TABLE calendar_dates (
   -- Clé primaire composée pour garantir l'unicité des exceptions de service
   service_id VARCHAR(255) NOT NULL,
   date_service DATE NOT NULL,
   exception_type VARCHAR(255) NOT NULL,
   PRIMARY KEY (service_id, date_service),
   FOREIGN KEY (service_id) REFERENCES calendar(service_id)
);

CREATE TABLE feed_info (
   feed_publisher_name VARCHAR(255) NOT NULL PRIMARY KEY,
   feed_publisher_url VARCHAR(255) NOT NULL,
   feed_lang VARCHAR(255) NOT NULL,
   default_lang VARCHAR(255),
   feed_start_date DATE,
   feed_end_date DATE,
   feed_version VARCHAR(255),
   feed_contact_email VARCHAR(255),
   feed_contact_url VARCHAR(255)
);

CREATE TABLE routes (
   route_id VARCHAR(255) NOT NULL PRIMARY KEY,
   agency_id VARCHAR(255),
   route_short_name VARCHAR(255),
   route_long_name VARCHAR(255),
   route_desc VARCHAR(255),
   route_type VARCHAR(255) NOT NULL,
   route_url VARCHAR(255),
   route_color VARCHAR(255),
   route_text_color VARCHAR(255),
   route_sort_order VARCHAR(255),
   continuous_pickup VARCHAR(255),
   continuous_drop_off VARCHAR(255),
   network_id VARCHAR(255),
   FOREIGN KEY (agency_id) REFERENCES agency(agency_id)
);

CREATE TABLE shapes (
   shape_id VARCHAR(255) NOT NULL,
   shape_pt_lat DOUBLE PRECISION NOT NULL,
   shape_pt_lon DOUBLE PRECISION NOT NULL,
   shape_pt_sequence integer NOT NULL,
   shape_dist_traveled DOUBLE PRECISION,
   -- Clé primaire composée pour identifier chaque point unique dans une forme
   PRIMARY KEY (shape_id, shape_pt_sequence)
);

CREATE TABLE stops (
   stop_id VARCHAR(255) NOT NULL PRIMARY KEY,
   stop_code VARCHAR(255),
   stop_name VARCHAR(255),
   tts_stop_name VARCHAR(255),
   stop_desc VARCHAR(255),
   stop_lat DOUBLE PRECISION,
   stop_lon DOUBLE PRECISION,
   zone_id VARCHAR(255),
   stop_url VARCHAR(255),
   location_type integer,
   parent_station VARCHAR(255), -- Recommandation: Ceci pourrait être une FK vers stop_id, mais n'est pas requis
   stop_timezone VARCHAR(255),
   wheelchair_boarding integer,
   level_id VARCHAR(255),
   platform_code VARCHAR(255)
   -- NOTE : Le FOREIGN KEY (route_id) de votre script original a été retiré, car
   -- un arrêt n'est pas directement lié à une route, mais à un trip via stop_times.
);

CREATE TABLE trips (
   -- Le trip_id est la clé primaire car un route_id peut avoir de nombreux trajets
   route_id VARCHAR(255) NOT NULL,
   service_id VARCHAR(255) NOT NULL,
   trip_id VARCHAR(255) NOT NULL PRIMARY KEY,
   trip_headsign VARCHAR(255),
   trip_short_name VARCHAR(255),
   direction_id VARCHAR(255),
   shape_id VARCHAR(255),
   wheelchair_accessible VARCHAR(255),
   bikes_allowed VARCHAR(255),
   cars_allowed VARCHAR(255),
   FOREIGN KEY (route_id) REFERENCES routes(route_id),
   FOREIGN KEY (service_id) REFERENCES calendar(service_id)
);

CREATE TABLE stop_times (
   trip_id VARCHAR(255) NOT NULL,
   -- Recommandation : Les champs de temps devraient être de type TIME
   arrival_time TIME,
   departure_time TIME,
   stop_id VARCHAR(255),
   location_group_id VARCHAR(255),
   location_id VARCHAR(255),
   stop_sequence integer NOT NULL,
   stop_headsign VARCHAR(255),
   start_pickup_drop_off_window VARCHAR(255),
   end_pickup_drop_off_window VARCHAR(255),
   pickup_type VARCHAR(255),
   drop_off_type VARCHAR(255),
   continuous_pickup VARCHAR(255),
   continuous_drop_off VARCHAR(255),
   shape_dist_traveled DOUBLE PRECISION,
   timepoint VARCHAR(255),
   pickup_booking_rule_id VARCHAR(255),
   drop_off_booking_rule_id VARCHAR(255),
   -- Clé primaire composée car un trip peut avoir de nombreux arrêts
   PRIMARY KEY (trip_id, stop_sequence),
   FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
   FOREIGN KEY (stop_id) REFERENCES stops(stop_id)
);