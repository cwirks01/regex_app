# text_extractor
Pulling specific text, symbols, and numbers formats using regular expression
#### To run application in Docker with NGINX:


- Run NGINX in a docker container
    - [Link to NGINX installation](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-docker/)

 - Prior to building docker ensure you took the previous container down and create a network
```docker
docker-compose down
THEN
docker network create nlp_project_default
```

 - Ensure GITHUB_TOKEN is saved in your Environmental Variables
```docker
sudo docker-compose build --build-arg GIT_TOKEN="$(echo $GIT_TOKEN)"; sudo docker-compose up -b
```

 - Confirm docker is running properly
```docker
docker logs --tail 50 --follow --timestamps <CONTAINER ID>
```


```Commandline
GITHUB_TOKEN expires every 90 days.
```

