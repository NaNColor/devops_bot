FROM postgres:15.6
RUN mkdir -p /var/log/postgres/ && chown postgres:postgres /var/log/postgresql/ && chmod -R 777 /var/log/postgresql/
RUN touch /var/log/postgres/postgresql.log && chown postgres:postgres /var/log/postgres/postgresql.log
RUN mkdir -p /oracle/pg_data/archive/ && chown postgres:postgres /oracle/pg_data/archive/
COPY init.sql /docker-entrypoint-initdb.d/