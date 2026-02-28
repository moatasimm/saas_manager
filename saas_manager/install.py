"""
saas_manager/install.py
Runs automatically on: bench --site SITE install-app saas_manager
Creates roles, default plans, and sample data.
"""
import frappe


def after_install():
    _create_roles()
    _create_default_plans()
    frappe.db.commit()
    print("✅ SaaS Manager installed successfully!")
    print("   → Go to: /app/saas-admin-dashboard")
    print("   → Customer Portal: /saas-portal")


def _create_roles():
    for role in ["SaaS Admin", "SaaS Customer"]:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)
            print(f"   ✓ Role created: {role}")


def _create_default_plans():
    plans = [
        {
            "plan_name": "Basic",
            "plan_code": "BASIC",
            "monthly_price": 299,
            "yearly_price": 2990,
            "max_users": 5,
            "storage_gb": 10,
            "api_calls_per_month": 50000,
            "trial_days": 14,
            "is_featured": 0,
            "is_active": 1,
            "sort_order": 1,
            "features": [
                {"feature_text": "5 مستخدمين"},
                {"feature_text": "10GB تخزين"},
                {"feature_text": "الوحدات الأساسية"},
                {"feature_text": "دعم بالبريد"},
            ],
        },
        {
            "plan_name": "Pro",
            "plan_code": "PRO",
            "monthly_price": 799,
            "yearly_price": 7990,
            "max_users": 25,
            "storage_gb": 50,
            "api_calls_per_month": 500000,
            "trial_days": 14,
            "is_featured": 1,
            "is_active": 1,
            "sort_order": 2,
            "features": [
                {"feature_text": "25 مستخدم"},
                {"feature_text": "50GB تخزين"},
                {"feature_text": "جميع الوحدات"},
                {"feature_text": "دعم أولوية"},
            ],
        },
        {
            "plan_name": "Enterprise",
            "plan_code": "ENTERPRISE",
            "monthly_price": 2499,
            "yearly_price": 24990,
            "max_users": 100,
            "storage_gb": 1024,
            "api_calls_per_month": 5000000,
            "trial_days": 30,
            "is_featured": 0,
            "is_active": 1,
            "sort_order": 3,
            "features": [
                {"feature_text": "مستخدمون غير محدود"},
                {"feature_text": "1TB تخزين"},
                {"feature_text": "تخصيص كامل"},
                {"feature_text": "مدير حساب خاص"},
            ],
        },
    ]

    for p in plans:
        if not frappe.db.exists("SaaS Plan", {"plan_code": p["plan_code"]}):
            doc = frappe.get_doc({"doctype": "SaaS Plan", **p})
            doc.insert(ignore_permissions=True)
            print(f"   ✓ Plan created: {p['plan_name']}")
