
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
    echo "Poetry version:" && \
    poetry --version && \
    echo "Exporting requirements..." && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    echo "Generated requirements.txt:" && \
    cat requirements.txt && \
    echo "Installing dependencies with uv..." && \
    uv pip install --no-cache-dir -r requirements.txt --python /venv/bin/python && \
    echo "Verifying drf-spectacular installation..." && \
    /venv/bin/python -c "import drf_spectacular; print('drf_spectacular version:', drf_spectacular.__version__)"


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

# Ensure django user owns the virtual environment
RUN chown -R django:django /venv


# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # entrypoint
  wait-for-it \
  # gdal
  binutils \
  gdal-bin \
  libgdal-dev \
  python3-gdal \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

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

# Ensure all dependencies are installed and accessible
RUN chown -R django:django /venv && \
    chmod -R 755 /venv

USER django

ENTRYPOINT ["/entrypoint"]
