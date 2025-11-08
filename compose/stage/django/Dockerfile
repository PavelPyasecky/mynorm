# define an alias for the specific python version used in this file.
FROM python:3.12.9-slim-bookworm AS python

# Python build stage
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

# Install apt packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    libpq-dev \
    binutils \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_HOME}

COPY pyproject.toml poetry.lock ./

# Install Poetry with the export plugin
RUN pip install --no-cache-dir poetry poetry-plugin-export

# Create virtual environment
RUN python -m venv /venv

# Export requirements using Poetry with export plugin
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install dependencies into virtual environment
RUN /venv/bin/pip install --upgrade pip
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Verify installation in build stage
RUN /venv/bin/python -c "import drf_spectacular; print('✅ drf_spectacular installed, version:', drf_spectacular.__version__)"

# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"

WORKDIR ${APP_HOME}

# Install runtime system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  libpq5 \
  gettext \
  wait-for-it \
  binutils \
  gdal-bin \
  libgdal-dev \
  python3-gdal \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# Copy virtual environment from build stage
COPY --from=python-build-stage /venv /venv

# Create django user
RUN addgroup --system django \
  && adduser --system --ingroup django django

# Copy entrypoint scripts
COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# copy application code to WORKDIR
COPY --chown=django:django . ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown -R django:django ${APP_HOME}

# Final verification as django user
USER django
RUN /venv/bin/python -c "import drf_spectacular; print('✅ drf_spectacular is accessible, version:', drf_spectacular.__version__)"

ENTRYPOINT ["/entrypoint"]