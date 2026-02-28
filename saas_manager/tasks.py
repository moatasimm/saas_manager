import frappe
from frappe.utils import today, add_days, date_diff

def check_subscription_expiry():
    expired = frappe.get_all("SaaS Subscription",
        filters={"status": "Active", "end_date": ("<", today())},
        fields=["name", "customer", "subscription_id", "end_date"])
    for sub in expired:
        frappe.db.set_value("SaaS Subscription", sub.name, "status", "Expired")
    if expired:
        frappe.db.commit()
    frappe.logger().info(f"[SaaS] Expiry check done: {len(expired)} expired")

def send_renewal_reminders():
    for days in [30, 14, 7, 3, 1]:
        target = add_days(today(), days)
        subs = frappe.get_all("SaaS Subscription",
            filters={"status": "Active", "end_date": target, "auto_renew": 0},
            fields=["name", "customer", "subscription_id", "end_date", "plan"])
        for sub in subs:
            email = frappe.db.get_value("Customer", sub.customer, "email_id")
            if email:
                frappe.sendmail(recipients=[email],
                    subject=f"⏰ Subscription expires in {days} day(s)",
                    message=f"Your subscription {sub.subscription_id} expires on {sub.end_date}.")

def generate_weekly_reports():
    from frappe.utils import flt
    mrr = frappe.db.sql("SELECT IFNULL(SUM(monthly_amount),0) FROM `tabSaaS Subscription` WHERE status='Active'")[0][0]
    active = frappe.db.count("SaaS Subscription", {"status": "Active"})
    admins = frappe.get_all("Has Role", filters={"role": "SaaS Admin", "parenttype": "User"}, pluck="parent")
    if admins:
        frappe.sendmail(recipients=admins,
            subject=f"📊 Weekly SaaS Report — MRR: {flt(mrr,0):,.0f} SAR",
            message=f"<b>Active:</b> {active} | <b>MRR:</b> {flt(mrr,2):,.2f} SAR | <b>ARR:</b> {flt(mrr*12,2):,.2f} SAR")
