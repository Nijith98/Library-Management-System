// Copyright (c) 2025, Nijith and contributors
// For license information, please see license.txt

frappe.query_reports["Overdue Book Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": (__("From Date")),
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": (__("From Date")),
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "library_member",
			"fieldtype": "Link",
			"options": "Library Member",
			"label": (__("Library Member"))
		}
	]
};