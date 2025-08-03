
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
    libproj-dev \
    gdal-bin \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/* \


# Set environment variables for GDAL
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so


# Install uv directly to /usr/local/bin (updated path)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv


# Install Poetry with export plugin
RUN pip install --no-cache-dir poetry poetry-plugin-export gunicorn


WORKDIR ${APP_HOME}

COPY pyproject.toml poetry.lock ./

# Create virtual environment and install dependencies
RUN python -m venv /venv && \
    . /venv/bin/activate && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    uv pip install -r requirements.txt --python /venv/bin/python


# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}
ENV PATH="/venv/bin:$PATH"


WORKDIR ${APP_HOME}

# Copy virtual environment from build stage
COPY --from=python-build-stage /venv /venv

RUN addgroup --system django \
  && adduser --system --ingroup django django


# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # entrypoint
  wait-for-it \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


# Copy installed packages from build stage
COPY --from=python-build-stage /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-build-stage /usr/local/bin/uv /usr/local/bin/uv


COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint


COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


# copy application code to WORKDIR
COPY --chown=django:django . ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown  django:django ${APP_HOME}/media
RUN chown  django:django ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint"]
