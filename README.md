# gameficate-engine
Open Source Gamification Engine


# Tutorials

## Databse (Migrations)

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
