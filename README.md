# ITSA-SSO
In the case of running into an error due to SSL, please launch the docker container on your machine directly to view the returned responses containing the user info and our bearer token. 

With the commands:
1. docker build -t <docker username>/sso:1.0 ./
2. docker run -p 5555:5555 <docker username>/sso:1.0

If unable to retrieve client secret and id, can be retrieved under the G2T5 app after logging in with admin credentials through https://smurnauth-production.fly.dev/
