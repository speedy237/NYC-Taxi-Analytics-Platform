FROM apache/superset:latest

USER root
# Driver Trino pour SQLAlchemy / Superset
# RUN pip install "sqlalchemy-trino"
RUN /app/.venv/bin/pip install "trino"


USER superset
