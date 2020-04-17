# gameficate-engine
Open Source Gamification Engine


# Tutorials

## Database (Migrations)

- Create schema called 'gamificate'

- Create .env file following .env_sample specifications

- To update db: 
```shell
flask db upgrade
```

- To apply changes in models to db: 
```shell
flask db migrate -m "message"
flask db upgrade
```

## App Server

- Start:
```shell
flask run
```

## API Testing

- Start App Server
- Run HTTPie commands to test, e.g.:
```shell
http POST http://localhost:5000/api/auth id_realm=<id> api_key=<api_key>
http --auth-type=jwt --auth="$(cat file_with_token.txt)" GET http://localhost:5000/api/users
http --auth-type=jwt --auth="<token>" GET http://localhost:5000/api/users
http --auth-type=jwt --auth="<token>" POST http://localhost:5000/api/users email="example@mail.pt" username="example"
```
### HTTPie options:
* -h : show header
* -v : show full request