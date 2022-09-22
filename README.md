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
        VERIFICATION_CODE_VALIDITY_IN_MINUTES = 10 # any integer value between [1 to 60]

        CURRENCY = '$' # your local currency
        CHECK_DELIVERABILITY = False
        # If set to `True`, upload all pincodes in the database where
        # you deliver your products.
        # optionally, you can also add products that are not deliverable at that location

        TIME_ZONE = 'UTC'
        USE_TZ = True

        'context_processors': [
                ...
                'store.context_processors.site_defaults',
        ],

### 07. To redirect users to "store" homepage use any of the following -
        - <a href="{% url 'store:homepage' %}">Store</a>
        - <a href='/store/'>Store</a>

### 08. When `AUTHENTICATION_DEBUG = TRUE`

        - Live EMAILS will not be sent and verification codes, if any, will be displayed in the console.

### 09. Product images are stored in `BASE_DIR/images/product-images/` if not other location is specified.

        upload_to="images/product-images/"

### 10. Check [Demo Website](https://django-ecom-store.herokuapp.com/) and [associated Github](https://github.com/parisrvs/django-store) code for more information.

### 11. Check information on authentication app [here](https://github.com/parisrvs/django-user-login)