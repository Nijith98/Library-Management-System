import frappe
from frappe.utils import nowdate


# Scheduled task to update status of overdue library loans daily
def update_overdue_status():
    # Retrieve all 'Library Loan' records where status is 'Loaned' and due_date is before today
    overdue_loans = frappe.get_all(
        "Library Loan",
        filters={
            "status": "Loaned",
            "due_date": ["<", nowdate()]
        },
        fields=["name"]
    )
    
    # Update the status of each overdue loan to 'Overdue'
    for loan in overdue_loans:
        doc = frappe.get_doc("Library Loan", loan.name)
        doc.status = "Overdue"
        doc.save()