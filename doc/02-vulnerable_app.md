# 1. git branch

```
git checkout -b vulnerable-app
```

# 2. app.py:

```python
from flask import Flask, request, redirect, url_for, render_template, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database with vulnerable tables
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create users table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT)''')
    
    # Insert some db.sqlite3 users if they don't exist
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 ('admin', 'admin123'))
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 ('user1', 'password1'))
    except sqlite3.IntegrityError:
        pass  # Users already exist
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def list_view():
    return render_template('listview.html')

def sanitize_username(username):
    if '--' in username:
        return username.split('--')[0].strip()
    return username

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # This is the vulnerable query - susceptible to SQL injection
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        c.execute(query)
        
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user'] = sanitize_username(username)
            return redirect(url_for('list_view'))
        else:
            return render_template('accounts/login.html', 
                                message="Invalid credentials!",
                                success=False)
    
    return render_template('accounts/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Vulnerable SQL query - susceptible to SQL injection
        try:
            c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            conn.commit()
            conn.close()
            session['user'] = username
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('accounts/login.html', 
                                message="Username already exists!",
                                success=False)
    
    return render_template('accounts/login.html', register=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
```

```
git status
git add .
git status
git commit -m "app.py"
```

# 3. templates

src/templates/_base.html:

```html
<!doctype html>
<html lang="en">
<head>
    {% block head %}
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='assets/img/fav.png') }}">
    <title>{% block title %}Bodegaa{% endblock %}</title>

    <link href="{{ url_for('static', filename='assets/vendor/bootstrap/css/bootstrap.min.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='assets/vendor/icons/icofont.min.css') }}" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <link href="{{ url_for('static', filename='assets/css/style.css') }}" rel="stylesheet">
    {% endblock %}
</head>
<body class="bg-light">
    {% include '_header.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include '_footer.html' %}
    {% include '_modals.html' %}

    <script src="{{ url_for('static', filename='assets/vendor/jquery/jquery.min.js') }}"></script>
    <script src="{{ url_for('static', filename='assets/vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='assets/js/custom.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

src/templates/_header.html:

```html
<nav class="navbar navbar-expand-lg navbar-light bg-white sticky-top shadow-sm osahan-header py-0">
    <div class="container">
        <a class="navbar-brand me-0 me-lg-3 me-md-3" href="{{ url_for('login') }}">
            <img src="{{ url_for('static', filename='assets/img/logo.svg') }}" alt="#" class="img-fluid d-none d-md-block">
            <img src="{{ url_for('static', filename='assets/img/fav.png') }}" alt="#" class="d-block d-md-none d-lg-none img-fluid">
        </a>
        <a href="#"
            class="ms-3 text-left d-flex text-dark align-items-center gap-2 text-decoration-none bg-white border-0 me-auto"
            data-bs-toggle="modal" data-bs-target="#add-delivery-location">
            <i class="bi bi-geo-alt-fill fs-5 text-success"></i>
            <span>
                <b>Delivery in 15 minutes</b>
                <small class="text-success d-block">Sant Pura, Industrial Area...<i
                        class="bi bi-arrow-right-circle-fill ms-1"></i></small>
            </span>
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav ms-auto me-3 top-link">
                <li class="nav-item dropdown">
                    <a class="nav-link" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        Shop Pages<i class="bi bi-chevron-down small ms-1"></i>
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="search.html">Search</a></li>
                        <li><a class="dropdown-item" href="listing.html">Listing</a></li>
                        <li><a class="dropdown-item" href="listing-detail.html">Listing Detail</a></li>
                        <li><a class="dropdown-item" href="product-detail.html">Product Detail</a></li>
                        <li><a class="dropdown-item" href="cart.html">Cart / Checkout</a></li>
                        <li><a class="dropdown-item" href="success-order.html">Success Order</a></li>
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        Profile<i class="bi bi-chevron-down small ms-1"></i>
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="profile.html">Orders List</a></li>
                        <li><a class="dropdown-item" href="profile.html">Addresses</a></li>
                        <li><a class="dropdown-item" href="profile.html">Manage Payments</a></li>
                        <li><a class="dropdown-item" href="profile.html">Bodegaa Cash</a></li>
                        <li><a class="dropdown-item" href="profile.html">Support / Help</a></li>
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        Pick up & Drop<i class="bi bi-chevron-down small ms-1"></i>
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="packages.html">Packages From</a></li>
                        <li><a class="dropdown-item" href="packages-payment.html">Packages Checkout</a></li>
                        <li><a class="dropdown-item" href="success-send.html">Successfully Send</a></li>
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        Extra Page<i class="bi bi-chevron-down small ms-1"></i>
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="about.html">About us</a></li>
                        <li><a class="dropdown-item" href="jobs.html">Jobs</a></li>
                        <li><a class="dropdown-item" href="contact.html">Contact Us</a></li>
                        <li><a class="dropdown-item" href="cupons.html">Cupons</a></li>
                    </ul>
                </li>
            </ul>
            <div class="d-flex align-items-center gap-2">
                <a href="search.html" class="btn btn-light position-relative rounded-pill rounded-icon">
                    <i class="icofont-search"></i>
                </a>
                <a href="cart.html" class="btn btn-light position-relative rounded-pill rounded-icon">
                    <i class="bi bi-cart3"></i>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning">5
                        <span class="visually-hidden">Cart</span>
                    </span>
                </a>

                {% if 'user' in session %}
                <div class="dropdown">
                    <a class="btn btn-success rounded-pill px-3 text-uppercase ms-2 dropdown-toggle" href="#" role="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                        {{ session['user'] }}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                        <li><a class="dropdown-item" href="profile.html">پروفایل</a></li>
                        <li><a class="dropdown-item" href="orders.html">سفارشات</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="{{ url_for('logout') }}">خروج</a></li>
                    </ul>
                </div>
                {% else %}
                <a class="btn btn-success rounded-pill px-3 text-uppercase ms-2" data-bs-toggle="modal"
                    href="{{ url_for('login') }}" role="button">ورود / ثبت نام</a>
                {% endif %}
            </div>
        </div>
    </div>
</nav>
```

src/templates/_footer.html:

```html
<footer class="bg-footer py-5 d-none d-md-block">
    <div class="container">
        <div class="row mb-5">
            <div class="col-12 text-white">
                <h6 class="fw-bold mb-4">You can't stop time, but you can save it</h6>
                <p class="text-white-50 m-0">Living in the city, there is never enough time to shop for groceries,
                    pick-up supplies, grab food and wade through traffic on the way back home. How about we take care of
                    all of the above for you? What if we can give you all that time back? Send packages across the city
                    and get everything from food, groceries, medicines and pet supplies delivered right to your
                    doorstep. From any store to your door, just make a list and we'll make it disappear. Just Bodegaa
                    It!</p>
            </div>
        </div>
        <hr class="text-white">
        <div class="row text-white mt-5">
            <div class="col-md-4 col-12">
                <div><img src="assets/img/fav.png" alt="" class="img-fluid footer-logo"></div>
            </div>
            <div class="col-md-2 col-6">
                <h6 class="text-uppercase mb-4 fw-bold">Bodegaa</h6>
                <ul class="list-unstyled d-grid gap-2 text-decoration-none">
                    <li><a class="text-decoration-none text-white-50" href="about.html">About us</a></li>
                    <li><a class="text-decoration-none text-white-50" href="jobs.html">Jobs</a></li>
                    <li><a class="text-decoration-none text-white-50" href="contact.html">Contact Us</a></li>
                    <li><a class="text-decoration-none text-white-50" href="cupons.html">Cupons</a></li>
                </ul>
            </div>
            <div class="col-md-2 col-6">
                <h6 class="text-uppercase mb-4 fw-bold">My Profile</h6>
                <ul class="list-unstyled d-grid gap-2">
                    <li><a class="text-decoration-none text-white-50" href="profile.html">Orders List</a></li>
                    <li><a class="text-decoration-none text-white-50" href="profile.html">Addresses</a></li>
                    <li><a class="text-decoration-none text-white-50" href="profile.html">Manage Payments</a></li>
                    <li><a class="text-decoration-none text-white-50" href="profile.html">Bodegaa Cash</a></li>
                    <li><a class="text-decoration-none text-white-50" href="profile.html">Support / Help</a></li>
                </ul>
            </div>
            <div class="col-md-2 col-6">
                <h6 class="text-uppercase mb-4 fw-bold">Shop Pages</h6>
                <ul class="list-unstyled d-grid gap-2">
                    <li><a class="text-decoration-none text-white-50" href="search.html">Search</a></li>
                    <li><a class="text-decoration-none text-white-50" href="listing.html">Listing</a></li>
                    <li><a class="text-decoration-none text-white-50" href="listing-detail.html">Listing Detail</a></li>
                    <li><a class="text-decoration-none text-white-50" href="product-detail.html">Product Detail</a></li>
                    <li><a class="text-decoration-none text-white-50" href="cart.html">Cart / Checkout</a></li>
                    <li><a class="text-decoration-none text-white-50" href="success-order.html">Success Order</a></li>
                </ul>
            </div>
            <div class="col-md-2 col-6">
                <h6 class="text-uppercase mb-4 fw-bold">get in touch</h6>
                <ul class="list-unstyled d-grid gap-2">
                    <li><a class="text-decoration-none text-white-50" href="#">Email</a></li>
                    <li><a class="text-decoration-none text-white-50" href="#">Twitter</a></li>
                    <li><a class="text-decoration-none text-white-50" href="#">Facebook</a></li>
                    <li><a class="text-decoration-none text-white-50" href="#">Instagram</a></li>
                    <li><a class="text-decoration-none text-white-50" href="#">Linkedin</a></li>
                </ul>
            </div>
        </div>
    </div>
</footer>
```

src/templates/_modals.html:

```html
<div class="modal fade" id="exampleModalToggle" aria-hidden="true" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered login-popup-main">
        <div class="modal-content border-0 shadow overflow-hidden rounded">
            <div class="modal-body p-0">
                <div class="login-popup">
                    <button type="button" class="btn-close position-absolute" data-bs-dismiss="modal"
                        aria-label="Close"></button>
                    <div class="row g-0">
                        <div class="d-none d-md-flex col-md-4 col-lg-4 bg-image1"></div>
                        <div class="col-md-8 col-lg-8 py-lg-5">
                            <div class="login p-5">
                                <div class="mb-4 pb-2">
                                    <h5 class="mb-2 fw-bold">Hey! what's your number?</h5>
                                    <p class="text-muted mb-0">Please login with this number the next time you sign-in
                                    </p>
                                </div>
                                <form>
                                    <div class="input-group bg-white border rounded mb-3 p-2">
                                        <span class="input-group-text bg-white border-0"><i
                                                class="bi bi-phone pe-2"></i> +91 </span>
                                        <input type="text" class="form-control bg-white border-0 ps-0"
                                            placeholder="Enter phone number">
                                    </div>
                                    <div class="form-check">
                                        <input type="checkbox" class="form-check-input" id="exampleCheck1">
                                        <label class="form-check-label small text-muted border-end pe-1"
                                            for="exampleCheck1">I accept the Terms of use & Privacy Policy</label>
                                        <a href="#" class="text-decoration-none text-success small">View T&C <i
                                                class="bi bi-chevron-right"></i></a>
                                    </div>
                                </form>
                                <button class="btn btn-success btn-lg py-3 px-4 text-uppercase w-100 mt-4"
                                    data-bs-target="#exampleModalToggle2" data-bs-toggle="modal">Get OTP <i
                                        class="bi bi-arrow-right ms-2"></i></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="exampleModalToggle2" aria-hidden="true" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered login-popup-main">
        <div class="modal-content border-0 shadow overflow-hidden rounded">
            <div class="modal-body p-0">
                <div class="login-popup">
                    <button type="button" class="btn-close position-absolute" data-bs-dismiss="modal"
                        aria-label="Close"></button>
                    <div class="row g-0">
                        <div class="d-none d-md-flex col-md-4 col-lg-4 bg-image1"></div>
                        <div class="col-md-8 col-lg-8 py-lg-5">
                            <div class="login p-5">
                                <div class="mb-4 pb-2">
                                    <h5 class="mb-2 fw-bold">Confirm your number</h5>
                                    <p class="text-muted mb-0">Enter the 4 digit OTP we've sent by SMS to 123456-78909
                                        <a data-bs-target="#exampleModalToggle2" data-bs-toggle="modal"
                                            class="text-success text-decoration-none" href="#"><i
                                                class="bi bi-pencil-square"></i> Edit</a>
                                    </p>
                                </div>
                                <form>
                                    <div class="d-flex gap-3 text-center">
                                        <div class="input-group bg-white border rounded mb-3 p-2">
                                            <input type="text" value="1"
                                                class="form-control bg-white border-0 text-center">
                                        </div>
                                        <div class="input-group bg-white border rounded mb-3 p-2">
                                            <input type="text" value="3"
                                                class="form-control bg-white border-0 text-center">
                                        </div>
                                        <div class="input-group bg-white border rounded mb-3 p-2">
                                            <input type="text" value="1"
                                                class="form-control bg-white border-0 text-center">
                                        </div>
                                        <div class="input-group bg-white border rounded mb-3 p-2">
                                            <input type="text" value="3"
                                                class="form-control bg-white border-0 text-center">
                                        </div>
                                    </div>
                                    <div class="form-check ps-0">
                                        <label class="small text-muted">Resend OTP in 0:55</label>
                                    </div>
                                </form>
                                <button class="btn btn-success btn-lg py-3 px-4 text-uppercase w-100 mt-4"
                                    data-bs-target="#exampleModalToggle3" data-bs-toggle="modal">Get OTP <i
                                        class="bi bi-arrow-right ms-2"></i></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="exampleModalToggle3" aria-hidden="true" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
            <div class="modal-header p-4 border-0">
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4">
                <div class="text-center mb-5 pb-2">
                    <div class="mb-3"><img src="{{ url_for('static', filename='assets/img/login2.png') }}" class="col-6 mx-auto" alt="">

                    </div>
                    <h5 class="mb-2">Have a Referral or Invite Code?</h5>
                    <p class="text-muted">Use code GET50 to earn 50 Bodegaa Cash</p>
                </div>
                <form>
                    <label class="form-label">Enter your referral/invite code</label>
                    <div class="input-group mb-2 border rounded-3 p-1">
                        <span class="input-group-text border-0 bg-white"><i
                                class="bi bi bi-ticket-perforated  text-secondary"></i></span>
                        <input type="text" class="form-control border-0 bg-white ps-1" placeholder="Enter the code">
                    </div>
                </form>
            </div>
            <div class="modal-footer px-4 pb-4 pt-0 border-0">
                <button class="btn btn-success btn-lg py-3 px-4 text-uppercase  w-100 m-0"
                    data-bs-target="#exampleModalToggle4" data-bs-toggle="modal">Claim Bodegaa Cash</button>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="exampleModalToggle4" aria-hidden="true" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
            <div class="modal-header p-4 border-0">
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4">
                <div class="row justify-content-center">
                    <div class="col-10 text-center">
                        <div class="mb-5"><img src="{{ url_for('static', filename='assets/img/login3.png') }}" alt="" class="col-6 mx-auto">
                        </div>
                        <div class="my-3">
                            <h5 class="fw-bold">You got &#8377;50.0 Bodegaa Cash!</h5>
                            <p class="text-muted h6">use this Bodegaa Cash to save on your next orders</p>
                        </div>
                        <div class="my-4">
                            <p class="small text-muted mb-0">Your Bodegaa Cash will expire in</p>
                            <div class="h5 text-success">6d:23h</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer px-4 pb-4 pt-0 border-0">
                <a href="index.html" class="btn btn-success btn-lg py-3 px-4 text-uppercase w-100 m-0">Tap to order</a>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="add-delivery-location" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
    aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
            <div class="modal-header px-4">
                <h5 class="h6 modal-title fw-bold">Add Your Location</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4">
                <form>
                    <div class="input-group border p-1 overflow-hidden osahan-search-icon shadow-sm rounded mb-3">
                        <span class="input-group-text bg-white border-0"><i class="icofont-search"></i></span>
                        <input type="text" class="form-control bg-white border-0 ps-0"
                            placeholder="Search for area, location name">
                    </div>
                </form>
                <div class="mb-4">
                    <a href="#" data-bs-dismiss="modal" aria-label="Close"
                        class="text-success d-flex gap-2 text-decoration-none fw-bold">
                        <i class="bi bi-compass text-success"></i>
                        <div>Use Current Location</div>
                    </a>
                </div>
                <div class="text-muted text-uppercase small">Search Results</div>
                <div>
                    <div data-bs-dismiss="modal" class="d-flex align-items-center gap-3 border-bottom py-3">
                        <i class="icofont-search h6"></i>
                        <div>
                            <p class="mb-1 fw-bold">Bangalore</p>
                            <p class="text-muted small m-0">Karnataka, India</p>
                        </div>
                    </div>
                    <div data-bs-dismiss="modal" class="d-flex align-items-center gap-3 border-bottom py-3">
                        <i class="icofont-search h6"></i>
                        <div>
                            <p class="mb-1 fw-bold">Bangalore internaltional airport</p>
                            <p class="text-muted small m-0">Karmpegowda.in't Airport, Hunachur, karnataka, India</p>
                        </div>
                    </div>
                    <div data-bs-dismiss="modal" class="d-flex align-items-center gap-3 border-bottom py-3">
                        <i class="icofont-search h6"></i>
                        <div>
                            <p class="mb-1 fw-bold">Railway Station back gate</p>
                            <p class="text-muted small m-0">M.G. Railway Colony, Majestic, Bangaluru, Karnataka.</p>
                        </div>
                    </div>
                    <div data-bs-dismiss="modal" class="d-flex align-items-center gap-3 border-bottom py-3">
                        <i class="icofont-search h6"></i>
                        <div>
                            <p class="mb-1 fw-bold">Bangalore Cant</p>
                            <p class="text-muted small m-0">Cantonent Railway Station Road, Contonment Railway.</p>
                        </div>
                    </div>
                    <div data-bs-dismiss="modal" class="d-flex align-items-center gap-3 py-3">
                        <i class="icofont-search h6"></i>
                        <div>
                            <p class="mb-1 fw-bold">Bangalore Contonement Railway Station</p>
                            <p class="text-muted small m-0">Contonement Railway Quarters, Shivaji nagar.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

src/templates/listview.html

```html
{% extends "_base.html" %}

{% block content %}
<div class="main-banner bg-white pt-4">
    <div class="container">
        <div id="carouselExampleFade" class="carousel slide carousel-fade mb-4" data-bs-ride="carousel">
            <div class="carousel-inner rounded">
                <div class="carousel-item active">
                    <a href="#"><img src="{{ url_for('static', filename='assets/img/banner1.png') }}" class="d-block w-100" alt="..."></a>
                </div>
                <div class="carousel-item">
                    <a href="#"><img src="{{ url_for('static', filename='assets/img/banner2.png') }}" class="d-block w-100" alt="..."></a>
                </div>
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleFade"
                data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleFade"
                data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
            </button>
        </div>
        <div class="row row-cols-2 row-cols-md-4 row-cols-lg-4 g-4">
            <div class="col"><a href="#"><img src="{{ url_for('static', filename='assets/img/l1.png') }}" alt="#"
                        class="img-fluid rounded-3"></a></div>
            <div class="col"><a href="#"><img src="{{ url_for('static', filename='assets/img/l3.png') }}" alt="#"
                        class="img-fluid rounded-3"></a></div>
            <div class="col"><a href="#"><img src="{{ url_for('static', filename='assets/img/l4.png') }}" alt="#"
                        class="img-fluid rounded-3"></a></div>
            <div class="col"><a href="#"><img src="{{ url_for('static', filename='assets/img/l2.png') }}" alt="#"
                        class="img-fluid rounded-3"></a></div>
        </div>
    </div>
</div>

<div class="bg-white">
    <div class="container py-5">
        <div class="d-flex align-items-center justify-content-between mb-4">
            <h5 class="mb-0 fw-bold">Explore our Range of Products</h5>
            <a class="text-decoration-none text-success" href="#">View All <i
                    class="bi bi-arrow-right-circle-fill ms-1"></i></a>
        </div>
        <div class="row row-cols-2 row-cols-md-4 row-cols-lg-6 g-4 homepage-products-range">
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/1.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Fresh Milk</h6>
                        <p class="card-text small text-success">128 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/2.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Vegetables</h6>
                        <p class="card-text small text-success">345 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/3.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Fruits</h6>
                        <p class="card-text small text-success">233 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/4.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Bakery &amp; Dairy</h6>
                        <p class="card-text small text-success">4445 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/5.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Beverages</h6>
                        <p class="card-text small text-success">234 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/6.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Breakfast, Snacks</h6>
                        <p class="card-text small text-success">83 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/7.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Oils &amp; Masalas</h6>
                        <p class="card-text small text-success">564 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/8.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Pooja Essentials</h6>
                        <p class="card-text small text-success">233 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/9.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Baby Care</h6>
                        <p class="card-text small text-success">677 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/10.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Beauty &amp; Hygiene</h6>
                        <p class="card-text small text-success">456 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/11.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Cleaning</h6>
                        <p class="card-text small text-success">23 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
            <div class="col">
                <div class="text-center position-relative border rounded pb-4">
                    <img src="{{ url_for('static', filename='assets/img/12.png') }}" class="img-fluid rounded-3 p-3" alt="...">
                    <div class="listing-card-body pt-0">
                        <h6 class="card-title mb-1 fs-14">Pet Care</h6>
                        <p class="card-text small text-success">866 Items</p>
                    </div>
                    <a href="#" class="stretched-link"></a>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="bg-white">
    <div class="container">
        <div class="row g-4">
            <div class="col-md-3 col-6">
                <a href="#"><img alt="..." src="{{ url_for('static', filename='assets/img/slider1.jpg') }}" class="img-fluid rounded-3"></a>
            </div>
            <div class="col-md-3 col-6">
                <a href="#"><img alt="..." src="{{ url_for('static', filename='assets/img/slider2.jpg') }}" class="img-fluid rounded-3"></a>
            </div>
            <div class="col-md-3 col-6">
                <a href="#"><img alt="..." src="{{ url_for('static', filename='assets/img/slider3.jpg') }}" class="img-fluid rounded-3"></a>
            </div>
            <div class="col-md-3 col-6">
                <a href="#"><img alt="..." src="{{ url_for('static', filename='assets/img/slider4.jpg') }}" class="img-fluid rounded-3"></a>
            </div>
        </div>
    </div>
</div>

<div id="app-section" class="bg-white py-5 mobile-app-section">
    <div class="container">
        <div class="bg-light rounded px-4 pt-4 px-md-4 pt-md-4 px-lg-5 pt-lg-5 pb-0">
            <div class="row justify-content-center align-items-center app-2 px-lg-4">
                <div class="col-md-7 px-lg-5">
                    <div class="text-md-start text-center">
                        <h1 class="fw-bold mb-2 text-dark">Get the Bodegaa app</h1>
                        <div class="m-0 text-muted">We will send you a link, open it on your phone to download the app
                        </div>
                    </div>
                    <div class="my-4 me-lg-5">
                        <div class="input-group bg-white shadow-sm rounded-pill p-2">
                            <span class="input-group-text bg-white border-0"><i class="bi bi-phone pe-2"></i> +91
                            </span>
                            <input type="text" class="form-control bg-white border-0 ps-0 me-1"
                                placeholder="Enter phone number">
                            <button class="btn btn-warning rounded-pill py-2 px-4 border-0" type="button">Send app
                                link</button>
                        </div>
                    </div>
                    <div class="text-md-start text-center mt-5 mt-md-1 pb-md-4 pb-lg-5">
                        <p class="mb-3">Download app from</p>
                        <a href="#/"><img alt="#" src="{{ url_for('static', filename='assets/img/play-store.svg') }}" class="img-fluid mobile-app-icon"></a>
                        <a href="#/"><img alt="#" src="{{ url_for('static', filename='assets/img/app-store.svg') }}" class="img-fluid mobile-app-icon"></a>
                    </div>
                </div>
                <div class="col-md-5 pe-lg-5 mt-3 mt-md-0 mt-lg-0">
                    <img alt="#" src="{{ url_for('static', filename='assets/img/mobile-app.png') }}" class="img-fluid">
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

src/templates/accounts
```html
{% extends "_base.html" %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow-sm border-0 rounded">
                <div class="card-body p-5">
                    {% if message %}
                    <div class="alert alert-{% if success %}success{% else %}danger{% endif %} mb-4">
                        {{ message }}
                    </div>
                    {% endif %}

                    <div class="text-center mb-4">
                        <h4 class="fw-bold">
                            {% if register %}Create your account{% else %}Welcome back{% endif %}
                        </h4>
                        <p class="text-muted">
                            {% if register %}Join Bodegaa today{% else %}Sign in to your Bodegaa account{% endif %}
                        </p>
                    </div>

                    <form method="POST" action="{% if register %}{{ url_for('register') }}{% else %}{{ url_for('login') }}{% endif %}">
                        <div class="mb-3">
                            <label for="loginEmail" class="form-label">Username</label>
                            <div class="input-group">
                                <span class="input-group-text bg-white"><i class="bi bi-person"></i></span>
                                <input type="text" class="form-control" id="loginEmail" name="username" placeholder="Enter username" required>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="loginPassword" class="form-label">Password</label>
                            <div class="input-group">
                                <span class="input-group-text bg-white"><i class="bi bi-lock"></i></span>
                                <input type="password" class="form-control" id="loginPassword" name="password"
                                    placeholder="Enter password" required>
                                <button class="btn btn-outline-secondary" type="button" id="toggleLoginPassword">
                                    <i class="bi bi-eye"></i>
                                </button>
                            </div>
                        </div>

                        {% if not register %}
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="rememberMe">
                                <label class="form-check-label small text-muted" for="rememberMe">
                                    Remember me
                                </label>
                            </div>
                            <a href="forgot-password.html" class="small text-decoration-none text-success">Forgot password?</a>
                        </div>
                        {% endif %}

                        <button type="submit" class="btn btn-success btn-lg py-3 px-4 text-uppercase w-100">
                            {% if register %}Sign Up{% else %}Sign In{% endif %}
                        </button>

                        <div class="text-center mt-4">
                            <p class="text-muted">
                                {% if register %}
                                Already have an account? <a href="{{ url_for('login') }}" class="text-decoration-none text-success fw-bold">Sign in</a>
                                {% else %}
                                Don't have an account? <a href="{{ url_for('register') }}" class="text-decoration-none text-success fw-bold">Sign up</a>
                                {% endif %}
                            </p>
                        </div>

                        {% if not register %}
                        <div class="d-flex align-items-center my-4">
                            <hr class="flex-grow-1">
                            <span class="mx-3 text-muted small">OR</span>
                            <hr class="flex-grow-1">
                        </div>

                        <div class="d-grid gap-3">
                            <button type="button" class="btn btn-outline-secondary py-2 text-uppercase">
                                <i class="bi bi-google me-2"></i> Continue with Google
                            </button>
                            <button type="button" class="btn btn-outline-secondary py-2 text-uppercase">
                                <i class="bi bi-facebook me-2"></i> Continue with Facebook
                            </button>
                        </div>
                        {% endif %}
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

add static files

cd .. or terminal 2

```
git status
git add .
git commit -m "Add _base.html, _footer.html, _header.html, _modals.html listview.html, login.html" 
```

```
python app.py
```

```
git checkout develop
git merge vulnerable-app
```

remove branch:
```
git branch -d vulnerable-app
```

