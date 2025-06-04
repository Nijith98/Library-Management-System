# Copyright (c) 2025, Nijith and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class Book(Document):
	def validate(self):
		self.initialize_available_quantity()
		self.validate_publication_year()

	# Initialize available_quantity if new
	def initialize_available_quantity(self):
		if self.is_new() and not self.available_quantity:
			self.available_quantity = self.total_quantity or 0

	# Validate that publication_year is between 1000 and the current year
	def validate_publication_year(self):
		current_year = datetime.now().year
		if not self.publication_year or self.publication_year < 1000 or self.publication_year > current_year:
			frappe.throw(f"Please enter a valid publication year, e.g. 2000.")