# sage-ui

Draft of a website for SAGE to let users authenticate using their institutional identity provider and create tokens for access to other SAGE resources.


# test instance using docker-compose

Starts a local instance of the SAGE UI on [http://localhost:8000/](http://localhost:8000/) and creates a test user that can be used to log in.

```bash
docker-compose up
```


The docker-compose file in this git repository is not used in production, it is only for development/testing purposes. In production the default login is authentication delegated to Globus Auth, the login will not work in a local deployment without SSL certificate and client registration with the Globus OAuth server. Instead, the deployment via the docker-compose file creates a native Django user (see [testing-entrypoint.sh](testing-entrypoint.sh)) and the developer can login via [http://localhost:8000/login](http://localhost:8000/login) as `test` with password `test`.  

