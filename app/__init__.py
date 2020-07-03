from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
import logging
from logging.handlers import SMTPHandler
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS
from flask_talisman import Talisman
import stripe
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            instance_relative_config=True) 
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'
mail = Mail(app)

jwt = JWTManager(app)

CORS(app)

if not app.debug:
    csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'stackpath.bootstrapcdn.com',
            'code.jquery.com',
            'cdn.jsdelivr.net',
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'cdn.buymeacoffee.com',
            '*.w3.org'
        ],
        'img-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'cdn.buymeacoffee.com',
            'www.w3.org',
            'data: *',
            '*'
        ],
        'script-src':[
            '\'self\'',
            '\'unsafe-inline\'',
            'checkout.stripe.com',
            'cdn.jsdelivr.net',
            'stackpath.bootstrapcdn.com',
            'code.jquery.com'
        ],
        'child-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'checkout.stripe.com'
        ],
        'connect-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'checkout.stripe.com'
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'checkout.stripe.com',
            'fonts.googleapis.com',
            'fonts.gstatic.com',
        ]
    }
    Talisman(app, content_security_policy=csp)

stripe.api_key = os.environ['STRIPE_SECRET_KEY']
stripe.publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.realms import bp as realms_bp
app.register_blueprint(realms_bp)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')


# Error handling
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Gamificate Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

## API DOC
app.config['SWAGGER'] = {
    'title': "Gamificate API",
    'uiversion': 3,
    'hide_top_bar': True,
    'head_text': 
    """
<link rel="stylesheet" href="../static/css/bootstrap_navbar.min.css">
<style>@import url('https://fonts.googleapis.com/css2?family=Russo+One&display=swap');</style>
<script>
        function addMargin() {
            document.getElementById("swagger-ui").style.marginTop = "80px";
        }

        window.addEventListener('DOMContentLoaded', addMargin);
</script>
    """,
    'top_text':
    """
    <style>
        .navbar-custom {
            background-color: #292825 !important;
            border-bottom: 2px solid black !important;
            font-size: 18px !important;
            font-family: 'Russo One', sans-serif !important;
        }
    </style>
	<nav class="navbar fixed-top navbar-expand-lg navbar-dark navbar-custom">
	    <a class="navbar-brand" href="http://www.gamificate-engine.com">Gamificate</a>
	</nav>
    """,
    'favicon': '../static/img/favicon/favicon-32x32.png',
    # 'openapi': '3.0.2',
}
swagger_config = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'docs',
            'route': '/swagger.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': "/api/"
}
template = {
  "info": {
    "title": "Gamificate API",
    "description": 
        """
# Welcome to Gamificate API Documentation!
Here you can find the documentation for the API available for the users of our app, **Gamificate**. 
In this page you will be able to explore the existing routes: checking what they can do, what are their parameters and what they return. You can even test it within the docs! (if you have the right permissions, of course, but we will discuss it later). An example of parameter data and return data are also available for all the routes.

### Content:

 1. Quickstart
 2. Authentication
 3. Routes

## Quickstart:
To be able to use our API, you need first to create an account in our app: [Gamificate](http://www.gamificate-engine.com).  

After signing up, you will need to create your first Realm. A Realm is the environment on which you will have your users, badges and rewards. In other words, a Realm represents the context on which you want to introduce gamification. 

When you create your Realm, an API Key will be sent to your email. That API Key must be kept a secret and handled carefuly, in order to keep people who want to ruin your Realm away! If you eventually lose your API Key, or want a new one, you can generate it on our app's dashboard.

Our API only allows you to interact with Users, Badges and Rewards. You will not be able to create Realms or Gamificate accounts through here. For that, you need to do it in our app's dashboard. Creating Badges and Rewards are also not covered here, but you can consult them and check their infos with the provided routes.

To be able to use our API, you need to authenticate yourself first. This will be explained in the next section.

## Authentication:
So, now that you have your API Key, you can access your Realm through our API!  

Every route we provide is locked. This means you need the *access_token* given by the **api/auth/** route, the only one that is not locked. Our authentication works via JWT, so you need to pass the token in every request's header like this:

`Authorization: Bearer <your_token>`

The *access_token* has a relatively short lifetime, so you may need to get a new one. But don't worry, we got your back! We provide you the **api/auth/refresh** route, that creates another *access_token*. To access this route though, you need to provide the *refresh_token* the API gave you when you authenticated. This *refresh_token* has a bigger lifetime, when compared to the other token.

Please store your tokens in a secure way!


## Routes:
We divided our routes in the following structure:
- **Auth**: routes that allow you to get the access and refresh tokens
- **Badges**: routes that allow you to get information regarding the Realm's Badges
- **Leaderboards**: routes that allow you to get the user's ranking, ordered by different properties
- **Rewards**: routes that allow you to get information regarding the Realm's Rewards
- **Users**: routes that allow you to interact with your Realm's users
	- **Badges**: routes that allow you to connect your users with the Realm's badges
	- **Rewards**: routes that allow you to connect your users with the Realm's rewards

You can get more info on each one of the routes below, and even testing them in real time with real values and real results. So, take care when using this feature!

As every route is locked and needs authentication, you have a button on your right that allows you to do that and will fill the request's header with the token you provide. Please follow the instructions on how to authenticate when you click the button. If you enter your token with a different format, the authorization will not be accomplished.

Have fun and **Gamificate** a lot!
        """,
    "contact": {
      "responsibleOrganization": "Universidade do Minho",
      "responsibleDeveloper": "Henrique Pereira, Pedro Moreira, Sarah Silva",
      "email": "gamificate.engine@gmail.com",
    },
    # "termsOfService": "http://me.com/terms",
    "version": "0.0.1"
  },
  "host": "www.gamificate-engine.com",  # overrides localhost:500
#   "basePath": "/api",  # base bash for blueprint registration
  "schemes": [
    "https"
  ],
#   "operationId": "getmyData"
    "securityDefinitions": {
        "Bearer": {
            "description":"Where above says '(apiKey)' it should say '(JWT)', but this version of Swagger UI doesn't allow it and there is no support yet for Flask in the newer versions. So, for accessing the API a valid JWT token must be passed in all the queries in the 'Authorization' header. A valid JWT token (access_token) is generated by the API and retourned as answer of a call to the route /auth giving a valid Realm ID and API key or, when the previous expires, by /auth/refresh. This last one requires the refresh_token instead of the access_token. The following syntax must be used in the 'Authorization' header :\n\n  \tBearer <token>",
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }       
}
swagger = Swagger(app, config=swagger_config, template=template)

from app import models
