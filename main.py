
import json, os, base64
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

Window.size = (390, 800)

DATA_FILE = 'zahraa_data.json'

GROUPS = [
    "اول اعدادي سبت ثلاثاء 2ظ بداية 8",
    "اول اعدادي احد اربعاء 2ظ بداية 8",
    "تاني اعدادي سبت ثلاثاء 3ع بداية 8",
    "تاني اعدادي احد اربعاء 3ع بداية 8",
    "تالت اعدادي سبت ثلاثاء 4ع بداية 8",
    "تالت اعدادي احد اربعاء 4ع بداية 8",
    "ث عام سبت ثلاثاء 7 بداية 8",
    "ث علمي سبت ثلاثاء 8 بداية 8",
    "ث ادبي اثنين خميس 2 بداية 8",
    "ث احصاء ادبي اثنين خميس 3 بداية 8",
    "ث رياضيات علمي رياضة اثنين خميس 4 بداية 8",
    "ث بكالوريا احد اربعاء 7",
    "ث مسار الطب احد اربعاء 8",
]

EXPENSE_TYPES = ["إيجار","كهرباء","مياه","طباعة وتصوير","صيانة","مرتبات","نظافة","دعاية","انتقالات","أخرى"]
PAY_TYPES = ["كاش في السنتر","انستاباي","محفظة فودافون","اتصالات كاش","تحويل"]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"students":[],"expenses":[],"payments":[],"attendance":[]}
    try:
        with open(DATA_FILE,'r',encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"students":[],"expenses":[],"payments":[],"attendance":[]}

def save_data(d):
    with open(DATA_FILE,'w',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

class HomeScreen(Screen):
    def on_enter(self):
        self.refresh()
    def refresh(self):
        self.clear_widgets()
        data = load_data()
        students = data.get('students',[])
        expenses = data.get('expenses',[])
        payments = data.get('payments',[])
        # حساب مالي
        total_in = sum([p.get('amount',0) for p in payments]) or sum([s.get('paid',0) for s in students])
        total_out = sum([e.get('amount',0) for e in expenses])
        net = total_in - total_out
        today = datetime.now().strftime("%Y-%m-%d")
        today_att = len([a for a in data.get('attendance',[]) if a.get('date')==today])

        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        root.add_widget(Label(text='[b][color=#d4af37]سنتر الزهراء فاطمة[/color][/b]\n[color=#ffffff]Realme C55 - Kivy App[/color]', markup=True, size_hint_y=None, height=dp(70)))

        kpi = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(160))
        for title,val,color in [
            (f"الطلاب\n[b]{len(students)}[/b]", str(len(students)), "#ffffff"),
            (f"المجموعات\n[b]{len(GROUPS)}[/b]", "13", "#ffffff"),
            (f"حضور اليوم\n[b]{today_att}[/b]", str(today_att), "#ffffff"),
            (f"صافي الربح\n[b]{net} جنيه[/b]", f"{net}", "#d4af37"),
        ]:
            b = BoxLayout(orientation='vertical')
            from kivy.uix.widget import Widget
            from kivy.graphics import Color, RoundedRectangle
            box = BoxLayout()
            with box.canvas.before:
                Color(0.04, 0.24, 0.18, 1) if "ربح" not in title else Color(0.04, 0.24, 0.18, 1)
                from kivy.graphics import RoundedRectangle
            lbl = Label(text=title, markup=True)
            kpi.add_widget(lbl)
        root.add_widget(kpi)

        fin = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, height=dp(110))
        fin.add_widget(Label(text=f"المدفوعات: {total_in} جنيه | المصروفات: {total_out} جنيه", font_size='13sp'))
        fin.add_widget(Label(text=f"[b]صافي الربح: {net} جنيه[/b]", markup=True, font_size='16sp', color=(0.83,0.68,0.21,1)))
        root.add_widget(fin)

        btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        btns.add_widget(Button(text='إضافة طالب', background_color=(0.83,0.68,0.21,1), on_press=lambda x: setattr(self.manager,'current','add_student')))
        btns.add_widget(Button(text='المجموعات', on_press=lambda x: setattr(self.manager,'current','groups')))
        root.add_widget(btns)

        # بحث سريع
        self.search = TextInput(hint_text='بحث بالاسم...', size_hint_y=None, height=dp(40), multiline=False)
        self.search.bind(text=lambda i,v: self.do_search(v))
        root.add_widget(self.search)

        scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)

        self.add_widget(root)
        self.do_search("")

    def do_search(self, q):
        data = load_data()
        students = data.get('students',[])
        if q:
            students = [s for s in students if q in s.get('name','')]
        self.list_layout.clear_widgets()
        for s in students[:50]:
            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
            row.add_widget(Label(text=s.get('name',''), halign='right'))
            row.add_widget(Label(text=s.get('group','')[:20], font_size='11sp'))
            row.add_widget(Label(text=f"{s.get('paid',0)}ج", font_size='12sp'))
            self.list_layout.add_widget(row)

class AddStudentScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text='إضافة طالب جديد', size_hint_y=None, height=dp(40), font_size='18sp', bold=True))
        self.name_in = TextInput(hint_text='اسم الطالب')
        self.phone_in = TextInput(hint_text='رقم الطالب', input_filter='int')
        self.parent_in = TextInput(hint_text='رقم ولي الأمر', input_filter='int')
        self.paid_in = TextInput(hint_text='المدفوع', input_filter='int')
        self.group_in = TextInput(hint_text='اختر مجموعة - اكتب رقم 1-13 أو الاسم')
        root.add_widget(self.name_in)
        root.add_widget(self.phone_in)
        root.add_widget(self.parent_in)
        root.add_widget(self.paid_in)
        root.add_widget(self.group_in)
        root.add_widget(Label(text='المجموعات: 1- اول اعدادي سبت... 13- مسار الطب', font_size='10sp', color=(0.5,0.5,0.5,1)))
        btn_save = Button(text='حفظ الطالب', background_color=(0.83,0.68,0.21,1), size_hint_y=None, height=dp(50))
        btn_save.bind(on_press=self.save)
        btn_back = Button(text='رجوع', size_hint_y=None, height=dp(44))
        btn_back.bind(on_press=lambda x: setattr(self.manager,'current','home'))
        root.add_widget(btn_save)
        root.add_widget(btn_back)
        self.add_widget(root)

    def save(self, *args):
        data = load_data()
        g = self.group_in.text.strip()
        if g.isdigit() and 1 <= int(g) <= len(GROUPS):
            g = GROUPS[int(g)-1]
        student = {
            "name": self.name_in.text,
            "phone": self.phone_in.text,
            "parent": self.parent_in.text,
            "paid": int(self.paid_in.text or 0),
            "group": g,
            "date": datetime.now().isoformat()
        }
        data['students'].append(student)
        data['payments'].append({"name":student['name'],"amount":student['paid'],"method":"كاش في السنتر","date":datetime.now().isoformat()})
        save_data(data)
        self.manager.current='home'

class GroupsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(Label(text='كل المجموعات (13)', size_hint_y=None, height=dp(50), bold=True))
        scroll = ScrollView()
        lay = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(10))
        lay.bind(minimum_height=lay.setter('height'))
        data = load_data()
        for i,g in enumerate(GROUPS,1):
            count = len([s for s in data.get('students',[]) if s.get('group')==g])
            btn = Button(text=f"{i}. {g} - {count} طالب", size_hint_y=None, height=dp(54), halign='right')
            lay.add_widget(btn)
        scroll.add_widget(lay)
        root.add_widget(scroll)
        back = Button(text='رجوع', size_hint_y=None, height=dp(50))
        back.bind(on_press=lambda x: setattr(self.manager,'current','home'))
        root.add_widget(back)
        self.add_widget(root)

class FinanceScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        data = load_data()
        total_in = sum([p.get('amount',0) for p in data.get('payments',[])]) or sum([s.get('paid',0) for s in data.get('students',[])])
        total_out = sum([e.get('amount',0) for e in data.get('expenses',[])])
        net = total_in-total_out
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        root.add_widget(Label(text=f'المالية - صافي الربح\n[b]{net} جنيه[/b]', markup=True, size_hint_y=None, height=dp(80)))
        # اضافة مصروف
        root.add_widget(Label(text='إضافة مصروف', size_hint_y=None, height=dp(30)))
        self.exp_type = TextInput(hint_text='نوع: إيجار، كهرباء...', size_hint_y=None, height=dp(40))
        self.exp_amount = TextInput(hint_text='المبلغ', input_filter='int', size_hint_y=None, height=dp(40))
        root.add_widget(self.exp_type)
        root.add_widget(self.exp_amount)
        btn = Button(text='إضافة مصروف', size_hint_y=None, height=dp(44), background_color=(0.83,0.68,0.21,1))
        btn.bind(on_press=self.add_exp)
        root.add_widget(btn)

        scroll = ScrollView()
        lay = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        lay.bind(minimum_height=lay.setter('height'))
        for e in data.get('expenses',[])[-20:]:
            lay.add_widget(Label(text=f"{e.get('type')} - {e.get('amount')} جنيه - {e.get('date','')[:10]}", size_hint_y=None, height=dp(30), font_size='12sp'))
        scroll.add_widget(lay)
        root.add_widget(scroll)

        back = Button(text='رجوع', size_hint_y=None, height=dp(50))
        back.bind(on_press=lambda x: setattr(self.manager,'current','home'))
        root.add_widget(back)
        self.add_widget(root)

    def add_exp(self,*a):
        data=load_data()
        data['expenses'].append({"type":self.exp_type.text,"amount":int(self.exp_amount.text or 0),"date":datetime.now().isoformat()})
        save_data(data)
        self.on_enter()

class SyncScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        root.add_widget(Label(text='المزامنة QR بين الأجهزة', bold=True, size_hint_y=None, height=dp(40)))
        self.code_box = TextInput(hint_text='كود المزامنة يظهر هنا...', size_hint_y=None, height=dp(120))
        root.add_widget(self.code_box)
        btn_gen = Button(text='توليد كود مزامنة (للإرسال)', background_color=(0.83,0.68,0.21,1), size_hint_y=None, height=dp(50))
        btn_gen.bind(on_press=self.gen)
        btn_imp = Button(text='استيراد كود من جهاز آخر', size_hint_y=None, height=dp(50))
        btn_imp.bind(on_press=self.imp)
        root.add_widget(btn_gen)
        root.add_widget(btn_imp)
        root.add_widget(Label(text='انسخ الكود وابعته واتساب للجهاز التاني\nالتطبيق التاني يعمل لصق واستيراد', font_size='11sp'))
        back = Button(text='رجوع', size_hint_y=None, height=dp(50))
        back.bind(on_press=lambda x: setattr(self.manager,'current','home'))
        root.add_widget(back)
        self.add_widget(root)

    def gen(self,*a):
        data=load_data()
        code = base64.b64encode(json.dumps(data,ensure_ascii=False).encode()).decode()[:8000]
        self.code_box.text = code
        self.code_box.hint_text = f"تم التوليد - {len(code)} حرف"

    def imp(self,*a):
        try:
            raw = base64.b64decode(self.code_box.text.encode()).decode()
            d=json.loads(raw)
            save_data(d)
            self.code_box.text="✅ تم الاستيراد بنجاح"
        except Exception as e:
            self.code_box.text=f"خطأ: {e}"

class ZahraaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddStudentScreen(name='add_student'))
        sm.add_widget(GroupsScreen(name='groups'))
        sm.add_widget(FinanceScreen(name='finance'))
        sm.add_widget(SyncScreen(name='sync'))

        # Bottom nav
        root = BoxLayout(orientation='vertical')
        root.add_widget(sm)

        nav = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(4), padding=dp(4))
        for txt,target in [('الرئيسية','home'),('المجموعات','groups'),('المالية','finance'),('مزامنة','sync')]:
            b=Button(text=txt, font_size='12sp')
            b.bind(on_press=lambda inst,t=target: setattr(sm,'current',t))
            nav.add_widget(b)
        root.add_widget(nav)
        return root

if __name__ == '__main__':
    ZahraaApp().run()
