"""saas_manager/permissions.py — Row-level permission logic."""
import frappe


def has_permission(doc, ptype="read", user=None):
    user = user or frappe.session.user
    roles = frappe.get_roles(user)

    if "SaaS Admin" in roles or "System Manager" in roles:
        return True

    if "SaaS Customer" in roles and ptype == "read":
        customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
        return doc.customer == customer

    return False
