docker login -u "$DOCKER_PUBLISHER_USER" -p "$DOCKER_PUBLISH_API_KEY" docker.io
docker build . -f Dockerfile.aws.lambda.python.build.image -t therowantree/aws.lambda.python.build.image:latest
docker push therowantree/aws.lambda.python.build.image:latest
docker logout
