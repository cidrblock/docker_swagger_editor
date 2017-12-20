rm -rf ./swagger_codegen
docker run --rm -v ${PWD}:/working swaggerapi/swagger-codegen-cli generate -i working/$1 -l python-flask -o /working/swagger_codegen
rm -rf ./swagger_server/models
mkdir -p swagger_server
echo -----------Copy files to be overwritten everytime
cp -v -R ./swagger_codegen/swagger_server/models ./swagger_server/
cp -v -R ./swagger_codegen/swagger_server/swagger ./swagger_server/
echo -----------Copy files only copied if they don\'t exist
cp -v -Rn ./swagger_codegen/swagger_server/controllers ./swagger_server/
cp -v -n ./swagger_codegen/swagger_server/__main__.py ./swagger_server/
cp -v -n ./swagger_codegen/swagger_server/encoder.py ./swagger_server/
cp -v -n ./swagger_codegen/swagger_server/util.py ./swagger_server/
cp -v -n ./swagger_codegen/requirements.txt .
