# Copyright (c) 2023, mohebi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe


class onlinestoreinv(Document):

    def validate_default_priority(doc, method):
        # Check if default_priority is positive
        if doc.default_priority <= 0:
            frappe.throw("Default Priority must be a positive number.")

        # Check if default_priority is unique
        existing_record = frappe.get_all("online_store_inv",
                                         filters={"default_priority": doc.default_priority, "name": ("!=", doc.name)},
                                         fields=["name"])
        if existing_record:
            frappe.throw("Default Priority must be unique.")

    # Attach the validation function to the doctype
    doc_events = {
        "online_store_inv": {
            "validate": validate_default_priority
        }
    }


