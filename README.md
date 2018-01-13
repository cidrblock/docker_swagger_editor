### Docker swagger editor

This repository serves as a jump start for building APIs using swagger, swagger editor, and swagger codegen.

Swagger editor is pulled from https://github.com/swagger-api/swagger-editor.  The index.html file is patched to enable automatic saving of the swagger file as it is edited.

A simple flask python script serves as the backend api which both serves the swagger file and saves it.

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

See https://github.com/cidrblock/codegenit
