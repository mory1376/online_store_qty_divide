// Copyright (c) 2023, mohebi and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["online store invntory"] = {
	"filters": [
		{
			"fieldname": "Store",
			"label": __("Store"),
			"fieldtype": "Link",
			"options": "online store inv",
		},
	]
};
