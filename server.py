"""Python Flask WebApp Auth0 integration example"""

import json, mysql.connector, os
from os import environ as env
from urllib.parse import quote_plus, urlencode
from uuid import uuid4

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
# Don't use filesystem sessions, use standard Flask sessions
# from flask_session import Session
from flask_cors import CORS
global id_var
id_var=0
# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
# Use a strong, fixed secret key for development
app.secret_key = env.get("APP_SECRET_KEY", "super-secret-key-for-auth0-testing")

# Standard Flask session (cookie-based)
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour

# Enable debug mode for more verbose logs
app.debug = True
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# OAuth configuration
oauth = OAuth(app)

# Print environment for debugging
print("Environment variables:")
for key in ["APP_SECRET_KEY", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET", "AUTH0_DOMAIN"]:
    print(f"{key}: {'Set' if env.get(key) else 'NOT SET'}")

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Controllers API

db_config = {
    'host': 'localhost',        
    'user': 'root',             
    'password': '',
    'database': 'ourrupee'  
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection


@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )
 
@app.route("/login")
def login():
    # Clear any existing session data
    session.clear()
    
    # Generate and store state
    state = str(uuid4())
    session['oauth_state'] = state
    session.permanent = True
    
    # Debug session
    print(f"Login - Session contents: {dict(session)}")
    print(f"Login - Session ID: {session.sid if hasattr(session, 'sid') else 'No SID'}")
    
    # Get correct callback URL
    callback_url = url_for("callback", _external=True)
    print(f"Login - Callback URL: {callback_url}")
    
    # Show Auth0 info
    print(f"Login - Auth0 Domain: {env.get('AUTH0_DOMAIN')}")
    print(f"Login - Auth0 Client ID: {env.get('AUTH0_CLIENT_ID')}")
    
    # Redirect to Auth0
    return oauth.auth0.authorize_redirect(
        redirect_uri=callback_url,
        state=state
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    # Debug info
    print(f"Callback - Full request URL: {request.url}")
    print(f"Callback - Request args: {request.args}")
    print(f"Callback - Session contents: {dict(session)}")
    
    # Get states
    request_state = request.args.get('state')
    session_state = session.get('oauth_state')
    
    print(f"Callback - Request state: {request_state}")
    print(f"Callback - Session state: {session_state}")
    
    # Check state match
    if not session_state:
        print("ERROR: No state in session!")
        return "No state found in session. Session may not be persisting.", 400
        
    if session_state != request_state:
        print(f"ERROR: State mismatch! Session: {session_state}, Request: {request_state}")
        return "State mismatch error", 400
    
    try:
        token = oauth.auth0.authorize_access_token()
        print(f"Auth0 token received successfully")
        session["user"] = token
        session.permanent = True
        return redirect("/")
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return f"Authentication error: {str(e)}", 400


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

@app.route("/submit",methods=["POST"])
def submit():
        global id_var
        id_var = id_var+1
        data = request.form
        name = data.get('name')
        mobile = data.get('mobile')
        email = data.get('email')
        title = data.get('title')
        description = data.get('description')
        target = data.get('target')
        
        """video_files = request.files.getlist('videos')
        document_files = request.files.getlist('documents')
        news_files = request.files.getlist('news')
        video_data = b''.join([video.read() for video in video_files if video])
        document_data = b''.join([document.read() for document in document_files if document])
        news_data = b''.join([news.read() for news in news_files if news])"""
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            insert_query = """
               INSERT INTO registrations (id,name, mobile, email, title, description, target)
               VALUES (%s,%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (id_var,name, mobile, email, title, description, target))

            connection.commit()
            return jsonify({"message": "Form submitted successfully!"}), 200
        except mysql.connector.Error as e:
             print(f"Error: {e}")
             return jsonify({"message": "An error occurred while submitting the form."}), 500
        finally:
            cursor.close()
            connection.close()

@app.route('/api/requests', methods=['POST'])
def get_requests():
    print("POST request received")  # Debugging line
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT name, title, description, mobile, target FROM registrations")
        results = cursor.fetchall()

        print("Results:", results)  # Debugging line
        return jsonify(results)
    
    except mysql.connector.Error as err:
        print("Database error:", err)  # Debugging line
        return jsonify({"error": str(err)}), 500
    
    finally:
        cursor.close()
        connection.close()

@app.route('/adminlogincheck', methods=['POST'])
def adminlogincheck():
    datanew = request.get_json()
    username = datanew.get("username")
    print(username)
    password = datanew.get("password")
    print(password)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE user = %s AND pass = %s", (username, password))
    admin = cursor.fetchone()
    conn.close()
    print(admin)
    if admin:
        print("success")
        return jsonify({"status": "success"})
    elif not admin:
        print("fail")
        return jsonify({"status": "fail"})





@app.route("/register")
def register():
    return render_template("registration2.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/viewcamp")
def viewcamp():
    return render_template("viewcamp.html")


@app.route("/adminlogin")
def adminlogin():
    return render_template("adminlogin.html")

@app.route("/campaignpage")
def campaignpage():
    return render_template("campaignpage.html")

@app.route("/createcam")
def createcam():
    return render_template("createcam.html")

@app.route("/userdash")
def userdash():
    return render_template("dash3.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
