from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "myapp"

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database    
db = SQLAlchemy(app)


#User Model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create a model for the database and store the messages
class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

#Create the database


#Login Route 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.username
            flash('Login successful', 'success')
            return redirect('/')
        else:
            flash("Invalid credentials, try again!", 'danger')

    return render_template('login.html')


#Logout Route
@app.route('/logout')
def logout(): 
    session.pop('user', None)
    flash('You have been logged out', 'info')
    return redirect('/login')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/submit", methods=['POST'])
def submit():
    name = request.form.get('name')
    message = request.form.get('message')

    # Save the message to the database
    new_message = Messages(name=name, message=message)
    db.session.add(new_message)
    db.session.commit()

    return redirect('/messages')  # Redirect to the messages page

@app.route('/messages')
def messages():
    messages = Messages.query.all()
    return render_template('messages.html', messages=messages)

#Delete a message
@app.route('/delete/<int:id>', methods=['POST'])
def delete_message(id):
    if "user" not in session:
        flash("You must be logged in to delete a message", 'danger')
        return  redirect('/login')
    
    msg_to_delee = Messages.query.get(id)
    if msg_to_delee:
        db.session.delete(msg_to_delee)
        db.session.commit()
        flash('Message deleted successfully', 'success')
    return redirect('/messages')

#Modify edit route to Require Login
@app.route('/edit/<int:id>')
def edit_message(id):
    if "user" not in session:
        flash("You must be logged in to edit a message", 'danger')
        return  redirect('/login')
    
    message = Messages.query.get(id)
    return render_template('edit.html', message=message)

#Update a message
@app.route('/update/<int:id>', methods=['POST'])
def update_message(id):
    if "user" not in session:
        flash("You must be logged in to update a message", 'danger')
        return  redirect('/login')
    
    message = Messages.query.get(id)
    message.name = request.form.get('name')
    message.message = request.form.get('message')
    db.session.commit()
    flash('Message updated successfully', 'success')
    return redirect('/messages')

if __name__ == '__main__':
    with app.app_context():
          db.create_all()
    app.run(debug=True)
