# CS462 — Thai Handwritten Numeral Recognition

จำแนกตัวเลขไทยเขียนด้วยมือ ๕๖–๖๐ ด้วย CNN

**สมาชิก:**
1. อนาวินธุ์ อักษรทิพย์ — 1660701440
2. ดฤพล กรณ์ถาวรวงศ์ — 1660703974
3. เอ็มเม็ต มีชัย แซลมอน — 1660704444
4. ธนวัฒน์ วิเศษชัยวรรณ — 1660703990

---

## ข้อควรระวัง (สำคัญ)

> **Windows**: ต้องวางโฟลเดอร์ใน path ที่สั้น เช่น `C:\CS462\` หรือ `C:\Users\ชื่อ\Desktop\`
>
> **อย่า**เปิดตรงจากโฟลเดอร์ Downloads โดยตรง โดยเฉพาะถ้าชื่อ user มีช่องว่าง
> เพราะ Windows มีลิมิต 260 ตัวอักษร — ถ้า path ยาวเกิน tensorflow จะติดตั้งไม่ได้

**วิธีแก้ถ้าติดตั้งไม่ผ่าน:**
1. สร้างโฟลเดอร์ `C:\CS462\`
2. ย้ายโปรเจกต์ไปไว้ที่นั่น
3. ลบโฟลเดอร์ `venv` (ถ้ามี) แล้วดับเบิลคลิก `run.bat` ใหม่

---

## วิธีติดตั้งและรัน

### วิธีที่ 1 — ดับเบิลคลิก (แนะนำ)

ดับเบิลคลิกที่ `run.bat` — จะติดตั้ง dependencies และเปิด server ให้อัตโนมัติ

จากนั้นเปิดเบราว์เซอร์ไปที่ `http://localhost:5000`

### วิธีที่ 2 — Command Line

```bash
pip install -r requirements.txt
python app.py
```

---

## (Optional) Evaluate model

ต้องมี dataset อยู่ที่ `dataset_thai_v4/dataset_thai_v4/`

```bash
python evaluate.py
```

จะสร้างไฟล์: `confusion_matrix.png`, `roc_curves.png`, `classification_report.txt`
