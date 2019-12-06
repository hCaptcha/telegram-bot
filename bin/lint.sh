TYPE=python
SOURCE_CODE=../app/

docker run -it --rm -v $(pwd):/work hmtcentral.azurecr.io/linter:latest $TYPE $SOUCE_CODE
