# Store
An E-Commerce store for Django Application

### 01. To install and use the package, use:

        pip install django-user-login
        pip install django-ecom-store

Instructions

### 02.	Add "authentication" and "store" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = [
            ...
            'authentication',
            'store',
        ]

### 03.	Include the authentication and store URLconfs in your project urls.py like this:

        path('authentication/', include('authentication.urls')),
        path('store/', include('store.urls')),

### 04.	Run `python manage.py migrate` (you'll need the Admin app enabled).

### 05.	The App requires [Django Sessions](https://docs.djangoproject.com/en/4.0/topics/http/sessions/#enabling-sessions)

### 06. In your settings.py file include the following:

        SITE_TITLE = 'your-site-title'
        LOGIN_URL = '/authentication/'
        EMAIL_HOST = 'email-host'
        EMAIL_PORT = email-port
        EMAIL_HOST_USER = 'emaill-address'
        EMAIL_HOST_PASSWORD = 'email-password
        EMAIL_USE_TLS = True
        AUTHENTICATION_DEBUG=False

        CURRENCY = 'Rs.'
        # Integer value
        DELIVERY_TIME_IN_HOURS = 24
        # Integer greater than or equal to 1, must correspond with DELIVERY_TIME_IN_HOURS
        DELIVERY_TIME_IN_DAYS = 1

        'context_processors': [
                ...
                'store.context_processors.site_defaults',
        ],

### 07. Tp redirect users to "store" homepage use any of the following -
        - <a href="{% url 'store:homepage' %}">Store</a>
        - <a href='/store/'>Login</a>

### 08. When `AUTHENTICATION_DEBUG = TRUE`

        - Live EMAILS will not be sent and verification codes, if any, will be displayed in the console.
        - No password validation will happen.

### 09. When a user closes their account, the app will not delete the User account but set `is_active` to `False` in [User Model](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#django.contrib.auth.models.User.is_active)

### 10. Layout template refers to `favicon.ico` in `static` folder in the root directory.

        <link rel="icon" type="image/x-icon" href="{% static 'favicon.ico' %}">

### 11. Product images are stored in `BASE_DIR/static/images/product-images`

        upload_to="static/images/product-images/"

### 12. Check [Demo Website](https://django-ecom-store.herokuapp.com/) and [Github](https://github.com/parisrvs/django-store) code for more information.