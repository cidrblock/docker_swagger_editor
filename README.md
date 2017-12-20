### Docker swagger editor

This repository serves as a jump start for building APIs using swagger, swagger editor, and swagger codegen.  It is currently set up to build a python flask project.

Included:

- A dockerfile to build a containerized version of the swagger editor that has automatic file saving enabled
- A codegen shell script that will convert a swagger file to a skeleton python/flash project.


### Build the container

Build the docker container:

```
docker build . -t dse
```

### Run the docker container

```
cd ~/your_project_folder
docker run --rm -it -p 5000:5000 -v ${PWD}:/working dse
```

### Launch the browser

```
http://localhost:5000/?url=api.yml
```
replace api.yml with the name of your swagger file if different

### Generate the code

Copy the `codegenit.sh` script into your project folder.

When you have completed your edits:

```
./codegenit.sh api.yml
```

### Run the API

```
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
python -m swagger_server
```
and point your browser to

```
http://localhost:8080/api/v1/ui
```

or curl it

```
curl http://localhost:8080/api/v1/message
```
