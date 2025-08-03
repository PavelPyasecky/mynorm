FROM docker.io/postgres:16

# Install PostGIS and create the extension template
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    binutils \
    gdal-bin \
    python3-gdal \
    postgis \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*

# Copy your maintenance scripts
COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

# Create initialization script
RUN echo "#!/bin/bash\nset -e\npsql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -c \"CREATE EXTENSION IF NOT EXISTS postgis;\"" > /docker-entrypoint-initdb.d/10-postgis.sh
RUN chmod +x /docker-entrypoint-initdb.d/10-postgis.sh