FROM python:3.11-bookworm

LABEL maintainer="Kronos443 <kronos443@mitchell.org.uk>"

COPY ./nutcase/docker/install-nginx-debian.sh /
RUN bash /install-nginx-debian.sh

# Install requirements
COPY ./nutcase/docker/requirements_core.txt /tmp/requirements_core.txt
RUN pip install --no-cache-dir -r /tmp/requirements_core.txt

EXPOSE 9995

# Remove default configuration from Nginx
RUN rm /etc/nginx/conf.d/default.conf
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY ./nutcase/docker/uwsgi.ini /etc/uwsgi/

# Install Supervisord
RUN apt-get update && apt-get install -y supervisor \
&& rm -rf /var/lib/apt/lists/*
# Custom Supervisord config
COPY ./nutcase/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy stop-supervisor.sh to kill the supervisor and substasks on app failure
COPY ./nutcase/docker/stop-supervisor.sh /etc/supervisor/stop-supervisor.sh
RUN chmod +x /etc/supervisor/stop-supervisor.sh

# Which uWSGI .ini file should be used, to make it customizable
ENV UWSGI_INI /app/uwsgi.ini
# By default, run 2 processes
ENV UWSGI_CHEAPER 2
# By default, when on demand, run up to 16 processes
ENV UWSGI_PROCESSES 16
# By default, allow unlimited file sizes, modify it to limit the file sizes
# To have a maximum of 1 MB (Nginx's default) change the line to:
# ENV NGINX_MAX_UPLOAD 1m
ENV NGINX_MAX_UPLOAD 0
# By default, Nginx will run a single worker process, setting it to auto
# will create a worker for each CPU core
ENV NGINX_WORKER_PROCESSES 1
# By default, Nginx listens on port 80.
# To modify this, change LISTEN_PORT environment variable.
# (in a Dockerfile or with an option for `docker run`)
ENV LISTEN_PORT 9995

# Copy start.sh script that will check for a /app/prestart.sh script and run it before starting the app
COPY ./nutcase/docker/start.sh /start.sh
RUN chmod +x /start.sh

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/app/static
# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 0

#===========================================================================
# Install app requirements

# Add app
COPY ./nutcase/app /app
WORKDIR /app

# RUN apt-get install nano
RUN apt-get install tzdata
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Make /app/* available to be imported by Python globally to better support 
# several use cases like Alembic migrations.
ENV PYTHONPATH=/app

# Copy the entrypoint that will generate Nginx additional configs
COPY ./nutcase/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script which will check for an /app/prestart.sh script 
# (e.g. for migrations) and then will start Supervisor, which in turn 
# will start Nginx and uWSGI
CMD ["/start.sh"]