# نظام تداول آلي ذكي للعملات المشفرة

نظام تداول آلي متعدد الطبقات يستخدم التعلم الآلي للتداول في العملات المشفرة عبر منصة بايننس.

## هيكل المشروع

```
├── src/
│   ├── analysis/           # تحليل البيانات والمؤشرات الفنية
│   ├── connection/         # الاتصال مع منصة Binance
│   ├── data/              # جمع وإدارة البيانات
│   ├── database/          # التعامل مع قاعدة البيانات
│   ├── trading/           # استراتيجيات وإدارة التداول
│   └── config.py          # إعدادات النظام
├── tests/                 # اختبارات النظام
└── README.md
```

## قاعدة البيانات

يستخدم النظام قاعدة بيانات MongoDB لتخزين البيانات التالية:

### المجموعات (Collections)

1. **market_data**
   - symbol: رمز العملة
   - timestamp: وقت التسجيل
   - data: بيانات السوق (OHLCV)
   - technical_indicators: المؤشرات الفنية
     - trend: اتجاه السوق
     - moving_averages: المتوسطات المتحركة
     - momentum: مؤشرات الزخم
     - volume: مؤشرات الحجم

2. **technical_analysis**
   - symbol: رمز العملة
   - timestamp: وقت التحليل
   - trend: نوع الاتجاه
   - signal_strength: قوة الإشارة
   - indicators: قيم المؤشرات

3. **news_analysis**
   - symbol: رمز العملة
   - timestamp: وقت التحليل
   - sentiment: توجه الخبر
   - confidence: درجة الثقة
   - source: مصدر الخبر

4. **trades**
   - timestamp: وقت التداول
   - symbol: رمز العملة
   - side: نوع الصفقة (شراء/بيع)
   - price: السعر
   - quantity: الكمية
   - total: القيمة الإجمالية
   - status: حالة الصفقة
   - market_trend: اتجاه السوق
   - strategy_type: نوع الاستراتيجية

## المتطلبات

- Python 3.11
- MongoDB
- مفاتيح API لمنصة Binance

## المكتبات المستخدمة

- ccxt: للاتصال مع منصة Binance
- pandas: لمعالجة البيانات
- pandas-ta: للمؤشرات الفنية
- pymongo: للاتصال مع قاعدة البيانات
- numpy: للعمليات الحسابية
- scikit-learn: للتعلم الآلي
