# Copyright (c) 2025, Nijith and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class LibraryLoan(Document):
    def before_submit(self):
        self.validate_book_availablity()
        self.validate_member_loan_eligibility()

    def on_submit(self):
        self.set_due_date()

    # Raise an exception if the book is not available.
    def validate_book_availablity(self):
        available_qty = frappe.db.get_value("Book", self.book, "available_quantity")
        if available_qty <= 0:
            frappe.throw(f"Book '<b>{self.book}</b>' is not available")
    

    # Fetch member details: max allowed books, current loaned books, and membership status
    def validate_member_loan_eligibility(self):
        dict_value = frappe.db.get_value("Library Member", self.member, ['max_books_allowed', 'books_currently_loaned', 'membership_status'], as_dict=1)
        if dict_value.max_books_allowed <= dict_value.books_currently_loaned:
            frappe.throw(f"Member '<b>{self.member_name}</b>' has reached the maximum loan limit")
        if dict_value.membership_status != "Active":
            frappe.throw(f"Member '<b>{self.member_name}</b>' is not active")

    # Automatically calculate and update due_date and status when the document is submitted
    def set_due_date(self):
        loan_per_days = frappe.db.get_single_value('Library Settings', 'loan_period_days')
        self.due_date = add_days(self.loan_date, loan_per_days)
        self.status = "Loaned"

        # Update and save Book
        book = frappe.get_doc("Book", self.book)
        book.available_quantity = (book.available_quantity or 0) - 1
        book.save()

        # Update and save Library Member
        member = frappe.get_doc("Library Member", self.member)
        member.books_currently_loaned = (member.books_currently_loaned or 1) + 1
        member.save()