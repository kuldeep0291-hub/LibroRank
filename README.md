# LibroRank

LibroRank is a Flask web application that ranks books from OpenLibrary and Google Books based on popularity, correctness, and relevance to a given topic and user type.

## Features

- Search books by topic using OpenLibrary or Google Books APIs
- Rank results using a scoring formula combining popularity, correctness, and relevance
- Filter results by user type: Beginner, Student, or Advanced

## Project Structure

```
LibroRank/
├── app.py              # Flask application and ranking logic
└── templates/
    └── index.html      # Main HTML template
```

## Running the App

```bash
pip install flask requests
python app.py
```

Then open `http://localhost:5000` in your browser.
