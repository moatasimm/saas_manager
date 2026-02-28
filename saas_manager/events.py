"""saas_manager/events.py — Document event hooks."""
import frappe


def subscription_on_submit(doc, method):
    frappe.logger().info(f"SaaS: Subscription submitted → {doc.subscription_id}")


def subscription_on_cancel(doc, method):
    frappe.logger().info(f"SaaS: Subscription cancelled → {doc.subscription_id}")
