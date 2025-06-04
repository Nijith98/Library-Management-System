import frappe
from frappe import _
import json
from frappe.utils import nowdate
from werkzeug.exceptions import BadRequest


# Return list of available books filtered by optional title and ISBN
@frappe.whitelist(allow_guest=True)
def list_available_books(title=None, isbn=None):
    try:
        filters = {
            "available_quantity": [">", 0]
        }
        if title:
            filters["title"] = ["like", f"%{title}%"]
        if isbn:
            filters["isbn"] = ["like", f"%{isbn}%"]

        # Fetch all books with available_quantity > 0, optionally filtered by title or ISBN
        books = frappe.get_all(
            "Book",
            filters=filters,
            fields=["name", "title", "isbn", "authors", "available_quantity"]
        )
        return books

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in list_available_books")
        return {
            "status": "error",
            "message": "Failed to fetch available books.",
            "error": str(e)
        }


# Fetch all loan records of a specific library member
@frappe.whitelist(allow_guest=True)
def member_loan_history(member_id):
    try:
        if not member_id:
            frappe.throw(_("member_id is required"))

        loans = frappe.get_all(
            "Library Loan",
            filters={"member": member_id},
            fields=["name", "book_title", "loan_date", "due_date", "return_date", "status"],
            order_by="loan_date desc"
        )
        return {
            "status": "success",
            "data": loans
        }

    except frappe.ValidationError as ve:
        # For custom validation errors (like frappe.throw)
        return {
            "status": "fail",
            "message": str(ve)
        }

    except Exception as e:
        # For unexpected errors
        frappe.log_error(frappe.get_traceback(), "Error in member_loan_history")
        return {
            "status": "error",
            "message": "Something went wrong while fetching the loan history.",
            "error": str(e)
        }


# API to issue a new book to a member and create a Library Loan record
@frappe.whitelist(allow_guest=False)
def issue_new_book():
    try:
        # Parse JSON body
        data = frappe.local.form_dict
        book_name = data.get("book_name")
        member_name = data.get("member_name")

        if not book_name or not member_name:
            raise BadRequest(_("Missing book_name or member_name"))

        # Create Library Loan doc
        loan = frappe.get_doc({
            "doctype": "Library Loan",
            "book": book_name,
            "member": member_name,
            "loan_date": nowdate()
        })

        loan.insert(ignore_permissions=True)
        loan.submit()
        return {
            "message": _("Library Loan created successfully."),
            "loan_id": loan.name,
            "status": "success"
        }

    except frappe.ValidationError as e:
        frappe.local.response.http_status_code = 422
        return {"error": str(e), "status": "failed"}
    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {"error": str(e), "status": "error"}


# API to process the return of a book, update loan status, book stock, and member loan count
@frappe.whitelist()
def process_book_return():
    try:
        # Parse input JSON
        loan_name = frappe.local.form_dict.get("loan_name")
        if not loan_name:
            raise BadRequest(_("Missing loan_name"))

        # Load the Library Loan document
        loan = frappe.get_doc("Library Loan", loan_name)

        # Call the same return logic used in UI
        if loan.status not in ["Loaned", "Overdue"]:
            frappe.local.response.http_status_code = 400
            return {"error": _("Loan is not currently active"), "status": "failed"}

        # Mark as returned (uses db.set_value because it's submitted)
        frappe.db.set_value("Library Loan", loan.name, {
            "status": "Returned",
            "return_date": frappe.utils.now_datetime()
        })

        # Update Book
        book = frappe.get_doc("Book", loan.book)
        book.available_quantity = (book.available_quantity or 0) + 1
        book.save()

        # Update Member
        member = frappe.get_doc("Library Member", loan.member)
        member.books_currently_loaned = (member.books_currently_loaned or 1) - 1
        member.save()

        return {
            "message": _("Book return processed successfully."),
            "status": "success"
        }

    except frappe.DoesNotExistError:
        frappe.local.response.http_status_code = 404
        return {"error": _("Loan not found"), "status": "error"}
    except frappe.ValidationError as e:
        frappe.local.response.http_status_code = 422
        return {"error": str(e), "status": "failed"}
    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {"error": str(e), "status": "error"}