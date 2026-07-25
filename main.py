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
from kivy.metrics import dp

# محاولة اصلاح العربي
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def ar(t):
        if not t: return ""
        try:
            return get_display(arabic_reshaper.reshape(str(t)))
        except:
            return str(t)
except:
    def ar(t): return str(t)

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

def load_data():
    if not os.path.exists(DATA_FILE): return {"students":[],"expenses":[],"payments":[],"attendance":[]}
    try:
        with open(DATA_FILE,'r',encoding='utf-8') as f: return json.load(f)
    except: return {"students":[],"expenses":[],"payments":[],"attendance":[]}

def save_data(d):
    with open(DATA_FILE,'w',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2)

class HomeScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.clear_widgets()
        data = load_data()
        students = data.get('students',[])
        expenses = data.get('expenses',[])
        payments = data.get('payments',[])
        total_in = sum([p.get('amount',0) for p in payments]) or sum([s.get('paid',0) for s in students])
        total_out = sum([e.get('amount',0) for e in expenses])
        net = total_in - total_out
        today = datetime.now().strftime("%Y-%m-%d")
        today_att = len([a for a in data.get('attendance',[]) if a.get('date')==today])

        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        root.add_widget(Label(text=ar('سنتر الزهراء فاطمة - Realme C55'), size_hint_y=None, height=dp(50), bold=True, font_size='18sp', color=(0.83,0.68,0.21,1)))

        kpi = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(160))
        kpi.add_widget(Label(text=ar(f"الطلاب\n{len(students)}")))
        kpi.add_widget(Label(text=ar(f"المجموعات\n{len(GROUPS)}")))
        kpi.add_widget(Label(text=ar(f"حضور اليوم\n{today_att}")))
        kpi.add_widget(Label(text=ar(f"صافي الربح\n{net} جنيه"), color=(0.83,0.68,0.21,1)))
        root.add_widget(kpi)

        root.add_widget(Label(text=ar(f"المدفوعات: {total_in} | المصروفات: {total_out}"), size_hint_y=None, height=dp(30), font_size='13sp'))

        btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        btns.add_widget(Button(text=ar('إضافة طالب'), background_color=(0.83,0.68,0.21,1), on_press=lambda x: setattr(self.manager,'current','add_student')))
        btns.add_widget(Button(text=ar('المجموعات'), on_press=lambda x: setattr(self.manager,'current','groups')))
        root.add_widget(btns)

        self.search = TextInput(hint_text=ar('بحث بالاسم...'), size_hint_y=None, height=dp(40), multiline=False)
        self.search.bind(text=lambda i,v: self.do_search(v))
        root.add_widget(self.search)

        scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.list
