# نظام تداول آلي ذكي للعملات المشفرة

نظام تداول آلي متعدد الطبقات يستخدم التعلم الآلي للتداول في العملات المشفرة عبر منصة بايننس.

## خطوات التثبيت

1. تثبيت Python 3.11:
```bash
sudo apt update
sudo apt install python3.11 python3.11-dev
```

2. تثبيت MongoDB:
```bash
sudo apt install mongodb
sudo systemctl start mongodb
```

3. إنشاء بيئة افتراضية وتفعيلها:
```bash
python3.11 -m venv venv
source venv/bin/activate  # لنظام Linux/Mac
# أو
.\venv\Scripts\activate  # لنظام Windows
```

4. تثبيت المكتبات المطلوبة:
```bash
pip install ccxt pandas pandas-ta numpy scikit-learn pymongo streamlit plotly
```

5. تعيين المتغيرات البيئية:
```bash
export BINANCE_API_KEY='your_api_key'
export BINANCE_API_SECRET='your_api_secret'
export MONGODB_URL='mongodb://localhost:27017/'
export NEWS_API_KEY='your_news_api_key'  # اختياري
```

6. تشغيل النظام:
```bash
# تشغيل نظام التداول
cd src
PYTHONPATH=. python main.py

# تشغيل واجهة المستخدم
cd src
PYTHONPATH=. streamlit run run_dashboard.py
```

## المتطلبات الأساسية

1. Python 3.11
2. MongoDB
3. مفاتيح API لمنصة Binance (للتداول الحقيقي)

## المكتبات المطلوبة

- ccxt: للاتصال مع منصة Binance
- pandas: لمعالجة البيانات
- pandas-ta: للمؤشرات الفنية
- numpy: للعمليات الحسابية
- scikit-learn: للتعلم الآلي
- pymongo: للاتصال مع قاعدة البيانات
- streamlit: لواجهة المستخدم
- plotly: للرسوم البيانية

## هيكل المشروع

```
src/
├── analysis/           # تحليل البيانات والمؤشرات الفنية
├── connection/         # الاتصال مع منصة Binance
├── data/              # جمع وإدارة البيانات
├── database/          # التعامل مع قاعدة البيانات
├── trading/           # استراتيجيات وإدارة التداول
├── visualization/     # واجهة المستخدم والرسوم البيانية
└── config.py          # إعدادات النظام
```

## قاعدة البيانات

يستخدم النظام MongoDB لتخزين:
1. بيانات السوق (OHLCV)
2. المؤشرات الفنية واتجاهات السوق
3. نتائج التحليل الفني
4. معلومات التداولات

## الوظائف الرئيسية

1. جمع وتحليل بيانات السوق بشكل مستمر
2. حساب المؤشرات الفنية وتحديد اتجاه السوق
3. تحليل الأخبار وتأثيرها على السوق
4. استخدام التعلم الآلي للتنبؤ بحركة السعر
5. تنفيذ استراتيجيات التداول آلياً
6. عرض التحليلات والنتائج في واجهة مستخدم تفاعلية

## ملاحظات مهمة

- يمكن استخدام وضع المحاكاة للتجربة بدون مفاتيح API حقيقية
- يجب التأكد من إعداد قاعدة البيانات MongoDB قبل التشغيل
- يمكن تعديل إعدادات التداول في ملف config.py
- للتشغيل في وضع المحاكاة، لا يلزم تعيين مفاتيح API