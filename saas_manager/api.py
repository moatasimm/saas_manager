"""
saas_manager/api.py
Whitelisted API endpoints — Admin Dashboard + Customer Portal.
"""
import frappe
from frappe import _
from frappe.utils import today, add_months, date_diff, flt, getdate


# ══════════════════════════════════════════════════════════════════════════
# ADMIN APIs
# ══════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_admin_stats():
    """KPIs for admin dashboard header cards."""
    _admin_only()

    total    = frappe.db.count("SaaS Subscription")
    active   = frappe.db.count("SaaS Subscription", {"status": "Active"})
    trial    = frappe.db.count("SaaS Subscription", {"status": "Trial"})
    expired  = frappe.db.count("SaaS Subscription", {"status": "Expired"})
    paused   = frappe.db.count("SaaS Subscription", {"status": "Paused"})
    cancelled= frappe.db.count("SaaS Subscription", {"status": "Cancelled"})

    expiring_soon = frappe.db.count("SaaS Subscription", {
        "status": "Active",
        "end_date": ("between", [today(), add_months(today(), 1)]),
    })

    mrr = frappe.db.sql(
        "SELECT IFNULL(SUM(monthly_amount),0) FROM `tabSaaS Subscription` WHERE status='Active'"
    )[0][0] or 0

    return {
        "total": total, "active": active, "trial": trial,
        "expired": expired, "paused": paused, "cancelled": cancelled,
        "expiring_soon": expiring_soon,
        "mrr": flt(mrr, 2),
        "arr": flt(mrr * 12, 2),
        "retention_rate": round(active / max(total, 1) * 100, 2),
    }


@frappe.whitelist()
def get_subscriptions(status=None, search=None, page=1, page_size=20):
    """Paginated subscription list."""
    _admin_only()

    filters = {}
    if status:
        filters["status"] = status
    if search:
        filters["customer"] = ("like", f"%{search}%")

    page, page_size = int(page), int(page_size)
    rows = frappe.get_all(
        "SaaS Subscription",
        filters=filters,
        fields=["name","subscription_id","customer","plan","status",
                "start_date","end_date","billing_cycle","active_users",
                "max_users","monthly_amount","server_name","subdomain","auto_renew"],
        order_by="modified desc",
        limit_start=(page - 1) * page_size,
        limit_page_length=page_size,
    )
    total = frappe.db.count("SaaS Subscription", filters)
    return {"data": rows, "total": total, "page": page,
            "pages": -(-total // page_size)}


@frappe.whitelist()
def get_revenue_chart(months=8):
    """Monthly revenue for bar chart."""
    _admin_only()
    months = int(months)
    data = []
    for i in range(months - 1, -1, -1):
        ms = add_months(today(), -i)
        me = add_months(ms, 1)
        rev = frappe.db.sql(
            "SELECT IFNULL(SUM(grand_total),0) FROM `tabSales Invoice` "
            "WHERE docstatus=1 AND posting_date BETWEEN %s AND %s",
            (ms, me),
        )[0][0] or 0
        data.append({"month": ms[:7], "revenue": flt(rev, 2)})
    return data


@frappe.whitelist()
def get_plan_distribution():
    """Plan share for donut chart."""
    _admin_only()
    rows = frappe.db.sql(
        """SELECT sp.plan_name, sp.plan_code, COUNT(ss.name) AS count
           FROM `tabSaaS Subscription` ss
           JOIN `tabSaaS Plan` sp ON sp.name=ss.plan
           WHERE ss.status='Active'
           GROUP BY ss.plan ORDER BY count DESC""",
        as_dict=True,
    )
    total = sum(r.count for r in rows) or 1
    for r in rows:
        r["pct"] = round(r.count / total * 100, 1)
    return rows


@frappe.whitelist()
def admin_create_subscription(customer, plan, billing_cycle="Monthly", start_date=None):
    _admin_only()
    doc = frappe.new_doc("SaaS Subscription")
    doc.customer = customer
    doc.plan = plan
    doc.billing_cycle = billing_cycle
    doc.start_date = start_date or today()
    doc.status = "Trial"
    doc.insert(ignore_permissions=True)
    return {"success": True, "name": doc.name, "id": doc.subscription_id}


@frappe.whitelist()
def admin_change_status(name, status):
    _admin_only()
    allowed = ["Active", "Paused", "Expired", "Cancelled"]
    if status not in allowed:
        frappe.throw(f"Status must be one of: {', '.join(allowed)}")
    frappe.db.set_value("SaaS Subscription", name, "status", status)
    return {"success": True}


@frappe.whitelist()
def admin_renew(name, billing_cycle=None):
    _admin_only()
    doc = frappe.get_doc("SaaS Subscription", name)
    return doc.renew(billing_cycle)


@frappe.whitelist()
def admin_upgrade_plan(name, new_plan):
    _admin_only()
    doc = frappe.get_doc("SaaS Subscription", name)
    return doc.upgrade_plan(new_plan)


@frappe.whitelist()
def get_plans():
    """Return all active plans (used by both admin & portal)."""
    from saas_manager.doctype.saas_plan.saas_plan import SaaSPlan
    return SaaSPlan.get_active_plans()


# ══════════════════════════════════════════════════════════════════════════
# CUSTOMER PORTAL APIs
# ══════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_my_subscription():
    """Return current user's active subscription."""
    customer = _customer_for_user()
    if not customer:
        return {"error": "no_customer"}

    subs = frappe.get_all(
        "SaaS Subscription",
        filters={"customer": customer, "status": ("in", ["Trial","Active","Paused"])},
        fields=["*"],
        order_by="creation desc",
        limit=1,
    )
    if not subs:
        return {"error": "no_subscription"}

    doc = frappe.get_doc("SaaS Subscription", subs[0].name)
    data = doc.as_dict()
    data["days_remaining"] = doc.get_days_remaining()
    data["usage"] = doc.get_usage_summary()
    data["plan_details"] = frappe.get_doc("SaaS Plan", doc.plan).as_dict()
    return data


@frappe.whitelist()
def get_my_invoices(page=1, page_size=10):
    """Customer invoice history."""
    customer = _customer_for_user()
    if not customer:
        return {"error": "no_customer"}

    page, page_size = int(page), int(page_size)
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"customer": customer, "docstatus": 1},
        fields=["name","posting_date","grand_total","status","due_date"],
        order_by="posting_date desc",
        limit_start=(page - 1) * page_size,
        limit_page_length=page_size,
    )
    total = frappe.db.count("Sales Invoice", {"customer": customer, "docstatus": 1})
    return {"data": rows, "total": total}


@frappe.whitelist()
def request_upgrade(new_plan):
    """Customer requests a plan upgrade."""
    customer = _customer_for_user()
    if not customer:
        frappe.throw("No customer account linked to your user")

    sub = _active_sub(customer)
    if not sub:
        frappe.throw("No active subscription found")

    old_price = frappe.db.get_value("SaaS Plan", sub.plan, "monthly_price") or 0
    new_price  = frappe.db.get_value("SaaS Plan", new_plan, "monthly_price") or 0
    if new_price <= old_price:
        frappe.throw("You can only upgrade to a higher-tier plan")

    frappe.get_doc({
        "doctype": "ToDo",
        "description": f"Plan upgrade request: {customer} → {new_plan} (from {sub.plan})",
        "reference_type": "SaaS Subscription",
        "reference_name": sub.name,
        "owner": _saas_admin(),
        "priority": "High",
    }).insert(ignore_permissions=True)

    return {"success": True, "message": "Upgrade request submitted. Our team will reach out shortly."}


@frappe.whitelist()
def portal_get_users():
    """List users in customer's subscription."""
    customer = _customer_for_user()
    sub = _active_sub(customer) if customer else None
    if not sub:
        return []
    return frappe.get_all(
        "SaaS Subscription User",
        filters={"parent": sub.name},
        fields=["user", "role", "is_active", "invited_on"],
    )


@frappe.whitelist(allow_guest=True)
def ping():
    return {"status": "ok", "app": "saas_manager", "version": "1.0.0"}


# ══════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════

def _admin_only():
    if "SaaS Admin" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not permitted"), frappe.PermissionError)


def _customer_for_user():
    return frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")


def _active_sub(customer):
    rows = frappe.get_all(
        "SaaS Subscription",
        filters={"customer": customer, "status": ("in", ["Trial","Active"])},
        fields=["name","plan","status"],
        limit=1,
    )
    return rows[0] if rows else None


def _saas_admin():
    rows = frappe.get_all("Has Role",
        filters={"role": "SaaS Admin", "parenttype": "User"},
        pluck="parent", limit=1)
    return rows[0] if rows else "Administrator"
