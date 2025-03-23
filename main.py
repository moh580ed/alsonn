from flet import *
import os
import websockets
import asyncio
import json
import aiohttp
from datetime import datetime
import threading




PRIMARY_COLOR = colors.BLUE_800
SECONDARY_COLOR = colors.GREY_200
ACCENT_COLOR = colors.AMBER_600

def create_appbar(root):
    return AppBar(
        title=Text('الألسن للعلوم الحديثة', color=colors.WHITE, size=25, weight=FontWeight.BOLD),
        bgcolor=PRIMARY_COLOR,
        center_title=True,
        elevation=10,
        leading=Icon(icons.SCHOOL, color=colors.WHITE, size=30),
        actions=[
            PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(text="الملف الشخصي", on_click=lambda _: root.go("/الصفحه الراسية"), icon=icons.PERSON),
                    PopupMenuItem(text="الإعدادات", icon=icons.SETTINGS),
                    PopupMenuItem(text="النتيجة", on_click=lambda _: root.go("/النتيجه"), icon=icons.GRADE),
                    PopupMenuItem(text="الشات", on_click=lambda _: root.go("/الشات"), icon=icons.CHAT_BUBBLE),
                    PopupMenuItem(text="الموقع الرسمي", icon=icons.WEB),
                    PopupMenuItem(text="من نحن", icon=icons.INFO),
                    PopupMenuItem(text="المساعدة", on_click=lambda _: root.go("/المساعدة"), icon=icons.HELP),
                    PopupMenuItem(text="تسجيل الخروج", on_click=lambda _: root.go("/"), icon=icons.LOGOUT),
                ]
            )
        ]
    )

def main(root: Page):
    root.title = 'Alson Education'
    root.theme_mode = ThemeMode.LIGHT
    root.bgcolor = SECONDARY_COLOR
    root.padding = 0

    username_field = TextField(
        label="اسم الطالب",
        prefix_icon=icons.PERSON,
        border_radius=15,
        bgcolor=colors.WHITE,
        width=0.8 * root.width if root.width else 320,
        text_style=TextStyle(size=16),
        border_color=PRIMARY_COLOR
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def create_view(route, content):
        return View(
            route,
            [
                create_appbar(root),
                Container(
                    content=content,
                    padding=15,
                    bgcolor=SECONDARY_COLOR,
                    expand=True
                )
            ],
            vertical_alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            bgcolor=SECONDARY_COLOR,
            scroll="auto"  
        )

    def route_change(route):
        root.views.clear()

        if root.route == "/":
            student_code = TextField(
                label="كود الطالب",
                prefix_icon=icons.LOCK,
                password=True,
                can_reveal_password=True,
                border_radius=15,
                bgcolor=colors.WHITE,
                width=0.8 * root.width if root.width else 320,
                border_color=PRIMARY_COLOR
            )
            
            def validate_login(e):
                if username_field.value.strip() and student_code.value.strip():
                    root.go("/الصفحه الراسية")
                else:
                    root.snack_bar = SnackBar(Text("يرجى إدخال جميع الحقول", color=colors.RED), open=True)
                    root.update()

            root.views.append(
                create_view(
                    "/",
                    Column(
                        [
                            Image(src="img/icon.png", width=0.4 * root.width if root.width else 150, fit=ImageFit.CONTAIN),
                            Text("مرحبًا بك في الألسن!", size=30, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                            username_field,
                            student_code,
                            ElevatedButton(
                                "تسجيل الدخول",
                                on_click=validate_login,
                                width=0.5 * root.width if root.width else 200,
                                height=50,
                                style=ButtonStyle(
                                    bgcolor=PRIMARY_COLOR,
                                    color=colors.WHITE,
                                    shape=RoundedRectangleBorder(radius=12),
                                    elevation=5
                                )
                            ),
                            TextButton("هل نسيت كود الطالب؟", style=ButtonStyle(color=PRIMARY_COLOR))
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  
                    )
                )
            )

        elif root.route == "/الصفحه الراسية":
            root.views.append(
                create_view(
                    "/الصفحه الراسية",
                    Column(
                        [
                            Text(f"مرحباً {username_field.value or 'الطالب'}", size=24, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                            Card(
                                content=Container(
                                    Column([
                                        Text("جدول المحاضرات اليوم", size=18, weight=FontWeight.BOLD),
                                        Image(src="img/po.jpg", width=0.9 * root.width if root.width else 340, fit=ImageFit.COVER),
                                        Text("الإثنين 22 مارس 2025", size=14, color=colors.GREY_600),
                                    ]),
                                    padding=10
                                ),
                                elevation=8,
                                shape=RoundedRectangleBorder(radius=15)
                            ),
                            ResponsiveRow([
                                ElevatedButton(
                                    "عرض النتيجة",
                                    on_click=lambda _: root.go("/النتيجه"),
                                    style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=colors.WHITE),
                                    col={"xs": 6, "md": 4}
                                ),
                                ElevatedButton(
                                    "الواجبات",
                                    style=ButtonStyle(bgcolor=ACCENT_COLOR, color=colors.WHITE),
                                    col={"xs": 6, "md": 4}
                                )
                            ])
                        ],
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  # إضافة التمرير للعمود
                    )
                )
            )

        elif root.route == "/النتيجه":
            student_id = TextField(
                label="رقم الجلوس",
                prefix_icon=icons.NUMBERS,
                border_radius=15,
                bgcolor=colors.WHITE,
                width=0.8 * root.width if root.width else 320,
                keyboard_type=KeyboardType.NUMBER,
                border_color=PRIMARY_COLOR
            )
            
            def show_results(e):
                if student_id.value.strip():
                    root.go("/عرض النتيجة")
                else:
                    root.snack_bar = SnackBar(Text("يرجى إدخال رقم الجلوس", color=colors.RED), open=True)
                    root.update()

            root.views.append(
                create_view(
                    "/النتيجه",
                    Column(
                        [
                            Text("استعلام النتائج", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                            Card(
                                content=Container(
                                    Column([
                                        student_id,
                                        Text("تأكد من إدخال رقم الجلوس الصحيح", size=14, color=colors.GREY_600),
                                    ]),
                                    padding=10
                                ),
                                elevation=5,
                                shape=RoundedRectangleBorder(radius=15),
                                width=0.9 * root.width if root.width else 340
                            ),
                            ElevatedButton(
                                "عرض النتيجة",
                                on_click=show_results,
                                width=0.5 * root.width if root.width else 200,
                                style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=colors.WHITE, shape=RoundedRectangleBorder(radius=12))
                            )
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  # إضافة التمرير للعمود
                    )
                )
            )

        elif root.route == "/عرض النتيجة":
            root.views.append(
                create_view(
                    "/عرض النتيجة",
                    Column(
                        [
                            Text("نتائج الامتحانات", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                            Card(
                                content=Container(
                                    Column([
                                        Text(f"الاسم: {username_field.value}", size=16),
                                        Divider(),
                                        Text("الرياضيات: 85/100", size=14),
                                        Text("العلوم: 92/100", size=14),
                                        Text("اللغة العربية: 88/100", size=14),
                                    ]),
                                    padding=15
                                ),
                                elevation=5,
                                shape=RoundedRectangleBorder(radius=15),
                                width=0.9 * root.width if root.width else 340
                            ),
                            ElevatedButton(
                                "عودة",
                                on_click=lambda _: root.go("/النتيجه"),
                                width=0.5 * root.width if root.width else 200,
                                style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=colors.WHITE)
                            )
                        ],
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  # إضافة التمرير للعمود
                    )
                )
            )

        elif root.route == "/المساعدة":
            root.views.append(
                create_view(
                    "/المساعدة",
                    Column(
                        [
                            Text("مركز المساعدة", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                            Card(
                                content=Container(
                                    Column([
                                        Text("تواصلوا معنا", size=18, weight=FontWeight.BOLD),
                                        Text("البريد: support@alson.edu", size=14),
                                        Text("الهاتف: 0123456789", size=14),
                                        Divider(),
                                        Text("ساعات العمل: 8 صباحاً - 4 مساءً", size=14),
                                    ]),
                                    padding=15
                                ),
                                elevation=5,
                                shape=RoundedRectangleBorder(radius=15),
                                width=0.9 * root.width if root.width else 340
                            ),
                            Image(src="img/po.jpg", width=0.9 * root.width if root.width else 340, fit=ImageFit.COVER)
                        ],
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  # إضافة التمرير للعمود
                    )
                )
            )

        elif root.route == "/الشات":
            message_input = TextField(
                label="اكتب رسالتك...",
                border_radius=15,
                bgcolor=colors.WHITE,
                width=0.75 * root.width if root.width else 300,
                multiline=True,
                max_lines=3,
                border_color=PRIMARY_COLOR,
                text_style=TextStyle(size=14)
            )
            chat_container = Container(
                content=Column([], scroll="auto"),  # التمرير موجود بالفعل هنا
                expand=True,
                bgcolor=colors.WHITE,
                border_radius=15,
                padding=10,
                height=0.7 * root.height if root.height else 450
            )

            def update_chat(messages):
                chat_container.content.controls = [
                    Container(
                        content=Row([
                            Container(
                                Text(f"{msg['username']}", size=14, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                                padding=padding.only(left=10)
                            ),
                            Container(
                                Text(msg["message"], size=14, color=colors.BLACK87),
                                bgcolor=colors.GREY_100,
                                padding=10,
                                border_radius=10,
                                expand=True
                            ),
                            Text(msg["timestamp"][-8:], size=12, color=colors.GREY_600)
                        ], alignment=MainAxisAlignment.START),
                        margin=margin.symmetric(vertical=5)
                    ) for msg in messages if isinstance(msg, dict)
                ]
                chat_container.content.controls.reverse()
                root.update()

            async def connect_websocket(chat_container, root):
                uri = "ws://127.0.0.1:8000/ws"
                while True:
                    try:
                        async with websockets.connect(uri) as websocket:
                            async with aiohttp.ClientSession() as session:
                                async with session.get("http://127.0.0.1:8000/messages") as resp:
                                    if resp.status == 200:
                                        messages = await resp.json()
                                        update_chat(messages)
                            while True:
                                try:
                                    msg = await websocket.recv()
                                    message_data = json.loads(msg)
                                    current_messages = [
                                        {
                                            "username": m.content.controls[0].content.value,
                                            "message": m.content.controls[1].content.value,
                                            "timestamp": m.content.controls[2].value
                                        } for m in chat_container.content.controls
                                    ]
                                    update_chat([message_data] + current_messages)
                                except websockets.ConnectionClosed:
                                    break
                    except Exception as e:
                        print(f"WebSocket Error: {e}")
                        root.snack_bar = SnackBar(Text("فشل الاتصال بالشات", color=colors.RED), open=True)
                        root.update()
                        await asyncio.sleep(2)

            async def send_message(message):
                uri = "ws://127.0.0.1:8000/ws"
                try:
                    async with websockets.connect(uri) as websocket:
                        message_data = {
                            "username": username_field.value or "مجهول",
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send(json.dumps(message_data))
                except Exception as e:
                    print(f"Send Error: {e}")
                    root.snack_bar = SnackBar(Text("فشل إرسال الرسالة", color=colors.RED), open=True)
                    root.update()

            def start_websocket():
                def run_websocket():
                    asyncio.set_event_loop(asyncio.new_event_loop())
                    asyncio.get_event_loop().run_until_complete(connect_websocket(chat_container, root))
                
                websocket_thread = threading.Thread(target=run_websocket, daemon=True)
                websocket_thread.start()

            def send_message_handler(e):
                if message_input.value.strip():
                    asyncio.run_coroutine_threadsafe(send_message(message_input.value), loop)
                    message_input.value = ""
                    root.update()

            start_websocket()

            root.views.append(
                create_view(
                    "/الشات",
                    Column(
                        [
                            Text("غرفة الشات", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                            chat_container,
                            ResponsiveRow([
                                message_input,
                                IconButton(
                                    icon=icons.SEND,
                                    bgcolor=PRIMARY_COLOR,
                                    icon_color=colors.WHITE,
                                    on_click=send_message_handler,
                                    tooltip="إرسال",
                                    col={"xs": 2}
                                )
                            ], alignment=MainAxisAlignment.CENTER)
                        ],
                        spacing=15,
                        expand=True,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  # إضافة التمرير للعمود
                    )
                )
            )

        else:
            root.views.append(
                create_view(
                    root.route,
                    Column(
                        [
                            Text("الصفحة غير موجودة", size=20, color=colors.RED),
                            ElevatedButton(
                                "العودة للرئيسية",
                                on_click=lambda _: root.go("/الصفحه الراسية"),
                                width=0.5 * root.width if root.width else 200,
                                style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=colors.WHITE)
                            )
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        scroll="auto"  # إضافة التمرير للعمود
                    )
                )
            )
        
        root.update()

    def root_go(view):
        if len(root.views) > 1:
            root.views.pop()
            back_page = root.views[-1]
            root.go(back_page.route)

    root.on_route_change = route_change
    root.on_view_pop = root_go
    root.go(root.route)

app(target=main, assets_dir='assets')
