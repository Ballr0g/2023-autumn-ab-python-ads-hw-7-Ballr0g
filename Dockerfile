FROM python:3.12 as requirements-stage
WORKDIR /tmp
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
FROM python:3.12
WORKDIR /build
COPY --from=requirements-stage /tmp/requirements.txt /build/requirements.txt
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r /build/requirements.txt
COPY ./resources /build/resources
COPY ./.env /build/.env
COPY ./app /build/app
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]