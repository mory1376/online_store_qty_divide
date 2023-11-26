from frappe import _
import frappe


def execute(filters=None):
    columns = [
        _("Item") + ":Link/Item:200",
    ]

    stores = get_custom_online_stores()
    if not filters:
        for store in stores:
            columns.append(_(store) + ":Int:100")
            columns.append(_(store + " Price") + ":Currency:100")
    if filters:
        columns.append(_(filters['Store']) + ":Int:100")
        columns.append(_(filters['Store'] + " Price") + ":Currency:100")
    data = []
    items = get_items()

    for item in items:
        row = [item.name]
        total_quantity = calculate_total_quantity_for_item(item.name)

        store_distribution = {store: 0 for store in stores}  # Create the dictionary with initial values
        price_distribution = {store: 0 for store in stores}  # Create the dictionary with initial values

        while total_quantity > 0:
            for store in stores:
                max_qty = get_max_qty_for_store(store)
                priority = get_priority_for_store(item.name, store)
                allowed_qty = min(max_qty - store_distribution[store], 1) if priority > 0 else 0

                if total_quantity > 0 and allowed_qty > 0:
                    if store_distribution[store] >= max_qty:
                        continue  # Skip stores that have already reached their max_qty
                    store_distribution[store] = store_distribution[store] + 1  # Add 1 to the store's quantity
                    total_quantity -= 1
            # Append the current state of the distribution to the row
            for store in stores:
                price = get_price_for_store(item.name, store)
                price_distribution[store] = price
            # Check if all stores have hit their max_qty
            if all(store_distribution[store] >= get_max_qty_for_store(store) for store in stores):
                break
        result = create_list(item, store_distribution, price_distribution)
        if filters:
            result2 = filter_list(result, filters)
            result3 = remove_items_by_pattern(result2)

        if not filters:
            result3 = remove_items_by_pattern(result)

        data.append(result3)

    return columns, data


def filter_list(input_list, filters):
    result = []

    for i in range(0, len(input_list), 4):
        item = input_list[i:i+4]

        # Check if there are enough elements in the chunk
        if len(item) >= 2:
            store = item[1]

            if isinstance(store, str) and store == filters.get('Store', ''):
                result.extend(item)

    return result

def remove_items_by_pattern(input_list):
    result = []
    i = 0
    pattern_position = 1

    while i < len(input_list):
        if i == pattern_position:
            result.append(input_list[i])
            pattern_position += 3
        i += 1
    result2 = [x for x in input_list if x not in result]
    return result2


def create_list(item_name, store_distribution, price_distribution):
    result_list = [item_name]

    for store in store_distribution:
        store_qty = store_distribution[store]
        store = store
        price = price_distribution.get(store, 0)
        result_list.extend([store, store_qty, price])

    # Convert integer values to float
    result_list = [float(item) if isinstance(item, int) else item for item in result_list]

    # Convert the first element to a string if it's a dictionary
    if isinstance(result_list[0], dict):
        result_list[0] = result_list[0].get('name', '')
    if isinstance(result_list[0], dict):
        result_list[1] = result_list[1].get(store, '')
    return result_list


def get_custom_online_stores():
    stores = []
    online_store_inv_child_table_data = frappe.get_all("online store inv", filters={}, fields=["store"])
    for row in online_store_inv_child_table_data:
        stores.append(row.store)

    return stores


def get_items():
    items = frappe.get_all("Item", filters={"custom_total_qty": (">", 0)}, fields=["name"])
    items_with_priority = []

    for item in items:
        online_store_inv_data = frappe.get_all("online store inv child table",
                                               filters={"parent": item.name},
                                               fields=["name"])
        total_qty = calculate_total_quantity_for_item(item.name)
        if online_store_inv_data and total_qty != 0:
            items_with_priority.append(item)

    return items_with_priority


def calculate_total_quantity_for_item(item):
    total_quantity = 0
    warehouses = frappe.get_doc("online_inv_allow_warehouse")
    allowed_warehouses = warehouses.warehouse
    allowed_warehouse_names = [child.warehouse for child in allowed_warehouses]

    bins = frappe.get_all(
        'Bin',
        filters={'item_code': item, 'warehouse': ['in', allowed_warehouse_names]},
        fields=['projected_qty', 'reserved_qty']
    )

    for bin in bins:
        total_quantity += max(bin.projected_qty, 0)

    return total_quantity


def get_max_qty_for_store(store):
    online_store_inv_data = frappe.get_all("online store inv", filters={"store": store},
                                           fields=["max_allowed_qty_pitem"])
    max_qty = online_store_inv_data[0].max_allowed_qty_pitem if online_store_inv_data else 0
    return max_qty


def get_priority_for_store(item, store):
    priority_data = frappe.get_all("online store inv child table", filters={"parent": item, "store": store},
                                   fields=["priority"])
    priority = priority_data[0].priority if priority_data else 0
    return priority


def get_price_for_store(item, store):
    store_price_list = frappe.get_all("online store inv", filters={"store": store},
                                      fields=["price_list"])
    item_price_currency = frappe.get_all("Item Price",
                                         filters={"item_code": item, "price_list": store_price_list[0].price_list},
                                         fields=["price_list_rate", "currency"])
    price = item_price_currency[0].price_list_rate if item_price_currency else 0
    currency = item_price_currency[0].currency if item_price_currency else None
    return price
