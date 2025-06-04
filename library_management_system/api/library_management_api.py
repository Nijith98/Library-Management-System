import frappe
from frappe import _


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