// Copyright (c) 2025, Nijith and contributors
// For license information, please see license.txt


frappe.ui.form.on("Library Loan", {
    // Add "Mark as Returned" button if loan is active or overdue and button show only document after submit
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && ['Loaned', 'Overdue'].includes(frm.doc.status)) {
            frm.add_custom_button('Mark as Returned', function() {
                frm.call('mark_as_returned').then(() => {
                    frappe.msgprint('Book returned successfully');
                    frm.reload_doc();
                });
            }, 'Actions');
        }
    },

    // Pop up the book title and ISBN when a book is selected
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

    // Pop up the Library Member's full name when a member is selected
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