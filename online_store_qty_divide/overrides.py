from frappe.model.document import Document
import frappe
from erpnext.stock.doctype.item.item import Item

class CustomItem(Document):
    def stock_ledger_created(self):
        if not hasattr(self, "_stock_ledger_created"):
            self._stock_ledger_created = len(
                frappe.db.sql(
                    """select name from `tabStock Ledger Entry`
                where item_code = %s and is_cancelled = 0 limit 1""",
                    self.name,
                )
            )
        return self._stock_ledger_created

    def onload(self):
        self.set_onload("stock_exists", self.stock_ledger_created())
        self.set_onload("asset_naming_series", get_asset_naming_series())
        self.calculate_custom_total_qty()

    def calculate_custom_total_qty(self):
        total_quantity = 0
        warehouses = frappe.get_doc("online_inv_allow_warehouse")
        allowed_warehouses = warehouses.warehouse
        allowed_warehouse_names = [child.warehouse for child in allowed_warehouses]

        if allowed_warehouse_names:
            bins = frappe.get_all(
                'Bin',
                filters={'item_code': self.item_code, 'warehouse': ['in', allowed_warehouse_names]},
                fields=['projected_qty']
            )
            if bins:
                for bin in bins:
                    temp_total_quantity = bin.projected_qty
                    if temp_total_quantity < 0:
                        temp_total_quantity = 0
                    total_quantity += temp_total_quantity

        self.custom_total_qty = total_quantity
        if self.custom_total_qty > 0:

@frappe.whitelist()
def get_asset_naming_series():
	from erpnext.assets.doctype.asset.asset import get_asset_naming_series

	return get_asset_naming_series()
