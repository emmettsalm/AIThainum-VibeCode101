# CS462 — Thai Handwritten Numeral Recognition

จำแนกตัวเลขไทยเขียนด้วยมือ ๕๖–๖๐ ด้วย CNN

**สมาชิก:**
1. อนาวินธุ์ อักษรทิพย์ — 1660701440
2. ดฤพล กรณ์ถาวรวงศ์ — 1660703974
3. เอ็มเม็ต มีชัย แซลมอน — 1660704444
4. ธนวัฒน์ วิเศษชัยวรรณ — 1660703990

---

## วิธีใช้งาน (ทุก OS)

### สิ่งที่ต้องติดตั้งก่อน (ครั้งเดียว)

- **Python 3.10 – 3.12** → https://www.python.org/downloads/
- ตอนติดตั้งให้เช็ค **"Add Python to PATH"** ด้วย

### รันโปรแกรม

1. แตก zip หรือ clone repo ไว้ที่ไหนก็ได้
2. ดับเบิลคลิก **`run.bat`**
3. ครั้งแรกจะติดตั้ง dependencies ให้อัตโนมัติ (ใช้เวลา ~5 นาที)
4. เปิดเบราว์เซอร์ไปที่ `http://localhost:5000`

> **หมายเหตุ**: dependencies จะถูกติดตั้งที่ `C:\cs462venv\` เสมอ
> ไม่ว่าจะวางโปรเจกต์ไว้ที่ไหนก็ตาม จึงไม่มีปัญหา path ยาวเกิน

---

## (Optional) สำหรับนักพัฒนา

### Evaluate model

ต้องมี dataset อยู่ที่ `dataset_thai_v4/dataset_thai_v4/`

```bash
python evaluate.py
```

จะสร้างไฟล์: `confusion_matrix.png`, `roc_curves.png`, `classification_report.txt`

### Train model (ใช้ Google Colab)

เปิดไฟล์ `Train_thainumModel.py` ใน Google Colab เท่านั้น
(ไฟล์นี้ใช้คำสั่ง `!apt-get` ที่รันได้เฉพาะบน Colab/Linux)
