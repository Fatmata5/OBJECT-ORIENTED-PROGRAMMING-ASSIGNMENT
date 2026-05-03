from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date
import asyncio
import uvicorn


app = FastAPI(title="Limkokwing Library API")


# ---------- Data Models ----------
class Book(BaseModel):
    id: int
    title: str
    author: str
    category: str
    available: bool


class BorrowRequest(BaseModel):
    user_id: str
    book_id: int


class ReturnRequest(BaseModel):
    user_id: str
    book_id: int


# ---------- Database ----------
books_db: Dict[int, Book] = {
    1: Book(id=1, title="Python Programming", author="Abubakarr Sidikie", category="Programming", available=True),
    2: Book(id=2, title="Data Science Handbook", author="Gif Tea", category="Data", available=True),
    3: Book(id=3, title="History of Art", author="Alhaji Cole", category="Art", available=True),
    4: Book(id=4, title="Machine Learning Basics", author="Musa Kamara", category="Programming", available=True),
    5: Book(id=5, title="Web Development", author="Mohamed Vandi", category="Technology", available=True),
}

borrowed_records: Dict[str, Dict[int, date]] = {}  # user_id -> {book_id: borrow_date}


def calculate_fine(borrow_date: date, return_date: date) -> int:
    days_borrowed = (return_date - borrow_date).days
    overdue_days = max(0, days_borrowed - 7)  # 7 days allowed
    return overdue_days * 100  # 100 per day


# ========== 1. SEARCH BOOKS (GET endpoint) ==========
@app.get("/books", response_model=List[Book])
async def search_books(
        title: Optional[str] = Query(None, description="Search by title"),
        author: Optional[str] = Query(None, description="Search by author"),
        category: Optional[str] = Query(None, description="Search by category"),
):
    """Search for books by title, author, or category"""
    await asyncio.sleep(0.1)  # Simulate async database query

    results = list(books_db.values())

    if title:
        results = [b for b in results if title.lower() in b.title.lower()]
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    if category:
        results = [b for b in results if category.lower() in b.category.lower()]

    return results


# ========== 2. BORROW BOOK (POST endpoint) ==========
@app.post("/borrow")
async def borrow_book(request: BorrowRequest):
    """Borrow a book from the library"""
    await asyncio.sleep(0.1)

    # Check if book exists
    book = books_db.get(request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if book is available
    if not book.available:
        raise HTTPException(status_code=400, detail="Book is already borrowed")

    # Update book availability
    book.available = False
    books_db[request.book_id] = book

    # Record borrowing
    if request.user_id not in borrowed_records:
        borrowed_records[request.user_id] = {}
    borrowed_records[request.user_id][request.book_id] = date.today()

    due_date = date.today()
    return {
        "message": "Book borrowed successfully",
        "user_id": request.user_id,
        "book_id": request.book_id,
        "book_title": book.title,
        "due_date": str(due_date),
        "return_by": str(date.today().replace(day=date.today().day + 7))
    }


# ========== 3. RETURN BOOK (POST endpoint) ==========
@app.post("/return")
async def return_book(request: ReturnRequest):
    """Return a borrowed book and calculate fine if overdue"""
    await asyncio.sleep(0.1)

    # Check if book exists
    book = books_db.get(request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if user borrowed this book
    user_borrows = borrowed_records.get(request.user_id, {})
    if request.book_id not in user_borrows:
        raise HTTPException(status_code=400, detail="User hasn't borrowed this book")

    # Calculate fine
    borrow_date = user_borrows[request.book_id]
    return_date = date.today()
    fine = calculate_fine(borrow_date, return_date)

    # Make book available again
    book.available = True
    books_db[request.book_id] = book

    # Remove borrowing record
    del borrowed_records[request.user_id][request.book_id]

    return {
        "message": "Book returned successfully",
        "user_id": request.user_id,
        "book_id": request.book_id,
        "book_title": book.title,
        "borrowed_date": str(borrow_date),
        "returned_date": str(return_date),
        "fine": fine,
        "fine_message": f"You owe {fine} Leones" if fine > 0 else "No fine, returned on time"
    }


# ========== 4. TRACK OVERDUE BOOKS & FINES (GET endpoint) ==========
@app.get("/users/{user_id}/overdue")
async def track_overdue(user_id: str):
    """Track overdue books and total fines for a specific user"""
    await asyncio.sleep(0.1)

    user_borrows = borrowed_records.get(user_id, {})
    overdue_books = []
    total_fine = 0

    for book_id, borrow_date in user_borrows.items():
        days_borrowed = (date.today() - borrow_date).days
        days_overdue = max(0, days_borrowed - 7)

        if days_overdue > 0:
            fine = days_overdue * 100
            total_fine += fine

            book = books_db.get(book_id)
            overdue_books.append({
                "book_id": book_id,
                "book_title": book.title if book else "Unknown",
                "borrowed_date": str(borrow_date),
                "days_overdue": days_overdue,
                "fine": fine
            })

    return {
        "user_id": user_id,
        "overdue_books": overdue_books,
        "total_fine": total_fine,
        "message": f"You owe {total_fine} Leones" if total_fine > 0 else "No overdue books"
    }


# ========== 5. SUPPORT: GET ALL BORROWED BOOKS (GET endpoint) ==========
@app.get("/users/{user_id}/borrowed")
async def get_user_borrowed_books(user_id: str):
    """Get all currently borrowed books by a user"""
    user_borrows = borrowed_records.get(user_id, {})

    borrowed_list = []
    for book_id, borrow_date in user_borrows.items():
        book = books_db.get(book_id)
        if book:
            borrowed_list.append({
                "book_id": book_id,
                "title": book.title,
                "author": book.author,
                "borrowed_date": str(borrow_date),
                "due_date": str(borrow_date.replace(day=borrow_date.day + 7))
            })

    return {
        "user_id": user_id,
        "borrowed_books": borrowed_list,
        "total_borrowed": len(borrowed_list)
    }


# ========== Run Server ==========
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)