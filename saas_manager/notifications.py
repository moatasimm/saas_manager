"""saas_manager/notifications.py"""
import frappe


def get_notification_config():
    return {
        "for_doctype": {
            "SaaS Subscription": {"status": "Trial"},
        }
    }
