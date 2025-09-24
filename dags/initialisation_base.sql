CREATE TABLE compagnie (
   id_compagnie INTEGER NOT NULL PRIMARY KEY,
   libelle_compagnie VARCHAR(150) NOT NULL,
   url_donnees_statiques VARCHAR(255) NOT NULL,
   url_rt VARCHAR(255)
);

CREATE TABLE agency (
   id_compagnie INTEGER NOT NULL,
   agency_id VARCHAR(255) NOT NULL,
   agency_name VARCHAR(255) NOT NULL,
   agency_url VARCHAR(255) NOT NULL,
   agency_timezone VARCHAR(255) NOT NULL,
   agency_lang VARCHAR(255),
   agency_phone VARCHAR(255),
   agency_fare_url VARCHAR(255),
   agency_email VARCHAR(255),
   PRIMARY KEY (id_compagnie, agency_id),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie)
);

CREATE TABLE calendar (
   id_compagnie INTEGER NOT NULL,
   service_id VARCHAR(255) NOT NULL,
   monday BOOLEAN NOT NULL,
   tuesday BOOLEAN NOT NULL,
   wednesday BOOLEAN NOT NULL,
   thursday BOOLEAN NOT NULL,
   friday BOOLEAN NOT NULL,
   saturday BOOLEAN NOT NULL,
   sunday BOOLEAN NOT NULL,
   start_date DATE NOT NULL,
   end_date DATE NOT NULL,
   PRIMARY KEY (id_compagnie, service_id),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie)
);

CREATE TABLE calendar_dates (
   -- Clé primaire composée pour garantir l'unicité des exceptions de service
   id_compagnie INTEGER NOT NULL,
   service_id VARCHAR(255) NOT NULL,
   date_service DATE NOT NULL,
   exception_type VARCHAR(255) NOT NULL,
   PRIMARY KEY (id_compagnie, service_id, date_service),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie)
   -- un service peut être ajouté explicitement sur une journée uniquement
   -- donc pas de lien obligatoire entre calendar et calendar_date
   --FOREIGN KEY (id_compagnie, service_id) REFERENCES calendar(id_compagnie, service_id)
);

CREATE TABLE feed_info (
   id_compagnie INTEGER NOT NULL,
   feed_publisher_name VARCHAR(255) NOT NULL,
   feed_publisher_url VARCHAR(255) NOT NULL,
   feed_lang VARCHAR(255) NOT NULL,
   default_lang VARCHAR(255),
   feed_start_date DATE,
   feed_end_date DATE,
   feed_version VARCHAR(255),
   feed_contact_email VARCHAR(255),
   feed_contact_url VARCHAR(255),
   PRIMARY KEY (id_compagnie, feed_publisher_name),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie)
);

CREATE TABLE routes (
   id_compagnie INTEGER NOT NULL,
   route_id VARCHAR(255) NOT NULL,
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
   PRIMARY KEY (id_compagnie, route_id),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie),
   FOREIGN KEY (id_compagnie, agency_id) REFERENCES agency(id_compagnie, agency_id)
);

CREATE TABLE shapes (
   id_compagnie INTEGER NOT NULL,
   shape_id VARCHAR(255) NOT NULL,
   shape_pt_lat DOUBLE PRECISION NOT NULL,
   shape_pt_lon DOUBLE PRECISION NOT NULL,
   shape_pt_sequence integer NOT NULL,
   shape_dist_traveled DOUBLE PRECISION,
   -- Clé primaire composée pour identifier chaque point unique dans une forme
   PRIMARY KEY (id_compagnie, shape_id, shape_pt_sequence),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie)
);

CREATE TABLE stops (
   id_compagnie INTEGER NOT NULL,
   stop_id VARCHAR(255) NOT NULL,
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
   platform_code VARCHAR(255),
   PRIMARY KEY (id_compagnie, stop_id),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie)
);

CREATE TABLE trips (
   -- Le trip_id est la clé primaire car un route_id peut avoir de nombreux trajets
   id_compagnie INTEGER NOT NULL,
   route_id VARCHAR(255) NOT NULL,
   service_id VARCHAR(255) NOT NULL,
   trip_id VARCHAR(255) NOT NULL,
   trip_headsign VARCHAR(255),
   trip_short_name VARCHAR(255),
   direction_id VARCHAR(255),
   block_id VARCHAR(255),
   shape_id VARCHAR(255),
   wheelchair_accessible VARCHAR(255),
   bikes_allowed VARCHAR(255),
   cars_allowed VARCHAR(255),
   PRIMARY KEY (id_compagnie, trip_id),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie),
   FOREIGN KEY (id_compagnie, route_id) REFERENCES routes(id_compagnie, route_id)
   -- un service n'est pas forcément renseigné dans le calendrier
   -- FOREIGN KEY (id_compagnie, service_id) REFERENCES calendar(id_compagnie, service_id)
);

CREATE TABLE stop_times (
   id_compagnie INTEGER NOT NULL,
   trip_id VARCHAR(255) NOT NULL,
   -- Recommandation : Les champs de temps devraient être de type TIME
   arrival_time INTERVAL,
   departure_time INTERVAL,
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
   PRIMARY KEY (id_compagnie, trip_id, stop_sequence),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie),
   FOREIGN KEY (id_compagnie, trip_id) REFERENCES trips(id_compagnie, trip_id),
   FOREIGN KEY (id_compagnie, stop_id) REFERENCES stops(id_compagnie, stop_id)
);

CREATE TABLE rt_trip_update (
   id_compagnie INTEGER NOT NULL,
   trip_id VARCHAR(255) NOT NULL,
   route_id VARCHAR(255) NOT NULL,
   stop_id VARCHAR(255),
   arrival TIMESTAMP, -- enregistré dans la TZ UTC
   PRIMARY KEY (id_compagnie, trip_id, route_id, stop_id),
   FOREIGN KEY (id_compagnie) REFERENCES compagnie(id_compagnie),
   FOREIGN KEY (id_compagnie, trip_id) REFERENCES trips(id_compagnie, trip_id),
   FOREIGN KEY (id_compagnie, stop_id) REFERENCES stops(id_compagnie, stop_id),
   FOREIGN KEY (id_compagnie, route_id) REFERENCES routes(id_compagnie, route_id)
);