from flask import *
from email_otp import *
from pymongo import MongoClient
import time

app = Flask(__name__)
app.secret_key = 'EmailAuthenticationByMahesh2024'

# MongoDB connection details
#mongo_url = "mongodb://localhost:27017/"
mongo_url = "mongodb://mongo:27017/" # Connecting to docker mongodb
db_name = "user_db"

# Function to connect to MongoDB
def connect_to_mongo():
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        return db, client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None, None

# Function to perform MongoDB operations
def perform_mongo_operation(data):
    db, client = connect_to_mongo()
    if db is not None and client is not None:
        # Check if the database exists
        existing_databases = client.list_database_names()
        if db_name not in existing_databases:
            print(f"Database '{db_name}' does not exist. Creating...")
            db = client[db_name]

        # Ensure the collection exists
        info_table = db['info_collection']
        print("Using collection 'info_collection'")

        # Check for duplicate entries
        existing_entry = info_table.find_one({
            '$or': [
                {'Email': data['Email']},
                {'Employee Id': data['Employee Id']}
            ]
        })

        if existing_entry:
            duplicate_fields = []
            if existing_entry.get('Email') == data.get('Email'):
                duplicate_fields.append('Email')
            if existing_entry.get('Employee Id') == data.get('Employee Id'):
                duplicate_fields.append('Employee ID')

            flash(f"Duplicate entry found in {', '.join(duplicate_fields)}")
            return False
        else:
            # Insert data into the collection
            info_table.insert_one(data)
            print("Data inserted into MongoDB")
            return True
    else:
        return False

# Send email with OTP
def mailsender():
    try:
        rec_email = request.form["email"]
        current_otp = sendEmailVerificationRequest(receiver=rec_email)
        session['current_otp'] = current_otp
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Main Form Route
@app.route("/", methods=['GET', 'POST'])
def sysaudit_form():
    if request.method == 'POST':
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

        data = {
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
        }

        # Perform MongoDB operation
        # A nested if else statement
        if perform_mongo_operation(data):
            # Send email with OTP
            if mailsender():
                return redirect(url_for('verify'))
            else:
                flash("Error sending email")
        else:
            #flash("Duplicate entry or error inserting data into DB")
            print('Duplicate entry or error inserting data into DB')

    return render_template('index.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

# Otp Verification Route
@app.route('/verify')
def verify():
    return render_template('verify.html')

# Validate Otp Route
@app.route('/validate', methods=["POST"])
def validate():
    current_user_otp = session.get('current_otp')
    #print(current_user_otp)
    user_otp = request.form.get('otp')
    #print(user_otp)

    if current_user_otp and user_otp and int(current_user_otp) == int(user_otp):
        
        # Clear the current_otp from the session
        session.pop('current_otp', None)
        
        # Clear the entire session history
        session.clear()

        return redirect(url_for('sysaudit_form'))
    else:
        # Flash an error message
        #print("Flashing error message")
        flash("Invalid OTP")

        # Redirect to the verification page
        return redirect(url_for('verify'))
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
