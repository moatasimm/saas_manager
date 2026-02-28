# 🚀 دليل تثبيت SaaS Manager في ERPNext v15

## نظرة عامة
هذا التطبيق يضيف إلى ERPNext:
- **لوحة تحكم المدير** → `/app/saas-admin-dashboard`
- **بوابة العميل** → `/saas-portal`
- **3 DocTypes** → SaaS Plan / SaaS Subscription / SaaS Plan Feature
- **API كامل** + مهام مجدولة تلقائية

---

## 📋 المتطلبات
- ERPNext v15 مثبت ويعمل
- Python 3.10+
- Bench v5+
- صلاحية الوصول إلى السيرفر (SSH)

---

## 🛠️ خطوات التثبيت

### الخطوة 1 — انسخ ملفات التطبيق

```bash
# انتقل إلى مجلد apps
cd /home/frappe/frappe-bench/apps

# انسخ مجلد saas_manager إلى هنا
# (قم برفع مجلد saas_manager من جهازك عبر scp أو git)
git clone https://github.com/YOUR_REPO/saas_manager.git
# أو انسخه يدوياً بـ scp
```

### الخطوة 2 — ثبّت التطبيق على الـ bench

```bash
cd /home/frappe/frappe-bench
bench get-app saas_manager /path/to/saas_manager
```

> **إذا كان المجلد موجوداً محلياً:**
```bash
pip install -e apps/saas_manager
```

### الخطوة 3 — ثبّت على الموقع

```bash
# استبدل YOUR_SITE_NAME باسم موقعك (مثل: mysite.localhost)
bench --site YOUR_SITE_NAME install-app saas_manager
```

✅ هذا سيقوم تلقائياً بـ:
- إنشاء الـ DocTypes في قاعدة البيانات
- إنشاء الأدوار: SaaS Admin و SaaS Customer  
- إنشاء الخطط الافتراضية: Basic, Pro, Enterprise
- إعداد المهام المجدولة

### الخطوة 4 — أعد تشغيل الخدمات

```bash
bench restart
bench build --app saas_manager
```

### الخطوة 5 — تحقق من التثبيت

```bash
bench --site YOUR_SITE_NAME list-apps
# يجب أن ترى: saas_manager
```

---

## ⚙️ الإعداد بعد التثبيت

### 1. إعطاء صلاحية المدير

في ERPNext → الإعدادات → المستخدمون:
1. افتح مستخدم المدير
2. اضف دور: **SaaS Admin**
3. احفظ

### 2. ربط العملاء بحسابات المستخدمين

لكل عميل تريد أن يصل إلى بوابة العميل:
1. اذهب إلى: **Selling → Customer**
2. افتح سجل العميل
3. في حقل **Email ID** → أدخل بريد المستخدم في ERPNext
4. احفظ

ثم أضف دور **SaaS Customer** للمستخدم.

### 3. فتح لوحة التحكم

- **لوحة المدير**: `/app/saas-admin-dashboard`
- **بوابة العميل**: `/saas-portal`

---

## 📁 هيكل الملفات

```
saas_manager/
├── setup.py                          ← إعداد Python Package
├── requirements.txt
└── saas_manager/
    ├── __init__.py
    ├── hooks.py                      ← إعدادات التطبيق
    ├── api.py                        ← جميع API endpoints
    ├── install.py                    ← يُشغَّل عند التثبيت
    ├── tasks.py                      ← مهام مجدولة (إنتهاء، تذكير)
    ├── doctype/
    │   ├── saas_plan/
    │   │   ├── saas_plan.json        ← تعريف الـ DocType
    │   │   ├── saas_plan.py          ← Python controller
    │   │   └── saas_plan_feature.json← Child table للمميزات
    │   └── saas_subscription/
    │       ├── saas_subscription.json← تعريف الـ DocType
    │       └── saas_subscription.py  ← Python controller (تجديد، ترقية)
    ├── page/
    │   └── saas_admin_dashboard/
    │       ├── saas_admin_dashboard.json  ← تعريف الـ Page
    │       ├── saas_admin_dashboard.html  ← HTML الواجهة
    │       ├── saas_admin_dashboard.js    ← JavaScript (Frappe)
    │       └── saas_admin_dashboard.py   ← Python controller
    └── www/
        └── saas-portal/
            ├── index.html            ← Jinja Template للبوابة
            └── index.py              ← Python controller للبوابة
```

---

## 🔌 API Endpoints

جميع الـ APIs تستخدم مسار: `/api/method/saas_manager.api.METHOD_NAME`

| Method | وصف | الصلاحية |
|--------|-----|-----------|
| `get_admin_dashboard_stats` | إحصائيات لوحة المدير | SaaS Admin |
| `get_subscriptions_list` | قائمة الاشتراكات مع تصفية | SaaS Admin |
| `get_revenue_chart` | بيانات رسم الإيرادات | SaaS Admin |
| `get_plan_distribution` | توزيع الخطط للرسم البياني | SaaS Admin |
| `admin_create_subscription` | إنشاء اشتراك جديد | SaaS Admin |
| `admin_change_status` | تغيير حالة اشتراك | SaaS Admin |
| `admin_renew_subscription` | تجديد اشتراك | SaaS Admin |
| `get_my_subscription` | بيانات اشتراك العميل | SaaS Customer |
| `get_my_invoices` | فواتير العميل | SaaS Customer |
| `request_plan_upgrade` | طلب ترقية | SaaS Customer |
| `get_available_plans` | الخطط المتاحة | Public |
| `ping` | فحص الاتصال | Public |

**مثال استخدام API:**
```javascript
// من داخل ERPNext
frappe.call({
    method: 'saas_manager.api.get_admin_dashboard_stats',
    callback: (r) => console.log(r.message)
});

// من خارج ERPNext (REST)
fetch('/api/method/saas_manager.api.get_available_plans', {
    headers: { 'X-Frappe-CSRF-Token': frappe.csrf_token }
})
```

---

## 🐛 حل المشاكل الشائعة

### المشكلة: `ModuleNotFoundError: No module named 'saas_manager'`
```bash
cd /home/frappe/frappe-bench
pip install -e apps/saas_manager
bench restart
```

### المشكلة: الـ DocTypes لا تظهر
```bash
bench --site YOUR_SITE migrate
bench restart
```

### المشكلة: لوحة التحكم لا تفتح
```bash
bench build --app saas_manager
bench clear-cache
```

### المشكلة: `Permission Error` في API
- تأكد أن المستخدم لديه دور **SaaS Admin**
- اذهب إلى: Settings → User → أضف الدور

---

## 📧 الدعم
للمساعدة: admin@erpcloud.sa
