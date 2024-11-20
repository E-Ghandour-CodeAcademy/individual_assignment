# Book Library

A web application for searching books, managing user subscriptions, and viewing subscribed books.

## Description

This project is a web application built with Flask and MongoDB. It allows users to search for books, subscribe to updates on specific books, and view their subscriptions. The application includes user authentication to manage user sessions and subscriptions.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/E-Ghandour-CodeAcademy/individual_assignment.git
    cd book-library
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    venv\Scripts\activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up MongoDB:
    - Ensure MongoDB is installed and running on your machine.
    - Update the `MONGO_URI` in `app.py` if necessary.

5. Run the application:
    ```bash
    flask run
    ```

## Usage

1. Open your web browser and go to `http://127.0.0.1:5000/`.
2. Register a new account or log in if you already have an account.
3. Use the search functionality to find books by title or author.
4. Subscribe to updates on specific books.
5. View your subscribed books on the dashboard.

## Features

- User registration and login
- Book search using the Open Library API
- Subscribe to updates on specific books
- View subscribed books on the dashboard
- User authentication and session management

## References 

This project uses the [Open Library API](https://openlibrary.org/developers/api) to fetch book data. You can find more information about the API and its usage [here](https://openlibrary.org/dev/docs/api/books).

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request
