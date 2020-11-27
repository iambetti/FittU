from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment, Bundle
import hashlib

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "sasjdn214jnxc2mf039"
assets = Environment(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

js = Bundle('./javascript/script.js',
            output='gen/scripts.js')
assets.register('js_all', js)

css = Bundle('./css/styles.css',
            output='gen/styles.css')
assets.register('css_all', css)

class User( db.Model ):
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


    def __init__(self, fname, lname, bio, picture, username, password):
        self.fname = fname
        self.lname = lname
        self.bio = bio
        self.picture = picture
        self.username = username
        self.password = password

class Instructor( db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    bio = db.Column(db.Text())
    picture = db.Column(db.String(100))
    category = db.Column(db.String(100))
    video = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    location = db.Column(db.String(100))

    # relationships
    booking = db.relationship( "Booking", backref="instructor" )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



    def __init__(self, fname, lname, bio, picture, category, video, years_of_experience, location, booking, user):
        self.fname = fname
        self.lname = lname
        self.bio = bio
        self.picture = picture
        self.category = category
        self.video = video
        self.years_of_experience = years_of_experience
        self.location = location
        self.booking = booking
        self.user = user

class Booking( db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100))
    start_time = db.Column(db.String(100))
    end_time = db.Column(db.Text())
    price= db.Column(db.String(100))
    location = db.Column(db.String(100)) # added "location", not on diagram

    # relationships
    review = db.relationship( "Review", backref="booking" )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))


    def __init__(self, date, start_time, end_time, price, location, user, instructor):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.price = price
        self.location = location
        self.user = user
        self.instructor = instructor

class Review( db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text()) # I also added this, to keep review as an Integer, and optional comments about the review.
                                     #though I am not sure if they need to be separate.

    # relationships
    booking = db.relationship( "Booking", backref="review" )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

    def __init__(self, rating, comments, user, booking):

        self.rating = rating
        self.comments = comments
        self.user = user
        self.booking = booking


# Main Routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == "Post":
        username = request.form.get("username", "get")
        password = request.form.get("password", "get")

        user = User.query.filter_by( username = username, password = password ).first()

        if user is not None:
            session[ 'username' ] = username

            return redirect("dashboard.html")
        else:
            return redirect("/login")

    else:
        return render_template("login.html")

@app.route("/signup")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    if checkLogin():

        user = User.query.filter_by( username = session[ 'username' ] ).first()
        return render_template("dashboard", user = user)

def checkLogin():
    if 'user' in session:
        return True
    else:
        return redirect("/login")

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

    return redirect("/users/")

@app.route("/users/<id>")
def get_user(id):
    user = User.query.get( int(id) )
    return render_template("user.html", user = user)

@app.route("/users/<id>/edit", methods=["GET", "POST"])
def edit_user(id):
    user = User.query.get( int(id) )

    if request == "Post":
        user.fname = request.form.get('fname', "")
        user.lname = request.form.get('lname', "")
        user.bio = request.form.get('bio', "")
        user.picture = request.form.get('picture', "")
        user.password = request.form.get('password', "")
        db.session.commit()
        return render_template("user.html", user = user)
    else:
        return render_template("edit_user.html", user = user)

@app.route("/users/<id>/delete", methods=["POST"])
def delete_user(id):
    user = User.query.get( int(id) )
    db.session.delete(user)
    db.session.commit()
    return redirect("users")


# CRUDI Instructors Controller

@app.route("/instructors")
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

    newInstructor = Instructor(fname, lname, bio, picture, category, video, years_of_experience, location)
    db.session.add(newInstructor)
    db.session.commit()

    return redirect("/instructors/")

@app.route("/instructors/<id>")
def get_instructor(id):
    instructor = Instructor.query.get( int(id) )
    return render_template("instructor.html", instructor = instructor)

@app.route("/instructors/<id>/edit", methods=["GET", "POST"])
def edit_instructor(id):
    instructor = Instructor.query.get( int(id) )

    if request == "Post":
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

@app.route("/instructors/<id>/delete", methods=["POST"])
def delete_instructor(id):
    instructor = Instructor.query.get( int(id) )
    db.session.delete(instructor)
    db.session.commit()
    return redirect("instructors")


#CRUDI Booking

@app.route("/book")
def all_bookings():
    allBookings = Booking.query.all()
    return render_template("bookings.html", bookings = allBookings)

@app.route("/bookings/create", methods=["POST"])
def create_booking():
    date = request.form.get('date', "")
    start_time = request.form.get('start_time', "")
    end_time = request.form.get('end_time', "")
    price = request.form.get('price', "")
    location = request.form.get('location', "")

    newBooking = Booking(date, start_time, end_time, price, location)
    db.session.add(newBooking)
    db.session.commit()

    return redirect("/book/")

@app.route("/booking/<id>")
def get_booking(id):
    booking = Booking.query.get( int(id) )
    return render_template("booking.html", booking= booking)

@app.route("/booking/<id>/edit", methods=["GET", "POST"])
def edit_booking(id):
    booking = Booking.query.get( int(id) )

    if request == "Post":
        booking.date = request.form.get('date', "")
        booking.start_time = request.form.get('start_time', "")
        booking.end_time = request.form.get('end_time', "")
        booking.price = request.form.get('price', "")
        booking.location = request.form.get('location', "")
        db.session.commit()
        return render_template("booking.html", booking = booking)
    else:
        return render_template("edit_booking.html", booking = booking)

@app.route("/bookings/<id>/delete", methods=["POST"])
def delete_booking(id):
    booking = Booking.query.get( int(id) )
    db.session.delete(booking)
    db.session.commit()
    return redirect("book")


#CRUDI Review

@app.route("/reviews")
def all_reviews():
    allReviews = Review.query.all()
    return render_template("reviews.html", reviews = allReviews)

@app.route("/reviews/create", methods=["POST"])
def create_review():
    rating = request.form.get('rating', "")
    comments = request.form.get('comments', "")

    newReview = Review(rating, comments)
    db.session.add(newReview)
    db.session.commit()

    return redirect("/reviews/")

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




if __name__ == "__main__":
    app.run()