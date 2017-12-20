FROM python:3.6.3-alpine3.7

# Set up the python backend
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY ./docker_files/backend.py /usr/share/app/
COPY ./docker_files/requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Get the swagger-editor
RUN wget https://github.com/swagger-api/swagger-editor/archive/v3.1.20.tar.gz -O /tmp/swagger_editor.tar.gz
RUN tar -xvf /tmp/swagger_editor.tar.gz --directory /tmp
RUN mkdir /swagger_editor
RUN cp -R /tmp/swagger-editor-3.1.20/dist /swagger_editor/dist/
COPY ./docker_files/index.html /swagger_editor/index.html

# init the container
EXPOSE 5000
CMD python /usr/share/app/backend.py -p 5000
