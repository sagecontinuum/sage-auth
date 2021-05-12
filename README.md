# SAGE Auth

Auth server for SAGE to let users authenticate using their institutional identity provider and create tokens for access to other SAGE resources.


# Test environments 


Both test environments described below are not to be used in production, they are only for development/testing purposes!

In production the default login is authentication delegated to Globus Auth, the login will not work in a local deployment without SSL certificate and client registration with the Globus OAuth server. Instead, the test deployments via the docker-compose create a native Django test user (see [testing-entrypoint.sh](testing-entrypoint.sh)) and the developer can login via [http://localhost:8000/login](http://localhost:8000/login) as `test` with password `test`.  



## minikube

For instructions see [minikube](minikube).


## docker-compose

Starts a local instance of the SAGE Auth server on [http://localhost:8000/](http://localhost:8000/) and creates a test user that can be used to log in.

```bash
docker-compose up
```


# Globus OAuth registration

- Create a globus account.
- Go to [https://auth.globus.org/v2/web/developers](https://auth.globus.org/v2/web/developers).
- Create a project.
- Add new app.
- Add scopes: profile, urn:globus:auth:scope:auth.globus.org:view_identity_set
- Specify redirect URL: https://<your-domain>/complete/globus/
    - This requires SAGE Auth to have an TLS certificate!
- Generate new client secret

SAGE Auth server has to be started with these two arguments:
- Globus_Auth_Client_ID
- Globus_Auth_Client_Secret



# Token introspection API

Other SAGE resources (e.g. API server) can verify SAGE tokens via the introspection API resource. For this a native Django user `sage-api-server` has to be created:

```bash
kubectl exec -it  <pod> -- /bin/ash

./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('sage-api-server', 'test@example.com', 'secret')"
```

Example token verification:
```bash
curl -X POST -H 'Accept: application/json; indent=4' -H 'Content-Type: application/x-www-form-urlencoded' -H "Authorization: Basic c2FnZS1hcGktc2VydmVyOnRlc3Q=" -d 'token=<SAGE-USER-TOKEN>'  <sage-auth-hostname>:80/token_info/
```
The basicAuth used here is the base64 encoding of `sage-api-server:test`.


Example response:
```json5
{
    "active": true,        # boolean value of whether or not the presented token is currently active.
    "scope": "default",    # A JSON string containing a space-separated list of scopes associated with this token.
    "client_id": "<user>",
    "username": "<user>",
    "exp": 1591632949      # The unix timestamp (integer timestamp, number of seconds since January 1, 1970 UTC) indicating when this token will expire. 
}
```
