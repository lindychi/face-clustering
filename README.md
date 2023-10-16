# Face Clustering Project with Flask

This project aims to provide a simple face clustering service. It's a Flask-based application that also offers basic user authentication features.

## Project Structure

The project follows a modular structure:

```
FaceClusteringProject/
├── app/
│   ├── templates/
│   │   └── login.html
│   │   └── register.html
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
├── migrations/
├── tests/
│   └── test_routes.py
├── config.py
├── run.py
└── requirements.txt
```

### File Descriptions

- `requirements.txt`: List of Python packages required for the project.
- `run.py`: Script to run the Flask application.
- `config.py`: Configuration settings for the app.
- `app/__init__.py`: Initializes Flask app and database objects.
- `app/routes.py`: Contains all the routes and view functions.
- `app/models.py`: Contains SQLAlchemy database models.
- `tests/test_routes.py`: Contains test cases for routes.
- `app/templates/`: Contains HTML templates.

## Setup and Running

### Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- Flask-Migrate

### Installation

1. Clone the repository and navigate into the project directory.

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS and Linux
   venv\Scripts\activate  # Windows
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:

   ```bash
   python run.py
   ```

Now, navigate to `http://127.0.0.1:5000/` in your browser to access the application.

## Features

- Face clustering (TBD)
- User registration
- User login

For more details, check the project documentation.

## Contributing

If you want to contribute, feel free to open an issue or create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
