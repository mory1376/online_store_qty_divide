def execute(filters=None):
    columns = [
        _("Item") + ":Link/Item:200",
    ]

    stores = get_custom_online_stores()
    for store in stores:
        columns.append(_(store) + ":Int:100")
        columns.append(_(store + " Price") + ":Currency:100")  # Add a column for the item price

    data = []

    items = get_items()

    for item in items:
        row = [item.name]
        total_quantity = calculate_total_quantity_for_item(item.name)

        store_distribution = {store: 0 for store in stores}  # Create the dictionary with initial values

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
            # Append the current state of the distribution to the row, including the item price
            for store in stores:
                price, _ = get_price_for_store(item.name, store)  # Get the item price
                row.extend([store_distribution[store], price])

            # Check if all stores have hit their max_qty
            if all(store_distribution[store] >= get_max_qty_for_store(store) for store in stores):
                break

        data.append(row)

    return columns, data
