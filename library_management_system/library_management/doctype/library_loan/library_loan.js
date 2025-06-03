// Copyright (c) 2025, Nijith and contributors
// For license information, please see license.txt


// Show the book title and ISBN when a book is selected, and display the member's full name when a member is selected.

frappe.ui.form.on("Library Loan", {
	book: function(frm) {
        frappe.db.get_value("Book", frm.doc.book, ['title', 'isbn'] )
        .then(r => {
            let title = r.message.title;
            let isbn = r.message.isbn;
            frappe.msgprint(
                __("Title: {0}, ISBN: {1}", [title, isbn])
            );
        })
	},

    member: function(frm) {
        frappe.db.get_value("Library Member", frm.doc.member, 'full_name')
        .then(r => {
            let full_name = r.message.full_name;
            frappe.msgprint(
                __("Member Name: {0}", [full_name])
            );
        })
	}
});