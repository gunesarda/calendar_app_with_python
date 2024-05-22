import tkinter as tk
from tkinter import messagebox, ttk
import configparser
from tkcalendar import Calendar
from datetime import datetime, date

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Takvim Uygulaması")
        self.root.geometry("400x400")

        self.selected_date = None
        self.event_tags = []

        self.create_widgets()
        self.get_events()

    def create_widgets(self):
        self.calendar = Calendar(self.root, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.get_selected_date)

        self.event_entry = tk.Entry(self.root)
        self.event_entry.pack(pady=10)

        self.add_button = tk.Button(self.root, text="Etkinlik Ekle", command=self.add_event)
        self.add_button.pack(pady=5)

        self.delete_button = tk.Button(self.root, text="Etkinlik Sil", command=self.delete_event)
        self.delete_button.pack(pady=5)

        self.event_label = tk.Label(self.root, text="Etkinlikler:")
        self.event_label.pack(pady=5)

        self.event_listbox = tk.Listbox(self.root)
        self.event_listbox.pack(pady=5)

    def add_event(self):
        event_text = self.event_entry.get()
        if event_text and self.selected_date:
            if self.check_event_exist(self.selected_date):
                messagebox.showwarning("Uyarı", "Bu tarihe zaten bir etkinlik eklenmiş.")
            else:
                self.add_to_file(self.selected_date, event_text)
                self.event_entry.delete(0, 'end')
                self.selected_date = None
                self.get_events()
        else:
            messagebox.showwarning("Uyarı", "Lütfen tarih seçin ve etkinlik girin.")

    def delete_event(self):
        selected_index = self.event_listbox.curselection()
        if selected_index:
            event = self.event_listbox.get(selected_index)
            date_str = event.split(":")[0].strip()
            if messagebox.askyesno("Etkinlik Silme", f"{date_str} tarihindeki etkinliği silmek istiyor musunuz?"):
                self.remove_from_file(date_str)
                self.remove_event_from_calendar(date_str)
                self.get_events()
        else:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz etkinliği seçin.")

    def remove_event_from_calendar(self, date_str):
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        for tag in self.event_tags:
            if tag['date'] == event_date:
                self.calendar.tag_delete(tag['tag'])
                self.event_tags.remove(tag)

    def remove_from_file(self, date_str):
        config = configparser.ConfigParser()
        config.read('calendar.ini')
        config.remove_option('Events', date_str)
        with open('calendar.ini', 'w') as configfile:
            config.write(configfile)

    def add_to_file(self, date, event):
        config = configparser.ConfigParser()
        config.read('calendar.ini')
        if not config.has_section('Events'):
            config.add_section('Events')
        if config.has_option('Events', str(date)):
            events = config.get('Events', str(date))
            events += f"\n{event}"
        else:
            events = event
        config.set('Events', str(date), events)
        with open('calendar.ini', 'w') as configfile:
            config.write(configfile)

    def get_events(self):
        self.event_listbox.delete(0, tk.END)
        config = configparser.ConfigParser()
        config.read('calendar.ini')
        if config.has_section('Events'):
            event_dict = {}
            for key in config['Events']:
                event_date = datetime.strptime(key, '%Y-%m-%d').date()
                event_text = f"{key}: {config['Events'][key]}"
                event_dict[event_date] = event_text
                tag = f"event_{event_date}"
                self.calendar.calevent_create(event_date, text=event_text, tags=(tag,))
                self.calendar.tag_config(tag, background='lightgreen')
                self.event_tags.append({'date': event_date, 'tag': tag})
            for key in sorted(event_dict.keys()):
                self.event_listbox.insert(tk.END, event_dict[key])

    def get_selected_date(self, event=None):
        self.selected_date = self.calendar.get_date()

    def check_event_exist(self, date):
        config = configparser.ConfigParser()
        config.read('calendar.ini')
        return config.has_option('Events', str(date))

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
