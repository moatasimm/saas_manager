app_name        = "saas_manager"
app_title       = "SaaS Manager"
app_publisher   = "Your Company"
app_description = "ERPNext SaaS Subscription Management Platform"
app_email       = "admin@yourcompany.com"
app_license     = "MIT"
app_version     = "1.0.0"

# ── Roles ────────────────────────────────────────────────────────────────
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["SaaS Admin", "SaaS Customer"]]]},
    {"dt": "Custom Field", "filters": [["module", "=", "SaaS Manager"]]},
]

# ── Website Routes ────────────────────────────────────────────────────────
website_route_rules = [
    {"from_route": "/saas-portal", "to_route": "saas-portal/index"},
]

# ── Portal Sidebar ────────────────────────────────────────────────────────
standard_portal_menu_items = [
    {
        "title": "اشتراكي | My Subscription",
        "route": "/saas-portal",
        "reference_doctype": "SaaS Subscription",
        "role": "SaaS Customer",
    }
]

# ── Scheduled Tasks ───────────────────────────────────────────────────────
scheduler_events = {
    "daily": [
        "saas_manager.tasks.check_expiry",
        "saas_manager.tasks.send_renewal_reminders",
    ],
    "monthly": [
        "saas_manager.tasks.auto_generate_invoices",
    ],
}

# ── Document Events ───────────────────────────────────────────────────────
doc_events = {
    "SaaS Subscription": {
        "on_submit": "saas_manager.events.subscription_on_submit",
        "on_cancel": "saas_manager.events.subscription_on_cancel",
    },
}

# ── Assets ────────────────────────────────────────────────────────────────
app_include_css = ["/assets/saas_manager/css/saas_manager.css"]
app_include_js  = ["/assets/saas_manager/js/saas_manager.js"]

web_include_css = ["/assets/saas_manager/css/portal.css"]
web_include_js  = ["/assets/saas_manager/js/portal.js"]

# ── Permissions ───────────────────────────────────────────────────────────
has_permission = {
    "SaaS Subscription": "saas_manager.permissions.has_permission",
}

# ── Notification Config ───────────────────────────────────────────────────
notification_config = "saas_manager.notifications.get_notification_config"
