# Django RESTful API for Library Management

This project is a Django-based RESTful API framework designed to manage various aspects of a library business process. It includes models for Book, Payment, Borrowings  allowing users to efficiently handle library-related operations.

## Features

- **Books management:** Ability to manage books in the library. You will always know the number of books. All users c


- **Borrowings management:** Track all borrowed books. You will be able to automatically see who borrowed, how much, and when they must be returned.


- **Payment:** Within the service, it is possible to pay for renting books immediately.


- **Notification:** Automatic reminder to users about their borrowing through the Telegram bot. Users will also receive a message about borrowing with all the necessary information in Telegram


- **Authorization:** JWT authentication

- **Documentation:** by swagger


## Tech Stack

**Core**:
- Django
- Django REST Framework (DRF)
***
**DataBase**: PostgreSQL
***
**Containerization platform:** Docker


## Quick Start

(!!Make sure Python3 is installed on your system!!)

To get started with the project, follow these steps:

1. Clone the repository to your local machine:

        git clone https://github.com/Serejka21/DRF_APILibrary.git

2. Navigate to the project directory:

        cd config

3. Set up a virtual environment:

        python -m venv env
        source env/bin/activate  # For Linux/Mac
        env\Scripts\activate  # For Windows

4. Install the required dependencies:

        pip install -r requirements.txt

5. Apply database migrations:

        python manage.py migrate

6. Start the development server:

        python manage.py runserver

7. Access the API at http://localhost:8000/ and explore the available endpoints.

**P.S. project doesn't work on Windows without Docker. Because Celery is used in the project**

***

**Available main endpoints:**

        /api/library/borrowings/

        /api/library/books/

        /api/library/payments/

        /api/library/token/

        /api/library/register/

        /admin/


For detailed API documentation and endpoint usage, refer to the API documentation available in the project or access when the server is running.

        api/library/schema/swagger-ui/

## Run with docker

        docker-compose build
        ducker-compose up

## Default user for testing

- **Email:** admin@admin.com
- **Password:** 1qazcde3

## User endpoints:

I used JWT in this project to manage accesses

- create user:

        api/library/user/register

- get access token:

        api/library/user/token

- verify access token:

        api/library/user/token/verify

- refresh token:

        api/library/user/token/refresh

- manage user:

        api/library/user/me
