from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment, Bundle
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "sasjdn214jnxc2mf039"
assets = Environment(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signmeup"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

js = Bundle('./javascript/script.js',
            output='gen/scripts.js')
assets.register('js_all', js)

css = Bundle('./css/styles.css',
            output='gen/styles.css')
assets.register('css_all', css)

class User(  UserMixin, db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    bio = db.Column(db.Text())
    picture = db.Column(db.String(100))
    username = db.Column(db.String(10))
    password = db.Column(db.String(20))

    # relationships
    booking = db.relationship( "Booking", backref="user" )
    review = db.relationship( "Review", backref="user" )
    instructor = db. relationship ("Instructor", backref ="user")


    def __init__(self, fname, lname, bio, picture, username, password):
        self.fname = fname
        self.lname = lname
        self.bio = bio
        self.picture = picture
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Instructor(db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    bio = db.Column(db.Text())
    picture = db.Column(db.String(100))
    category = db.Column(db.String(100))
    video = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    location = db.Column(db.String(100))
    #username = db.Column(db.String(10))
    #password = db.Column(db.String(20))

    # relationships
    booking = db.relationship( "Booking", backref="instructor" )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, fname, lname, bio, picture, category, video, years_of_experience, location, user): #username, password):
        self.fname = fname
        self.lname = lname
        self.bio = bio
        self.picture = picture
        self.category = category
        self.video = video
        self.years_of_experience = years_of_experience
        self.location = location
        #self.username = username
        #self.password = password
        #self.booking = booking
        self.user = user


class Booking( db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    date = db.Column(db.String(100))
    start_time = db.Column(db.String(100))
    end_time = db.Column(db.String(100))
    price= db.Column(db.Integer)
    location = db.Column(db.String(50)) # added "location", not on diagram


    # relationships
    reviews = db.relationship( "Review", backref="booking" )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))


    def __init__(self, category, date, start_time, end_time, price, location,user):
        self.category = category
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.price = price
        self.location = location
        self.user = user
       #self.instructor = instructor
        #self.review - review

class Review( db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    # relationships
   # booking = db.relationship( "Booking", backref="review" )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))


    def __init__(self, rating, comments, user, booking):

        self.rating = rating
        self.comments = comments
        self.user = user
        self.booking = booking


# MAIN ROUTES
#today = datetime.now()
#datetime.strptime('2015-01-02T00:00', '%Y-%m-%dT%H:%M')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():


    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by( username = username, password = password ).first()

        if user is not None:
            login_user(user)

            return redirect("/dashboard")
        else:
            flash("No user found")
            return redirect("/login")

    else:

        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect("/")

@app.route("/signup")
def register():
    return render_template("register.html")

@app.route("/teach")
@login_required
def registerInstructor():
    return render_template("registerInstructor.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/book")
@login_required
def createAbooking():
    return render_template("createBooking.html")


@app.route("/bookingcomplete")
def bookingcomplete():
        return render_template("bookingcomplete.html")


# CRUDI - Users Controller

@app.route("/users")
def all_users():
    allUsers = User.query.all()
    return render_template("users.html", users = allUsers)

@app.route("/users/create", methods=["POST"])
def create_user():
    fname = request.form.get('fname', "")
    lname = request.form.get('lname', "")
    bio = request.form.get('bio', "")
    picture = request.form.get('picture', "")
    username = request.form.get('username', "")
    password = request.form.get('password', "")

    newUser = User(fname, lname, bio, picture, username, password)
    db.session.add(newUser)
    db.session.commit()

    return redirect("/login")

#@app.route("/users/settings")
#def get_user():
#    print("=================================================")
#    print("Not here")
#    print(current_user.id)
#    print("=================================================")
#    user = current_user.id
#    return redirect("/users/delete")

@app.route("/users/edit", methods=['GET', 'POST'])
@login_required
def edit_user():
    user = User.query.get(int(current_user.id))

    if request.method == "POST":


        user.fname = request.form.get('fname', "")
        user.lname = request.form.get('lname', "")
        user.bio = request.form.get('bio', "")
        user.picture = request.form.get('picture', "")
        user.username = request.form.get('username', "")
        user.password = request.form.get('password', "")
        db.session.commit()
        return render_template("dashboard.html", user = user)
    else:
        return render_template("editUser.html", user = user)

@app.route("/users/delete", methods=['GET','POST'])
@login_required
def delete_user():

    uID = int(current_user.id)
    found_user = User.query.filter_by(id = uID).delete()
    db.session.commit()
    return redirect("/")


# CRUDI Instructors Controller

@app.route("/instructors", methods=['GET', 'POST'])
def all_instructors():
    allInstructors = Instructor.query.all()
    return render_template("instructors.html", instructors = allInstructors)

@app.route("/instructors/create", methods=["POST"])
def create_instructor():
    fname = request.form.get('fname', "")
    lname = request.form.get('lname', "")
    bio = request.form.get('bio', "")
    picture = request.form.get('picture', "")
    category = request.form.get('category', "")
    video = request.form.get('video', "")
    years_of_experience = request.form.get('years_of_experience', "")
    location = request.form.get('location', "")
    #username = request.form.get('username', "")
    #password = request.form.get('password', "")


    newInstructor = Instructor(fname, lname, bio, picture, category, video, years_of_experience, location, current_user)#username, password
    db.session.add(newInstructor)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/instructors/<id>")
def get_instructor(id):
    instructor = Instructor.query.get( int(id) )
    return render_template("instructor.html", instructor = instructor)

@app.route("/instructors/edit", methods=["GET", "POST"])
def edit_instructor(id):
    instructor = Instructor.query.get(id)

    if request == "POST":
        instructor.fname = request.form.get('fname', "")
        instructor.lname = request.form.get('lname', "")
        instructor.bio = request.form.get('bio', "")
        instructor.picture = request.form.get('picture', "")
        instructor.category = request.form.get('category', "")
        instructor.video = request.form.get('video', "")
        instructor.years_of_experience = request.form.get('years_of_experience', "")
        instructor.location = request.form.get('location', "")

        db.session.commit()
        return render_template("instructor.html", instructor = instructor)

    else:
        return render_template("edit_instructor.html", instructor = instructor)

@app.route("/instructors/delete", methods=["POST"])
def delete_instructor(id):

    instructor = Instructor.query.get(int(id))
    db.session.delete(instructor)
    db.session.commit()
    return redirect("instructors")


#CRUDI Booking

 #@app.route("/book")
#def all_bookings():
 #   allBookings = Booking.query.all()
  #  return render_template("bookings.html", bookings = allBookings)

@app.route("/bookings")
def all_bookings():
    allBookings = Booking.query.all()
    return render_template("bookings.html", bookings = allBookings)

@app.route("/bookings/create", methods=["POST"])
@login_required
def create_booking():

    category = request.form.get('category', "")
    date = request.form.get('date', "")
    start_time = request.form.get('start_time', "")
    end_time = request.form.get('end_time', "")
    price = request.form.get('price', "")
    location = request.form.get('location', "")

    newBooking = Booking(category, date, start_time, end_time, price, location, current_user)
    db.session.add(newBooking)
    db.session.commit()

    return redirect("/dashboard")

   # user = User.query.filter_by( username = username, password = password ).first()

#@app.route("/booking/<id>")
#def get_booking(id):
#   booking = Booking.query.get( int(id) )
#    return render_template("booking.html", booking= booking)

@app.route("/booking/<id>/edit", methods=["GET", "POST"])
@login_required
def edit_booking(id):

    booking = Booking.query.get(int(id))

    if request.method == "POST":

        booking.category = request.form.get('category', "")
        booking.date = request.form.get('date', "")
        booking.start_time = request.form.get('start_time', "")
        booking.end_time = request.form.get('end_time', "")
        booking.price = request.form.get('price', "")
        booking.location = request.form.get('location', "")
        db.session.commit()
        return redirect("/dashboard")
    else:
        return render_template("editBooking.html", booking = booking)

@app.route("/booking/<id>/delete", methods=["GET", "POST"])
@login_required
def delete_booking(id):


    bookingID = id
    found_booking = Booking.query.filter_by(id = bookingID).first()
    db.session.delete(found_booking)
    db.session.commit()
    return redirect("/dashboard")


#CRUDI Review

@app.route("/reviews")
def all_reviews():
    allReviews = Review.query.all()
    return render_template("reviews.html", reviews = allReviews)

@app.route("/reviews/<id>/create", methods=["GET","POST"])
@login_required
def create_review(id):

    booking = Booking.query.get(int(id))
    rating = request.form.get('rating', "")
    comments = request.form.get('comments', "")


    newReview = Review(rating, comments, current_user, booking)
    db.session.add(newReview)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/reviews/<id>")
def get_review(id):
    review = Review.query.get( int(id) )
    return render_template("review.html", review  = review )

@app.route("/reviews/<id>/edit", methods=["GET", "POST"])
def edit_review(id):
    review = Review.query.get( int(id) )

    if request == "Post":
        review.rating = request.form.get('rating', "")
        review.comments = request.form.get('comments', "")
        db.session.commit()
        return render_template("review.html", review = review)
    else:
        return render_template("edit_review.html", review = review)

@app.route("/reviews/<id>/delete", methods=["POST"])
def delete_review(id):
    review = Review.query.get( int(id) )
    db.session.delete(review)
    db.session.commit()
    return redirect("reviews")

@app.route("/signmeup")
def signmeup():
    return render_template("signmeup.html")


if __name__ == "__main__":
    app.run()