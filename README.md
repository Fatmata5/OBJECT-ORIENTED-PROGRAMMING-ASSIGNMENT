 Limkokwing Library API

A basic digital library management system API that allows users to search, borrow, return books, and track overdue fines. Built with FastAPI and asynchronous Python.

 Features

-  Search books by title, author, or category
-  Borrow books with automatic due date tracking
-  Return books with automated fine calculation
-  Track overdue books and calculate fines (100 Leones/day after 7 days)
-  View all borrowed books for any user
-  Async support for handling multiple users simultaneously
-  Type annotations for better code clarity and IDE support

 Technologies Used

- Python 3.8+
- FastAPI
- Uvicorn (ASGI server)
- Pydantic for data validation
- Asyncio for concurrent operations

 API Endpoints

| Method | Endpoint | Description |
| GET | `/books` | Search all books or filter by title/author/category |
| POST | `/borrow` | Borrow a book from the library |
| POST | `/return` | Return a borrowed book and calculate fines |
| GET | `/users/{user_id}/overdue` | Track overdue books and fines for a user |
| GET | `/users/{user_id}/borrowed` | Get all currently borrowed books by a user |

 Installation & Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/Limkokwing-Library-API.git
cd Limkokwing-Library-API
