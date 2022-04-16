FROM python:latest
COPY src /
EXPOSE 8000 8080
CMD python -m main