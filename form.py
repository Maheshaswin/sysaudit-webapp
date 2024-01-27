from flask import *  
from random import *  
from email_otp import *
from pymongo import MongoClient


app = Flask(__name__)

app.secret_key = 'EmailAuthenticationByMahesh2024'

def mailsender():
    rec_email = request.form["email"]
    current_otp = sendEmailVerificationRequest(receiver=rec_email) # this function sends otp to the receiver and also returns the same otp for our session storage
    session['current_otp'] = current_otp

# MongoDB connection details
mongoURL = "mongodb://localhost:27017/"
db_name = "user_db"

# Function to connect to MongoDB
def connect_to_mongo():
    try:
        client = MongoClient(mongoURL)
        db = client[db_name]
        return db, client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None, None

# Route to check MongoDB connection
@app.route('/check_mongo_connection')
def check_mongo_connection():
    # Attempt to connect to MongoDB
    db, client = connect_to_mongo()

    if db is not None and client is not None:
        return jsonify({"status": "success", "message": "Connected to MongoDB"})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to MongoDB"})

# Main Form
@app.route("/", methods=['GET', 'POST'])
def sysaudit_form():
    # Method equals to post then get the info from form
    if request.method == 'POST':
        print("Received POST request")
        # Extraction info from form
        tlname = request.form['tl']
        empid = request.form['empid']
        empname = request.form['name']
        email = request.form['email']
        desig = request.form['designation']
        bunit = request.form['bunit']
        brand = request.form['device']
        model = request.form['model']
        sn = request.form['sn']
        issue = request.form['issue']

        # Connect to MongoDB
        db, client = connect_to_mongo()
        print("Connected to MongoDB")

        # Check if the database exists
        existing_databases = client.list_database_names()
        if db_name not in existing_databases:
            print(f"Database '{db_name}' does not exist. Creating...")
            db = client[db_name]

        # Ensure the collection exists
        info_table = db['info_collection']
        print("Using collection 'info_collection'")

        # Insert data into the collection
        info_table.insert_one({
            'TL name': tlname,
            'Employee Id': empid,
            'Employee Name': empname,
            'Email': email,
            'Designation': desig,
            'Business Unit': bunit,
            'Device Brand': brand,
            'Device Model': model,
            'Serial Number': sn,
            'Issue': issue
        })
        print("Data inserted into MongoDB")
        
        mailsender()
        return redirect(url_for('verify'))
        
        #return jsonify({"status": "success", "message": "Data inserted into MongoDB"})
        
    
    #print("Not a POST request")
    return render_template('index.html')


# Policy Route
@app.route("/policy", methods=["GET"])
def policy():
    return render_template('policy.html')

# Otp Verfication
@app.route('/verify')  
def verify():  
    return render_template('verify.html')

@app.route('/validate', methods=["POST"])
def validate():
    # Actual Otp which was sent to the receiver
    current_user_otp = session.get('current_otp')
    print("Current User OTP", current_user_otp)

    # Otp Entered by the User
    user_otp = request.form.get('otp')
    print("User OTP : ", user_otp)

    # Otp checking and redirection
    if current_user_otp and user_otp and int(current_user_otp) == int(user_otp):
        # Clear the current_otp from the session
        session.pop('current_otp', None)
        # Clear the sesstion
        session.clear()
        return '<h3>Successfully Verfied</h3>'
    else:
        flash("Invalid OTP")
        return redirect(url_for('verify'))   

# Start the server
if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)