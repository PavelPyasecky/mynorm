FROM docker.io/postgres:16

# Install PostGIS and GDAL dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

# Initialize PostGIS in the database
COPY ./compose/production/postgres/initdb-postgis.sh /docker-entrypoint-initdb.d/10-postgis.sh
RUN chmod +x /docker-entrypoint-initdb.d/10-postgis.sh