from flet import *
 
################data bass##############





#########################
def main (root:Page):
    root.title = 'alson'
    root.window.height=740
    root.window.width=390
    root.window.top = 10
    root.window.left = 960
    root.theme_mode =ThemeMode.LIGHT
    root.scroll=True

    ########صفحة التسجيل########
    def route_change(route):
        root.views.clear()
        root.views.append(
            View(
                "/",
                [ 
                    AppBar(
                        title= Text('الأسن للعلوم الحديثة',color='white',size=23),
                        bgcolor= colors.BLUE,
                         center_title= True,
                         leading=Icon(icons.HOME),
                         leading_width=40,
                         actions=[
                             IconButton(icons.NOTIFICATIONS),
                             PopupMenuButton(
                                 items=[
                                     PopupMenuItem(text="المساعدة"),
                                      PopupMenuItem(text="من نحن"),
                                 ]
                             )
                        
                        ]
                        
                    
                       
                        ),
                     Row([
                        Image(src="img/icon.png", width=250),
                        
                        ],alignment=MainAxisAlignment.CENTER),
                        TextField(label='اسم الطلا ب',icon=icons.EMAIL),
                        TextField(label='كود الطلاب', icon=icons.PASSWORD,password=True,can_reveal_password=True),
                    
                    Row([
                        ElevatedButton("تسجيل الدخول" ,on_click=lambda _: root.go( "/الصفحه الراسية"),
                                       width=170,
                                       style=ButtonStyle(bgcolor='BLUE',color='white'))
                    ],alignment=MainAxisAlignment.CENTER)
                        
                    
                    
                ],
                 )
        )
        #############الصفحة الراسيه#######################
       
        if root.route == "/الصفحه الراسية":
            root.views.append(
            View(
                "/الصفحه الراسية",
                [
                     AppBar(
                        title= Text('الأسن للعلوم الحديثة' ,color='white'),
                        bgcolor= colors.BLUE,
                        center_title= True,
                        leading=Icon(icons.HOME),
                         leading_width=40,
            
                        
                         actions=[
                             IconButton(icons.NOTIFICATIONS),
                             PopupMenuButton(
                                 items=[
                                     PopupMenuItem(text="الملف الشخصي"),
                                     PopupMenuItem(text="الاعدات"),
                                     PopupMenuItem(text="النتيجة", on_click=lambda _: root.go( "/النتيجه")),
                                      PopupMenuItem(text="الموقع الرسمي"),
                                      PopupMenuItem(text="من نحن"),
                                      PopupMenuItem(text="المساعدة" ,on_click=...),
                                      
                                 ]
                             )
                        
                        ]
                        
                    
                        
                        
                       
                        ),
                    Row([
                        Text('جدول المحاضرات' ,size=25 ,color='black' ,text_align='CENTER')
                        ],alignment=MainAxisAlignment.CENTER),
                    Row([
                       
                        Image(src="img/po.jpg" ,width=360),
                    ],alignment=MainAxisAlignment.CENTER),
                     
               
                    Row([
                        ElevatedButton("عرض النتيجة",on_click=lambda _: root.go( "/النتيجه"),
                                       width=170,
                                       style=ButtonStyle(bgcolor='BLUE',color='white'))
                    ],alignment=MainAxisAlignment.CENTER)
                ],
                 )
        )
        if root.route == "/النتيجه":
            root.views.append(
            View(
                "/النتيجه",
                [
                     AppBar(
                        title= Text('الأسن للعلوم الحديثة' ,color='white'),
                        bgcolor= colors.BLUE,
                        center_title= True,
                        leading=Icon(icons.HOME),
                         leading_width=40,
                        
                         actions=[
                             IconButton(icons.NOTIFICATIONS),
                             PopupMenuButton(
                                 items=[
                                     PopupMenuItem(text="الملف الشخصي"),
                                     PopupMenuItem(text="الاعدات"),
                                      PopupMenuItem(text="من نحن"),
                                      PopupMenuItem(text="المساعدة"),
                                      PopupMenuItem(text="exit" ,)
                                 ]
                             )
                        
                        ]
                        
                    
                        
                        
                       
                        ),
                        TextField(label='رقم الجلوس'),
                    Row([
                        ElevatedButton("االنتيجة",on_click=lambda _: root.go(  "/عرض النتيجة"),
                                       width=170,
                                       style=ButtonStyle(bgcolor='BLUE',color='white'))
                    ],alignment=MainAxisAlignment.CENTER),
                ],
                 )
        )
        if root.route == "/عرض النتيجة":
            root.views.append(
            View(
                 "/عرض النتيجة",
                [
                     AppBar(
                        title= Text('الأسن للعلوم الحديثة' ,color='white'),
                        bgcolor= colors.BLUE,
                        center_title= True,
                        leading=Icon(icons.HOME),
                         leading_width=40,
                        
                         actions=[
                             IconButton(icons.NOTIFICATIONS),
                             PopupMenuButton(
                                 items=[
                                     PopupMenuItem(text="الملف الشخصي"),
                                     PopupMenuItem(text="الاعدات"),
                                     PopupMenuItem(text="النتيجة"),
                                      PopupMenuItem(text="من نحن"),
                                      PopupMenuItem(text="المساعدة"),
                                      PopupMenuItem(text='///////////////')
                                 ]
                             )
                        
                        ]
                        
                    
                        
                        
                       
                        ),
                       
                    Row([
                       Image(src='img/po.jpg' ,width=320)
                    ],alignment=MainAxisAlignment.CENTER),
                ],
                 )
        )            
        
    
        root.update()
    def root_go(view):
        root.views.pop()
        back_page = root.views[-1]
        root.go(back_page.route)
        
        
    root.on_route_change =route_change
    root.on_view_pop = root_go
    root.go(root.route)

def new_func(root):
    root.scroll = True

app(main)