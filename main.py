import sqlite3
import csv
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

# Android specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path

# Settings
Window.clearcolor = (1, 1, 1, 1)

# --- Path Helper Functions ---
def get_db_path():
    if platform == 'android':
        return os.path.join(app_storage_path(), "stdid.db")
    return "stdid.db"

def get_export_path(filename):
    if platform == 'android':
        # Android ke 'Download' folder mein file save hogi
        return os.path.join("/sdcard/Download", filename)
    return filename

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS stdid (
                    sid TEXT PRIMARY KEY, sname TEXT, scourse TEXT, sbatch_time TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS attrec (
                    sid TEXT, sname TEXT, scourse TEXT, sbatch_time TEXT,
                    in_date TEXT, in_time TEXT, out_date TEXT, out_time TEXT, status TEXT)""")
    conn.commit()
    conn.close()

init_db()

# --- Shared UI Components ---
def get_btn(txt, color=(0.1, 0.5, 0.9, 1)):
    return Button(text=txt, size_hint=(None, None), size=(250, 50),
                  pos_hint={'center_x': 0.5}, background_normal='', background_color=color)

# --- HOME SCREEN ---
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.time_label = Label(text="", font_size='18sp', color=(0, 0, 0, 1), size_hint_y=None, height=40)
        Clock.schedule_interval(self.update_time, 1)
        layout.add_widget(self.time_label)
        layout.add_widget(Label(text="Expertedu", font_size='40sp', bold=True, color=(0, 0, 0, 1)))
        
        admin_btn = get_btn("Admin")
        admin_btn.bind(on_press=self.show_pwd)
        layout.add_widget(admin_btn)

        layout.add_widget(Label(size_hint_y=None, height=20))
        self.att_id = TextInput(hint_text="Enter the center id", size_hint=(None, None), size=(280, 45), pos_hint={'center_x':0.5}, multiline=False)
        mark_btn = get_btn("Mark Attendance", (0.1, 0.7, 0.3, 1))
        mark_btn.bind(on_press=self.process_att)
        
        layout.add_widget(self.att_id); layout.add_widget(mark_btn); layout.add_widget(Label())
        self.add_widget(layout)

    def update_time(self, *args): self.time_label.text = datetime.now().strftime("%d %B %Y | %I:%M %p")
    
    def show_pwd(self, x):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.pwd = TextInput(hint_text="Password", password=True, multiline=False)
        btn = Button(text="Login", background_color=(0.1, 0.8, 0.1, 1), size_hint_y=None, height=50)
        btn.bind(on_press=self.check_pwd)
        content.add_widget(self.pwd); content.add_widget(btn)
        self.pop = Popup(title="Security", content=content, size_hint=(0.8, 0.3)); self.pop.open()

    def check_pwd(self, x):
        if self.pwd.text == "core": self.pop.dismiss(); self.manager.current='admin_panel'
        else: Popup(title="Error", content=Label(text="Wrong Password"), size_hint=(0.6, 0.2)).open()

    def process_att(self, x):
        sid = self.att_id.text.strip()
        if not sid: return
        conn = sqlite3.connect(get_db_path()); cur = conn.cursor()
        cur.execute("SELECT * FROM stdid WHERE sid=?", (sid,))
        student = cur.fetchone()
        if not student:
            Popup(title="Error", content=Label(text="no id found"), size_hint=(0.6, 0.2)).open()
            self.att_id.text = ""; conn.close(); return
        
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT * FROM attrec WHERE sid=? AND in_date=? AND out_time=''", (sid, today))
        entry = cur.fetchone(); conn.close()
        self.show_det(student, entry)

    def show_det(self, student, entry):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        details = [f"ID: {student[0]}", f"Name: {student[1]}", f"Course: {student[2]}", f"Batch: {student[3]}"]
        for d in details: content.add_widget(Label(text=d))
        
        btn_txt = "Mark Out" if entry else "Mark In"
        btn_color = (1,0,0,1) if entry else (0,1,0,1)
        btn = Button(text=btn_txt, background_color=btn_color, size_hint_y=None, height=50)
        btn.bind(on_press=lambda x: self.do_mark(student, entry))
        content.add_widget(btn)
        self.det_pop = Popup(title="Details", content=content, size_hint=(0.8, 0.5)); self.det_pop.open()

    def do_mark(self, std, entry):
        now = datetime.now()
        conn = sqlite3.connect(get_db_path()); cur = conn.cursor()
        if not entry:
            cur.execute("INSERT INTO attrec VALUES (?,?,?,?,?,?,?,?,?)", 
                        (std[0], std[1], std[2], std[3], now.strftime("%Y-%m-%d"), now.strftime("%I:%M %p"), "", "", "present"))
        else:
            cur.execute("UPDATE attrec SET out_date=?, out_time=? WHERE sid=? AND in_date=? AND out_time=''", 
                        (now.strftime("%Y-%m-%d"), now.strftime("%I:%M %p"), std[0], now.strftime("%Y-%m-%d")))
        conn.commit(); conn.close(); self.det_pop.dismiss(); self.att_id.text = ""
        Popup(title="Success", content=Label(text="you are marked"), size_hint=(0.6, 0.2)).open()

# --- ADMIN PANEL ---
class AdminPanel(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=15)
        layout.add_widget(Label(text="Admin Panel", font_size='32sp', bold=True, color=(0,0,0,1)))
        
        b1 = get_btn("Register"); b1.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        b2 = get_btn("Show Attendance"); b2.bind(on_press=lambda x: setattr(self.manager, 'current', 'records_menu'))
        b3 = get_btn("Delete Record", (1, 0.5, 0, 1)); b3.bind(on_press=self.del_pop_show)
        b4 = get_btn("Logout", (0.9, 0.2, 0.2, 1)); b4.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        for b in [b1, b2, b3, b4]: layout.add_widget(b)
        self.add_widget(layout)

    def del_pop_show(self, x):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.di = TextInput(hint_text="ID to Delete", multiline=False)
        btn = Button(text="Confirm", background_color=(1,0,0,1), size_hint_y=None, height=50)
        btn.bind(on_press=self.delete)
        content.add_widget(self.di); content.add_widget(btn)
        self.dp = Popup(title="Delete", content=content, size_hint=(0.8, 0.3)); self.dp.open()

    def delete(self, x):
        conn = sqlite3.connect(get_db_path()); cur = conn.cursor()
        cur.execute("DELETE FROM stdid WHERE sid=?", (self.di.text.strip(),))
        conn.commit(); conn.close(); self.dp.dismiss()
        Popup(title="Done", content=Label(text="Deleted"), size_hint=(0.6, 0.2)).open()

# --- ATTENDANCE RECORDS MENU ---
class RecordsMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="Attendance Records", font_size='28sp', bold=True, color=(0,0,0,1)))
        
        btns = [("Date wise", "date"), ("Month wise", "month"), ("Name wise", "name"), ("Batch wise", "batch")]
        for txt, mode in btns:
            b = get_btn(txt)
            b.bind(on_press=lambda x, m=mode: self.ask_input(m))
            layout.add_widget(b)
            
        back = get_btn("Back", (0.6, 0.6, 0.6, 1))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_panel'))
        layout.add_widget(back); self.add_widget(layout)

    def ask_input(self, mode):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        hints = {"date":"YYYY-MM-DD", "month":"MM-YYYY", "name":"Enter Name", "batch":"Enter Batch Time"}
        self.inp = TextInput(hint_text=hints[mode], multiline=False)
        btn = Button(text="Search", background_color=(0.1, 0.8, 0.1, 1), size_hint_y=None, height=50)
        btn.bind(on_press=lambda x: self.start_search(mode))
        content.add_widget(self.inp); content.add_widget(btn)
        self.sp = Popup(title=f"Search {mode}", content=content, size_hint=(0.8, 0.3)); self.sp.open()

    def start_search(self, mode):
        val = self.inp.text.strip()
        self.sp.dismiss()
        self.manager.get_screen('display_records').fetch_data(mode, val)
        self.manager.current = 'display_records'

# --- DATA DISPLAY SCREEN ---
class DisplayRecordsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=9, size_hint_y=None, spacing=2)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        self.stats_label = Label(text="", size_hint_y=None, height=40, color=(0,0,0,1), bold=True)
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.export_btn = Button(text="Export CSV", background_color=(0.1, 0.7, 0.3, 1))
        self.export_btn.bind(on_press=self.export_data)
        close_btn = Button(text="Close", background_color=(0.9, 0.2, 0.2, 1))
        close_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_panel'))
        
        btn_box.add_widget(self.export_btn); btn_box.add_widget(close_btn)
        self.layout.add_widget(self.scroll); self.layout.add_widget(self.stats_label); self.layout.add_widget(btn_box)
        self.add_widget(self.layout); self.current_data = []

    def fetch_data(self, mode, val):
        self.grid.clear_widgets()
        headers = ["ID", "Name", "Course", "Batch", "In Date", "In Time", "Out Date", "Out Time", "Status"]
        for h in headers: self.grid.add_widget(Label(text=h, color=(0,0,0,1), bold=True, size_hint_y=None, height=40))
        
        conn = sqlite3.connect(get_db_path()); cur = conn.cursor()
        if mode == "date": query = "SELECT * FROM attrec WHERE in_date=? OR out_date=?"
        elif mode == "month": query = "SELECT * FROM attrec WHERE in_date LIKE ? OR out_date LIKE ?"
        elif mode == "name": query = "SELECT * FROM attrec WHERE sname LIKE ?"
        elif mode == "batch": query = "SELECT * FROM attrec WHERE sbatch_time=?"
        
        params = (f"%{val}%", f"%{val}%") if mode == "month" else (f"%{val}%",) if mode == "name" else (val,) if mode == "batch" else (val, val)
        cur.execute(query, params)
        self.current_data = cur.fetchall(); conn.close()
        
        present_count = sum(1 for row in self.current_data if row[8].lower() == "present")
        for row in self.current_data:
            for item in row: self.grid.add_widget(Label(text=str(item), color=(0.4,0.4,0.4,1), size_hint_y=None, height=35))
        
        self.scroll.clear_widgets(); self.scroll.add_widget(self.grid)
        self.stats_label.text = f"Total Records: {len(self.current_data)} | Total Present: {present_count}"

    def export_data(self, x):
        if not self.current_data: return
        filename = f"Attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        target_path = get_export_path(filename)
        
        try:
            with open(target_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Course", "Batch", "In Date", "In Time", "Out Date", "Out Time", "Status"])
                writer.writerows(self.current_data)
            Popup(title="Success", content=Label(text=f"Saved to Downloads!"), size_hint=(0.7, 0.2)).open()
        except Exception as e:
            Popup(title="Error", content=Label(text=f"Check Permissions"), size_hint=(0.8, 0.3)).open()

# --- REGISTER SCREEN ---
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=30, spacing=10)
        l.add_widget(Label(text="Registration", font_size='26sp', bold=True, color=(0,0,0,1)))
        self.i1 = TextInput(hint_text="ID"); self.i2 = TextInput(hint_text="Name")
        self.i3 = TextInput(hint_text="Course"); self.i4 = TextInput(hint_text="Batch Time")
        for i in [self.i1, self.i2, self.i3, self.i4]: 
            i.size_hint=(None,None); i.size=(300,45); i.pos_hint={'center_x':0.5}; l.add_widget(i)
        
        sub = get_btn("Submit"); sub.bind(on_press=self.save)
        back = get_btn("Back", (0.6,0.6,0.6,1)); back.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_panel'))
        l.add_widget(sub); l.add_widget(back); self.add_widget(l)

    def save(self, x):
        conn = sqlite3.connect(get_db_path()); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO stdid VALUES (?,?,?,?)", (self.i1.text, self.i2.text, self.i3.text, self.i4.text))
            conn.commit(); Popup(title="Success", content=Label(text="Registered"), size_hint=(0.6, 0.2)).open()
        except:
            cur.execute("UPDATE stdid SET sname=?, scourse=?, sbatch_time=? WHERE sid=?", (self.i2.text, self.i3.text, self.i4.text, self.i1.text))
            conn.commit(); Popup(title="Updated", content=Label(text="ID Updated"), size_hint=(0.6, 0.2)).open()
        conn.close()

# --- MAIN APP CLASS ---
class AttendanceApp(App):
    def build(self):
        # Android Back Button Handle
        Window.bind(on_keyboard=self.on_key)
        
        if platform == 'android':
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AdminPanel(name='admin_panel'))
        sm.add_widget(RecordsMenu(name='records_menu'))
        sm.add_widget(DisplayRecordsScreen(name='display_records'))
        sm.add_widget(RegisterScreen(name='register'))
        return sm

    def on_key(self, window, key, *args):
        if key == 27: # Back button
            if self.root.current == 'home': return False
            self.root.current = 'home'
            return True

if __name__ == '__main__':
    AttendanceApp().run()