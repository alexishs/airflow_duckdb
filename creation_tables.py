def creer_sql(nom_table: str, chaine: str) -> str:
    liste_champs = chaine.split(",")
    chaine_pk = " primary key"
    chaine_virgule = ""
    sql = f"create table {nom_table} (\n"
    for champ in liste_champs:
        sql += chaine_virgule
        sql += f"   {champ} varchar not null{chaine_pk}"
        chaine_pk = ""
        chaine_virgule = ",\n"
    sql += "\n)\n"
    return sql


chemin_fichier_sql = "initialisation_base.sql"

with open(chemin_fichier_sql, "w", encoding="utf-8") as fichier:
    fichier.write(
        creer_sql(
            "agency",
            "agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone,agency_fare_url,agency_email",
        )
    )
    fichier.write(creer_sql("calendar_dates", "service_id,date,exception_type"))
    fichier.write(
        creer_sql(
            "calendar",
            "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date",
        )
    )
    fichier.write(
        creer_sql(
            "feed_info",
            "feed_publisher_name,feed_publisher_url,feed_lang,default_lang,feed_start_date,feed_end_date,feed_version,feed_contact_email,feed_contact_url",
        )
    )
    fichier.write(
        creer_sql(
            "routes",
            "route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color,route_sort_order,continuous_pickup,continuous_drop_off,network_id",
        )
    )
    fichier.write(
        creer_sql(
            "shapes",
            "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence,shape_dist_traveled",
        )
    )
    fichier.write(
        creer_sql(
            "stop_times",
            "trip_id,arrival_time,departure_time,stop_id,location_group_id,location_id,stop_sequence,stop_headsign,start_pickup_drop_off_window,end_pickup_drop_off_window,pickup_type,drop_off_type,continuous_pickup,continuous_drop_off,shape_dist_traveled,timepoint,pickup_booking_rule_id,drop_off_booking_rule_id",
        )
    )
    fichier.write(
        creer_sql(
            "stops",
            "stop_id,stop_code,stop_name,tts_stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url,location_type,parent_station,stop_timezone,wheelchair_boarding,level_id,platform_code",
        )
    )
    fichier.write(
        creer_sql(
            "trips",
            "route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,shape_id,wheelchair_accessible,bikes_allowed,cars_allowed",
        )
    )
