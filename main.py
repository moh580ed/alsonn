import flet as ft
import qrcode
from io import BytesIO
import base64
import json
import re
import os
import webbrowser
import time

# --- دوال مساعدة لمعالجة الأرقام والروابط ---
def clean_phone(phone):
    """تنظيف رقم الهاتف من المسافات والرموز"""
    return ''.join(filter(str.isdigit, phone))

def get_platform_url(platform, handle):
    """تحويل اسم المنصة والمعرف إلى رابط مباشر"""
    platform = platform.lower().strip()
    handle = handle.strip()
    links = {
        "facebook": f"https://facebook.com/{handle}",
        "twitter": f"https://twitter.com/{handle}",
        "instagram": f"https://instagram.com/{handle}",
        "tiktok": f"https://tiktok.com/@{handle}",
        "telegram": f"https://t.me/{handle}",
        "youtube": f"https://youtube.com/@{handle}",
        "linkedin": f"https://linkedin.com/in/{handle}",
        "github": f"https://github.com/{handle}",
        "snapchat": f"https://snapchat.com/add/{handle}",
        "reddit": f"https://reddit.com/user/{handle}",
    }
    return links.get(platform, "")

# --- نموذج البيانات ---
class ContactData:
    def __init__(self, name="", primary_phone="", extra_phones=None, primary_email="",
                 extra_emails=None, social_media=None, image_data=None):
        self.name = name
        self.primary_phone = primary_phone
        self.extra_phones = extra_phones or []
        self.primary_email = primary_email
        self.extra_emails = extra_emails or []
        self.social_media = social_media or {}  # dict: {platform: handle}
        self.image_data = image_data  # base64 string

    def to_dict(self):
        return {
            "name": self.name,
            "primary_phone": self.primary_phone,
            "extra_phones": self.extra_phones,
            "primary_email": self.primary_email,
            "extra_emails": self.extra_emails,
            "social_media": self.social_media,
            "image_data": self.image_data,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            primary_phone=data.get("primary_phone", ""),
            extra_phones=data.get("extra_phones", []),
            primary_email=data.get("primary_email", ""),
            extra_emails=data.get("extra_emails", []),
            social_media=data.get("social_media", {}),
            image_data=data.get("image_data", None),
        )

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str):
        try:
            return cls.from_dict(json.loads(json_str))
        except:
            return None

    def to_vcard(self):
        """تحويل البيانات إلى صيغة vCard"""
        vcard = "BEGIN:VCARD\nVERSION:3.0\n"
        vcard += f"FN:{self.name}\n"
        vcard += f"TEL;TYPE=CELL;PREF:{clean_phone(self.primary_phone)}\n"
        for p in self.extra_phones:
            vcard += f"TEL;TYPE=CELL:{clean_phone(p)}\n"
        vcard += f"EMAIL;PREF:{self.primary_email}\n"
        for e in self.extra_emails:
            vcard += f"EMAIL:{e}\n"
        notes = "; ".join([f"{p}: {h}" for p, h in self.social_media.items()])
        if notes:
            vcard += f"NOTE:{notes}\n"
        vcard += "END:VCARD"
        return vcard

# --- الصفحة الرئيسية (عرض البيانات + توليد الكود) ---
class MainPage(ft.UserControl):
    def __init__(self, page, contact_data=None):
        super().__init__()
        self.page = page
        self.contact = contact_data or ContactData()
        self.qr_image_ref = ft.Ref[ft.Image]()
        self.scan_result_dialog = None

    def build(self):
        # صورة شخصية
        self.avatar = ft.Container(
            width=100,
            height=100,
            border_radius=50,
            bgcolor=ft.Colors.GREY_300,
            content=ft.Icon(name=ft.icons.PERSON, size=50, color=ft.Colors.GREY_600),
            alignment=ft.alignment.center,
        )
        if self.contact.image_data:
            self.avatar.content = ft.Image(
                src_base64=self.contact.image_data,
                width=100,
                height=100,
                fit=ft.ImageFit.COVER,
            )

        # اسم المستخدم
        self.name_text = ft.Text(self.contact.name or "اسم المستخدم", size=24, weight=ft.FontWeight.BOLD)

        # رقم الواتساب الأساسي
        self.whatsapp_button = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.icons.WHATSAPP, color=ft.Colors.WHITE), ft.Text("تواصل عبر واتساب")],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_400,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=ft.Radius(30)),
            ),
            on_click=lambda e: self.page.launch_url(f"https://wa.me/{clean_phone(self.contact.primary_phone)}"),
            visible=bool(self.contact.primary_phone),
        )

        # باقي المعلومات
        self.info_container = ft.Column(spacing=10)

        # أرقام إضافية
        if self.contact.extra_phones:
            extra_phones_row = ft.Row([
                ft.Icon(ft.icons.PHONE, color=ft.Colors.BLUE_400),
                ft.Text("أرقام إضافية: ", weight=ft.FontWeight.BOLD),
                ft.Text(", ".join(self.contact.extra_phones)),
            ])
            self.info_container.controls.append(extra_phones_row)

        # البريد الإلكتروني
        email_row = ft.Row([
            ft.Icon(ft.icons.EMAIL, color=ft.Colors.RED_400),
            ft.Text("البريد: ", weight=ft.FontWeight.BOLD),
            ft.Text(self.contact.primary_email),
        ])
        self.info_container.controls.append(email_row)

        # بريد إضافي
        if self.contact.extra_emails:
            extra_emails_row = ft.Row([
                ft.Icon(ft.icons.EMAIL_OUTLINED, color=ft.Colors.RED_400),
                ft.Text("بريد إضافي: ", weight=ft.FontWeight.BOLD),
                ft.Text(", ".join(self.contact.extra_emails)),
            ])
            self.info_container.controls.append(extra_emails_row)

        # حسابات التواصل الاجتماعي
        if self.contact.social_media:
            social_row = ft.Row(wrap=True, spacing=10)
            for platform, handle in self.contact.social_media.items():
                url = get_platform_url(platform, handle)
                if url:
                    social_row.controls.append(
                        ft.IconButton(
                            icon=ft.icons.LINK,
                            tooltip=f"{platform}: {handle}",
                            on_click=lambda e, url=url: self.page.launch_url(url),
                        )
                    )
                else:
                    social_row.controls.append(ft.Text(f"{platform}: {handle}"))
            self.info_container.controls.append(social_row)

        # كود QR الخاص بالمستخدم
        self.qr_image = ft.Image(
            ref=self.qr_image_ref,
            width=200,
            height=200,
            visible=False,
        )

        # زر توليد كود QR
        generate_qr_button = ft.ElevatedButton(
            text="توليد كود QR الخاص بي",
            icon=ft.icons.QR_CODE,
            on_click=self.generate_qr_code,
        )

        # زر تعديل البيانات
        edit_button = ft.ElevatedButton(
            text="تعديل البيانات",
            icon=ft.icons.EDIT,
            on_click=lambda e: self.page.go("/edit"),
        )

        # زر المسح
        scan_button = ft.ElevatedButton(
            text="مسح كود QR",
            icon=ft.icons.QR_CODE_SCANNER,
            on_click=lambda e: self.page.go("/scan"),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([self.avatar], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.name_text], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.whatsapp_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20),
                    self.info_container,
                    ft.Divider(height=20),
                    ft.Row([self.qr_image], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([generate_qr_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([edit_button, scan_button], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        )

    def generate_qr_code(self, e):
        """توليد كود QR من بيانات المستخدم"""
        if not self.contact.name or not self.contact.primary_phone:
            self.page.snack_bar = ft.SnackBar(ft.Text("يرجى إدخال الاسم ورقم الواتساب أولاً"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # تحويل البيانات إلى JSON
        data = self.contact.to_json()

        # توليد الكود
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # تحويل الصورة إلى base64
        img = qr.make_image(fill_color="#2d3748", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # عرض الصورة
        self.qr_image.src_base64 = img_base64
        self.qr_image.visible = True
        self.qr_image_ref.current.update()
        self.page.update()

        self.page.snack_bar = ft.SnackBar(ft.Text("✅ تم توليد كود QR بنجاح!"))
        self.page.snack_bar.open = True
        self.page.update()

# --- صفحة تعديل البيانات ---
class EditPage(ft.UserControl):
    def __init__(self, page, contact_data=None):
        super().__init__()
        self.page = page
        self.contact = contact_data or ContactData()
        self.image_data = self.contact.image_data

    def build(self):
        # حقول الإدخال
        self.name_field = ft.TextField(
            label="الاسم الكامل",
            value=self.contact.name,
            width=300,
        )
        self.primary_phone_field = ft.TextField(
            label="رقم الواتساب الأساسي",
            value=self.contact.primary_phone,
            width=300,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        self.extra_phones_field = ft.TextField(
            label="أرقام إضافية (افصل بينها بفاصلة)",
            value=", ".join(self.contact.extra_phones) if self.contact.extra_phones else "",
            width=300,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        self.primary_email_field = ft.TextField(
            label="البريد الإلكتروني الأساسي",
            value=self.contact.primary_email,
            width=300,
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        self.extra_emails_field = ft.TextField(
            label="بريد إضافي (افصل بينها بفاصلة)",
            value=", ".join(self.contact.extra_emails) if self.contact.extra_emails else "",
            width=300,
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        self.social_field = ft.TextField(
            label="حسابات التواصل (المنصة:المعرف, منصة2:معرف2)",
            value=", ".join([f"{p}:{h}" for p, h in self.contact.social_media.items()]),
            width=300,
            multiline=True,
            min_lines=2,
        )

        # زر اختيار الصورة
        self.image_button = ft.ElevatedButton(
            text="اختيار صورة شخصية",
            icon=ft.icons.UPLOAD_FILE,
            on_click=self.pick_image,
        )

        # عرض الصورة المختارة
        self.image_preview = ft.Container(
            width=100,
            height=100,
            border_radius=50,
            bgcolor=ft.Colors.GREY_300,
            content=ft.Icon(name=ft.icons.PERSON, size=50, color=ft.Colors.GREY_600),
            alignment=ft.alignment.center,
        )
        if self.image_data:
            self.image_preview.content = ft.Image(
                src_base64=self.image_data,
                width=100,
                height=100,
                fit=ft.ImageFit.COVER,
            )

        # زر الحفظ
        save_button = ft.ElevatedButton(
            text="💾 حفظ البيانات",
            on_click=self.save_data,
        )

        # زر الرجوع
        back_button = ft.TextButton(
            text="🔙 رجوع",
            on_click=lambda e: self.page.go("/"),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("تعديل البيانات", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row([self.image_preview], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.image_button], alignment=ft.MainAxisAlignment.CENTER),
                    self.name_field,
                    self.primary_phone_field,
                    self.extra_phones_field,
                    self.primary_email_field,
                    self.extra_emails_field,
                    self.social_field,
                    ft.Row([save_button, back_button], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        )

    def pick_image(self, e):
        """اختيار صورة من المعرض"""
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()

        def on_result(result):
            if result.files:
                file_path = result.files[0].path
                if file_path:
                    with open(file_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode()
                        self.image_data = img_data
                        self.image_preview.content = ft.Image(
                            src_base64=img_data,
                            width=100,
                            height=100,
                            fit=ft.ImageFit.COVER,
                        )
                        self.image_preview.update()
                        self.page.update()

        file_picker.on_result = on_result
        file_picker.pick_files(allow_multiple=False)

    def save_data(self, e):
        """حفظ البيانات والعودة للصفحة الرئيسية"""
        name = self.name_field.value or ""
        primary_phone = self.primary_phone_field.value or ""
        if not name or not primary_phone:
            self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ الاسم ورقم الواتساب إلزاميان"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        extra_phones = [p.strip() for p in self.extra_phones_field.value.split(",") if p.strip()]
        primary_email = self.primary_email_field.value or ""
        extra_emails = [e.strip() for e in self.extra_emails_field.value.split(",") if e.strip()]
        social_media = {}
        for item in self.social_field.value.split(","):
            if ":" in item:
                parts = item.split(":", 1)
                social_media[parts[0].strip()] = parts[1].strip()

        # إنشاء كائن البيانات
        self.contact = ContactData(
            name=name,
            primary_phone=primary_phone,
            extra_phones=extra_phones,
            primary_email=primary_email,
            extra_emails=extra_emails,
            social_media=social_media,
            image_data=self.image_data,
        )

        # حفظ البيانات في session
        self.page.session.set("contact_data", self.contact.to_json())

        # العودة للصفحة الرئيسية مع البيانات الجديدة
        self.page.go("/")

# --- صفحة مسح الكود ---
class ScanPage(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.scan_result = None
        self.is_scanning = False

    def build(self):
        self.result_text = ft.Text("", size=16)

        # زر فتح الكاميرا
        self.scan_button = ft.ElevatedButton(
            text="📷 فتح الكاميرا لمسح الكود",
            icon=ft.icons.CAMERA_ALT,
            on_click=self.start_scan,
        )

        # زر الرجوع
        back_button = ft.TextButton(
            text="🔙 رجوع",
            on_click=lambda e: self.page.go("/"),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("مسح كود QR", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("استخدم كاميرا هاتفك لمسح أي كود QR", size=14, color=ft.Colors.GREY_600),
                    ft.Divider(height=20),
                    ft.Row([self.scan_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20),
                    ft.Container(
                        content=self.result_text,
                        padding=10,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=10,
                        width=350,
                    ),
                    ft.Row([back_button], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        )

    def start_scan(self, e):
        """بدء عملية المسح باستخدام الكاميرا"""
        if self.is_scanning:
            return

        # نعرض رسالة توضيحية
        self.result_text.value = "📸 جاري فتح الكاميرا... امسح الكود"
        self.result_text.color = ft.Colors.BLUE_400
        self.result_text.update()

        # نفتح الكاميرا باستخدام FilePicker (لأن فليت لا يدعم الكاميرا مباشرة)
        # بدلاً من ذلك، نستخدم FilePicker لالتقاط صورة من الكاميرا
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()

        def on_result(result):
            if result.files:
                file_path = result.files[0].path
                if file_path:
                    self.decode_qr_from_image(file_path)

        file_picker.on_result = on_result
        # نطلب من المستخدم التقاط صورة للكود
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])

    def decode_qr_from_image(self, image_path):
        """فك تشفير الكود من صورة"""
        try:
            # نحاول استخدام مكتبة pyzbar إن وجدت، وإلا نعرض رسالة
            try:
                from pyzbar.pyzbar import decode
                from PIL import Image
                img = Image.open(image_path)
                decoded = decode(img)
                if decoded:
                    data = decoded[0].data.decode('utf-8')
                    self.show_scanned_data(data)
                else:
                    self.result_text.value = "❌ لم يتم العثور على كود QR في الصورة"
                    self.result_text.color = ft.Colors.RED_400
                    self.result_text.update()
            except ImportError:
                # محاكاة فك التشفير (لأغراض العرض)
                self.result_text.value = "⚠️ يلزم تثبيت مكتبة pyzbar: pip install pyzbar"
                self.result_text.color = ft.Colors.ORANGE_400
                self.result_text.update()
        except Exception as ex:
            self.result_text.value = f"❌ خطأ: {str(ex)}"
            self.result_text.color = ft.Colors.RED_400
            self.result_text.update()

    def show_scanned_data(self, data):
        """عرض البيانات المستخرجة من الكود"""
        # نحاول تحليل البيانات كـ JSON
        contact = None
        try:
            contact = ContactData.from_json(data)
        except:
            # نحاول كـ vCard
            pass

        if contact and contact.name:
            # عرض البيانات بشكل منظم
            lines = [
                f"👤 {contact.name}",
                f"📱 واتساب: {contact.primary_phone}",
            ]
            if contact.extra_phones:
                lines.append(f"📞 أرقام إضافية: {', '.join(contact.extra_phones)}")
            if contact.primary_email:
                lines.append(f"✉️ {contact.primary_email}")
            if contact.extra_emails:
                lines.append(f"📧 بريد إضافي: {', '.join(contact.extra_emails)}")
            if contact.social_media:
                social_text = ", ".join([f"{p}: {h}" for p, h in contact.social_media.items()])
                lines.append(f"🌐 {social_text}")

            self.result_text.value = "\n".join(lines)
            self.result_text.color = ft.Colors.GREEN_700
            self.result_text.update()

            # عرض رسالة نجاح
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ تم قراءة البيانات بنجاح!"))
            self.page.snack_bar.open = True
            self.page.update()
        else:
            # عرض البيانات الخام
            self.result_text.value = f"📄 البيانات:\n{data}"
            self.result_text.color = ft.Colors.BLUE_700
            self.result_text.update()

# --- التطبيق الرئيسي ---
def main(page: ft.Page):
    page.title = "بطاقتي الرقمية"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # تحميل البيانات المحفوظة
    saved_data = page.session.get("contact_data")
    contact = None
    if saved_data:
        try:
            contact = ContactData.from_json(saved_data)
        except:
            pass

    # إنشاء الصفحات
    main_page = MainPage(page, contact)
    edit_page = EditPage(page, contact)
    scan_page = ScanPage(page)

    def route_change(route):
        page.controls.clear()
        if page.route == "/":
            # تحديث الصفحة الرئيسية بالبيانات الجديدة
            saved = page.session.get("contact_data")
            if saved:
                try:
                    new_contact = ContactData.from_json(saved)
                    main_page.contact = new_contact
                    # تحديث الواجهة
                    main_page.name_text.value = new_contact.name or "اسم المستخدم"
                    main_page.whatsapp_button.visible = bool(new_contact.primary_phone)
                    # تحديث باقي العناصر...
                except:
                    pass
            page.add(main_page)
        elif page.route == "/edit":
            # تمرير البيانات الحالية لصفحة التعديل
            saved = page.session.get("contact_data")
            if saved:
                try:
                    edit_page.contact = ContactData.from_json(saved)
                    edit_page.image_data = edit_page.contact.image_data
                except:
                    pass
            page.add(edit_page)
        elif page.route == "/scan":
            page.add(scan_page)
        page.update()

    page.on_route_change = route_change
    page.go("/")

# تشغيل التطبيق
ft.app(target=main)
