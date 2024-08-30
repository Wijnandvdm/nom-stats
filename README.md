# recipes-db

# build docker image
docker build -t flask-yaml-processor .

# run docker image
docker run -p 5000:5000 flask-yaml-processor