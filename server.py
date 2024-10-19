"""Python Flask WebApp Auth0 integration example"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from uuid import uuid4

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
from flask_session import Session

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY", "your-default-secret-key")

# Session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_COOKIE_SECURE"] = False  # Use True in production
app.config["SESSION_PROTECTION"] = "strong"
app.config["SESSION_KEY_PREFIX"] = "auth0_"
app.config["SESSION_COOKIE_PATH"] = "/"
Session(app)

# OAuth configuration
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

print("APP_SECRET_KEY:", env.get("APP_SECRET_KEY"))
print("AUTH0_CLIENT_ID:", env.get("AUTH0_CLIENT_ID"))
print("AUTH0_DOMAIN:", env.get("AUTH0_DOMAIN"))
# Controllers API

@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )

@app.route("/login")
def login():
    print(f"Session before setting state: {session}")
    state = str(uuid4())
    session['oauth_state'] = state
    print(f"Session after setting state: {session}")
    return oauth.auth0.authorize_redirect(
        redirect_uri="http://localhost:3000/callback",
        state=state
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    print(f"Session during callback: {session}")
    request_state = request.args.get('state')
    session_state = session.get('oauth_state')
    print(f"Request state: {request_state}")
    print(f"Session state: {session_state}")
    
    if 'oauth_state' not in session or session['oauth_state'] != request_state:
        return "State mismatch error", 400

    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
