# Copyright (c) 2024, Aadhil and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Document Type"),
            "fieldname": "document_type",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Reference"),
            "fieldname": "reference",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Remark"),
            "fieldname": "po_remark",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Debit"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 120
        }
    ]

    conditions, values = get_conditions(filters)
    data = frappe.db.sql("""
        SELECT
            posting_date,
            IF(is_return, 'Sales Return', 'Sales Invoice') AS document_type,
            name AS reference,
            po_no AS po_remark,
            IF(is_return, 0, grand_total) AS debit,
            IF(is_return, grand_total, 0) AS credit
        FROM
            `tabSales Invoice`
        WHERE
            {conditions}
        ORDER BY
            posting_date ASC
    """.format(conditions=conditions), values, as_dict=True)

    balance = 0
    for row in data:
        balance += row.get("debit", 0) + row.get("credit", 0)
        row["balance"] = balance

    # Add total balance row
    total_balance = sum(row["debit"] + row["credit"] for row in data)

    return columns, data

def get_conditions(filters):
    conditions = "docstatus = 1"
    values = {}

    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    if filters.get("customer"):
        conditions += " AND customer = %(customer)s"
        values["customer"] = filters.get("customer")

    return conditions, values
