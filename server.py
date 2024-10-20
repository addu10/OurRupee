"""Python Flask WebApp Auth0 integration example"""

import json, mysql.connector
from os import environ as env
from urllib.parse import quote_plus, urlencode
from uuid import uuid4

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
from flask_session import Session
from flask_cors import CORS
global id_var
id_var=0
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
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
