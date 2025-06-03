# Copyright (c) 2025, Nijith and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import date
from frappe.utils import date_diff
from frappe.query_builder.functions import Date


def execute(filters=None):
	validate_filters(filters)
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data
	
# Validate that 'To Date' is not before 'From Date'

def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")
	if date_diff(to_date, from_date) < 0:
		frappe.throw(_("To Date cannot be before From Date."))


def get_columns(filters):
	columns = [
		{
			"fieldname": "loan_id",
			"fieldtype": "Link",
			"label": ("Loan ID"),
			"options": "Library Loan"
		},
		{
			"fieldname": "book_title",
			"fieldtype": "Data",
			"label": ("Book Title"),
			"width": 150
		},
		{
			"fieldname": "isbn",
			"fieldtype": "Data",
			"label": ("ISBN"),
			"width": 150
		},
		{
			"fieldname": "member_name",
			"fieldtype": "Data",
			"label": ("Member Name"),
			"width": 150
		},
		{
			"fieldname": "loan_date",
			"fieldtype": "Date",
			"label": ("Loan Date"),
			"width": 150
		},
		{
			"fieldname": "due_date",
			"fieldtype": "Date",
			"label": ("Due Date"),
			"width": 150
		},
		{
			"fieldname": "days_overdue",
			"fieldtype": "Data",
			"label": _("Days Overdue"),
			"width": 150
		}
	]
	return columns


def get_data(filters):
	# Base query to fetch overdue loans
	lrl = frappe.qb.DocType("Library Loan")
	lrl_query = (
		frappe.qb.from_(lrl)
		.select(
			lrl.name.as_("loan_id"),
			lrl.book_title,
			lrl.isbn,
			lrl.member_name,
			lrl.loan_date,
			lrl.due_date
		)
		.where(lrl.docstatus < 2)
		.where(lrl.status == "Overdue")
	)
	
	# Apply filters to the loan query

	if filters.get("library_member"):
		lrl_query = lrl_query.where(lrl.member == filters.get("library_member"))
	if filters.get("from_date"):
		lrl_query = lrl_query.where(Date(lrl.loan_date) >= filters.get("from_date"))
	if filters.get("to_date"):
		lrl_query = lrl_query.where(Date(lrl.loan_date) <= filters.get("to_date"))
	
	results = lrl_query.run(as_dict=1)

	# Days Overdue (Calculated: Today - Due Date)
	
	for row in results:
		if row.due_date:
			row.days_overdue = (date.today() - row.due_date.date()).days
		else:
			row.days_overdue = 0

	return results