from erpnext.stock.doctype.item.item import Item
import frappe
from frappe import _


class ItemChild(Doc):

    @frappe.whitelist()
    def calculate_custom_total_qty(self):
        try:
            total_quantity = 0
            # Retrieve stock ledger entries for the specified item
            ledger_entries = frappe.get_all(
                'Stock Ledger Entry',
                filters={'item_code': self.item_code},
                fields=['actual_qty']
            )

            # Iterate through ledger entries and calculate total quantity
            for entry in ledger_entries:
                total_quantity += entry.actual_qty

            return 2020
        except Exception as e:
            frappe.log_error(f"An error occurred: {str(e)}")
            return 0  # Return 0 in case of an error
