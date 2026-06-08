import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gio
import locale
import os
import json
import threading
from typing import List, Optional, Callable

from system_prober import SystemProber, CommandError, debug_log
from backend import BackendRunner
from manager import DriverManager
from profiles import DriverProfiles, DriverProfile

APP_ID = "org.parch.DriverManager"
CONFIG_DIR = os.path.expanduser("~/.config/parch-driver-manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'C')

translations = {
    'en': {},
    'fa': {
        'Parch Driver Manager': 'مدیریت درایورهای پارچ',
        'Hardware & Drivers': 'سخت‌افزار و درایورها',
        'GPU': 'کارت گرافیک',
        'Network': 'شبکه',
        'Audio': 'صدا',
        'Bluetooth': 'بلوتوث',
        'System Info': 'اطلاعات سیستم',
        'Logs': 'گزارشات',
        'Select a Category': 'یک دسته انتخاب کنید',
        'Detected Graphics Cards': 'کارت‌های گرافیک شناسایی شده',
        'Recommended Driver Profiles': 'پروفایل‌های درایور پیشنهادی',
        'Install Driver': 'نصب درایور',
        'Remove Driver': 'حذف درایور',
        'Disable Hardware': 'غیرفعال کردن سخت‌افزار',
        'Enable Hardware': 'فعال کردن سخت‌افزار',
        'No GPU detected': 'کارت گرافیک یافت نشد',
        'Detected Network Devices': 'دستگاه‌های شبکه شناسایی شده',
        'No Network devices detected': 'دستگاه شبکه‌ای یافت نشد',
        'Detected Audio Devices': 'دستگاه‌های صوتی شناسایی شده',
        'No Audio devices detected': 'دستگاه صوتی یافت نشد',
        'Detected Bluetooth Devices': 'دستگاه‌های بلوتوث شناسایی شده',
        'No Bluetooth devices detected': 'دستگاه بلوتوث یافت نشد',
        'System information': 'اطلاعات سیستم',
        'GPU Vendor': 'سازنده کارت گرافیک',
        'Session Type': 'نوع نشست',
        'Hybrid Graphics': 'گرافیک ترکیبی',
        'Secure Boot': 'بوت امن',
        'Enabled': 'فعال',
        'Disabled': 'غیرفعال',
        'Operation log': 'گزارش عملیات',
        'No profile selected.': 'پروفایلی انتخاب نشده است.',
        'Profile installed successfully.': 'پروفایل با موفقیت نصب شد.',
        'Profile removed successfully.': 'پروفایل با موفقیت حذف شد.',
        'Hardware disabled. Reboot might be required.': 'سخت‌افزار غیرفعال شد. ممکن است ریبوت نیاز باشد.',
        'Hardware enabled.': 'سخت‌افزار فعال شد.',
        'Driver': 'درایور',
        'None': 'ندارد',
        'Search drivers...': 'جستجوی درایورها...',
        'Clear': 'پاک کردن',
        'OK': 'باشه',
        'Language Changed': 'زبان تغییر کرد',
        'Please restart the application to apply changes': 'لطفا برنامه را مجددا باز کنید',
        'Install': 'نصب',
        'Remove': 'حذف',
        'Enable': 'فعال',
        'Disable': 'غیرفعال',
        'Detected Hardware': 'سخت‌افزار شناسایی شده',
        'Available Drivers': 'درایورهای موجود',
        'Kernel': 'کرنل',
        'Processor': 'پردازنده',
        'Memory': 'حافظه',
        'Device': 'دستگاه',
        'Operating System': 'سیستم‌عامل',
        'Hostname': 'نام میزبان',
        'Display Server': 'سرور نمایش',
        'Hardware': 'سخت‌افزار',
        'System': 'سیستم',
        'Features': 'ویژگی‌ها',
        'Cancel': 'لغو',
        'Confirm': 'تایید',
        'Are you sure?': 'آیا مطمئن هستید؟',
        'This action will install the driver packages.': 'این عملیات پکیج‌های درایور را نصب می‌کند.',
        'This action will remove the driver packages.': 'این عملیات پکیج‌های درایور را حذف می‌کند.',
        'This action will disable the hardware module.': 'این عملیات ماژول سخت‌افزاری را غیرفعال می‌کند.',
        'Language': 'زبان',
        'Theme': 'تم',
        'English': 'English',
        'Persian': 'فارسی',
        'Light': 'روشن',
        'Dark': 'تیره',
        'Auto': 'خودکار',
        'Settings': 'تنظیمات',
        'Appearance': 'ظاهر',
        'Operation in progress...': 'در حال انجام عملیات...',
        'Unknown': 'نامشخص',
        'This profile has no associated kernel module to disable.': 'این پروفایل ماژول کرنل ندارد.',
        'This profile has no associated kernel module to enable.': 'این پروفایل ماژول کرنل ندارد.',
        'Starting installation': 'شروع نصب',
        'Profile installation finished.': 'نصب پروفایل به پایان رسید.',
        'Starting removal': 'شروع حذف',
        'Profile removal finished.': 'حذف پروفایل به پایان رسید.',
        'Disabling hardware module': 'غیرفعال کردن ماژول سخت‌افزاری',
        'Enabling hardware module': 'فعال کردن ماژول سخت‌افزاری',
        'Operation failed. See log for details.': 'عملیات ناموفق بود. گزارشات را ببینید.',
        'Unexpected error. See log for details.': 'خطای غیرمنتظره. گزارشات را ببینید.',
        'Please restart the application to apply language changes': 'لطفا برنامه را مجددا باز کنید تا تغییرات اعمال شود',
        'Hardware detected on your system': 'سخت‌افزار شناسایی شده در سیستم شما',
        'Network interfaces on your system': 'رابط‌های شبکه در سیستم شما',
        'Audio devices on your system': 'دستگاه‌های صوتی در سیستم شما',
        'Bluetooth adapters on your system': 'آداپترهای بلوتوث در سیستم شما',
        'Configuration and hardware status': 'پیکربندی و وضعیت سخت‌افزار'
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'language': 'en'}

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except:
        pass

current_config = load_config()
current_language = current_config.get('language', 'en')

def _(text: str) -> str:
    return translations.get(current_language, {}).get(text, text)

class LogBuffer:
    def __init__(self, textview: Gtk.TextView):
        self.textview = textview
        self.buffer = textview.get_buffer()

    def append(self, text: str):
        def _append():
            end_iter = self.buffer.get_end_iter()
            self.buffer.insert(end_iter, text + "\n")
            mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
            self.textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(_append)

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application):
        super().__init__(application=app)
        self.set_title(_("Parch Driver Manager"))
        self.set_default_size(1200, 750)

        self.backend = BackendRunner()
        self.manager = DriverManager(self.backend)

        self.gpu_info = SystemProber.get_gpu_info()
        self.session_type = SystemProber.get_session_type()
        self.hybrid = SystemProber.is_hybrid_graphics()
        self.secure_boot = SystemProber.has_secure_boot()
        self.hardware_devices = SystemProber.get_hardware_devices()
        self.kernel_info = SystemProber.get_kernel_info()
        self.system_info = SystemProber.get_system_info()

        self.current_profile: Optional[DriverProfile] = None
        self.profiles: List[DriverProfile] = []
        self.kernel_flavor = self.kernel_info.get('flavor', 'default')
        self.current_operation: Optional[threading.Thread] = None
        self.search_text: str = ""
        
        self.style_manager = Adw.StyleManager.get_default()
        
        self._build_ui()

    def _build_ui(self):
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.set_vexpand(True)
        self.toast_overlay.set_child(main_box)

        header = Adw.HeaderBar()
        header.add_css_class("flat")
        main_box.append(header)

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text(_("Settings"))
        header.pack_end(menu_button)

        menu = Gio.Menu()
        
        appearance_section = Gio.Menu()
        appearance_section.append(_("Settings"), "app.settings")
        menu.append_section(None, appearance_section)
        
        menu_button.set_menu_model(menu)

        self.split_view = Adw.NavigationSplitView()
        self.split_view.set_show_content(True)
        self.split_view.set_vexpand(True)
        main_box.append(self.split_view)

        sidebar_page = Adw.NavigationPage(title=_("Categories"))
        self.split_view.set_sidebar(sidebar_page)

        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar_box.set_vexpand(True)
        sidebar_page.set_child(sidebar_box)

        sidebar_header = Adw.HeaderBar(show_start_title_buttons=False, show_end_title_buttons=False)
        sidebar_header.add_css_class("flat")
        title_label = Gtk.Label(label=_("Hardware & Drivers"))
        title_label.add_css_class("title-2")
        sidebar_header.set_title_widget(title_label)
        sidebar_box.append(sidebar_header)

        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.add_css_class("navigation-sidebar")
        self.sidebar_list.set_vexpand(True)
        self.sidebar_list.connect("row-selected", self.on_sidebar_selected)
        sidebar_box.append(self.sidebar_list)

        categories = [
            (_("GPU"), "video-display-symbolic"),
            (_("Network"), "network-wireless-symbolic"),
            (_("Audio"), "audio-card-symbolic"),
            (_("Bluetooth"), "bluetooth-symbolic"),
            (_("System Info"), "preferences-system-symbolic"),
            (_("Logs"), "text-x-generic-symbolic")
        ]
        
        for cat, icon in categories:
            row = Adw.ActionRow(title=cat)
            row.set_icon_name(icon)
            self.sidebar_list.append(row)

        content_page = Adw.NavigationPage(title=_("Content"))
        self.split_view.set_content(content_page)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_vexpand(True)
        content_page.set_child(content_box)

        self.content_header = Adw.HeaderBar(show_start_title_buttons=False, show_end_title_buttons=False)
        self.content_header.add_css_class("flat")
        self.content_title = Gtk.Label(label=_("Select a Category"))
        self.content_title.add_css_class("title-1")
        self.content_header.set_title_widget(self.content_title)
        content_box.append(self.content_header)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        self.progress_bar.add_css_class("osd")
        content_box.append(self.progress_bar)

        stack_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        stack_box.set_vexpand(True)
        content_box.append(stack_box)
        
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(300)
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)
        stack_box.append(self.stack)

        self._build_gpu_page()
        self._build_network_page()
        self._build_audio_page()
        self._build_bluetooth_page()
        self._build_info_page()
        self._build_logs_page()

        GLib.idle_add(self.sidebar_list.select_row, self.sidebar_list.get_row_at_index(0))
        
        self._load_css()

    def _create_profile_widgets(self, profiles: List[DriverProfile], category: str) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        profiles_group = Adw.PreferencesGroup(title=_("Available Drivers"))
        box.append(profiles_group)

        profile_listbox = Gtk.ListBox()
        profile_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        profile_listbox.add_css_class("boxed-list")
        profiles_group.add(profile_listbox)
        setattr(self, f"profile_listbox_{category.lower()}", profile_listbox)

        for idx, profile in enumerate(profiles):
            row = Adw.ActionRow(title=profile.name, subtitle=profile.description)
            row.set_activatable(True)
            
            chevron = Gtk.Image()
            chevron.set_from_icon_name("go-next-symbolic")
            row.add_suffix(chevron)
            
            row.connect("activated", self.on_profile_row_activated, idx, category)
            profile_listbox.append(row)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_top=16)
        button_box.set_halign(Gtk.Align.CENTER)
        box.append(button_box)

        install_button = Gtk.Button(label=_("Install"))
        install_button.add_css_class("suggested-action")
        install_button.add_css_class("pill")
        install_button.connect("clicked", self.on_install_clicked, category)
        button_box.append(install_button)

        remove_button = Gtk.Button(label=_("Remove"))
        remove_button.add_css_class("destructive-action")
        remove_button.add_css_class("pill")
        remove_button.connect("clicked", self.on_remove_clicked, category)
        button_box.append(remove_button)

        disable_button = Gtk.Button(label=_("Disable"))
        disable_button.add_css_class("pill")
        disable_button.connect("clicked", self.on_disable_clicked, category)
        button_box.append(disable_button)

        enable_button = Gtk.Button(label=_("Enable"))
        enable_button.add_css_class("pill")
        enable_button.connect("clicked", self.on_enable_clicked, category)
        button_box.append(enable_button)

        return box

    def _build_gpu_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        scrolled.set_child(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_vexpand(False)
        clamp.set_child(main_box)

        hw_group = Adw.PreferencesGroup(title=_("Detected Hardware"))
        main_box.append(hw_group)
        
        hw_list = Gtk.ListBox()
        hw_list.add_css_class("boxed-list")
        hw_group.add(hw_list)

        gpus = [d for d in self.hardware_devices if d['category'] == 'GPU']
        if gpus:
            for gpu in gpus:
                driver_text = gpu['driver'] if gpu['driver'] else _('None')
                sub = f"{_('Driver')}: {driver_text}"
                row = Adw.ActionRow(title=gpu['name'], subtitle=sub)
                
                status_badge = Gtk.Image()
                status_badge.set_from_icon_name("media-record-symbolic")
                status_badge.set_pixel_size(10)
                if gpu['driver']:
                    status_badge.add_css_class("success-icon")
                else:
                    status_badge.add_css_class("warning-icon")
                row.add_prefix(status_badge)
                
                hw_list.append(row)
        else:
            row = Adw.ActionRow(title=_("No GPU detected"))
            row.set_sensitive(False)
            hw_list.append(row)

        self.gpu_profiles = DriverProfiles.get_gpu_profiles(self.gpu_info.get("vendor", "Unknown"), self.kernel_flavor)
        main_box.append(self._create_profile_widgets(self.gpu_profiles, "GPU"))
        
        self.stack.add_named(scrolled, _("GPU"))

    def _build_network_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        scrolled.set_child(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_vexpand(False)
        clamp.set_child(main_box)

        hw_group = Adw.PreferencesGroup(title=_("Detected Hardware"))
        main_box.append(hw_group)
        
        hw_list = Gtk.ListBox()
        hw_list.add_css_class("boxed-list")
        hw_group.add(hw_list)

        nets = [d for d in self.hardware_devices if d['category'] == 'Network']
        if nets:
            for net in nets:
                driver_text = net['driver'] if net['driver'] else _('None')
                sub = f"{_('Driver')}: {driver_text}"
                row = Adw.ActionRow(title=net['name'], subtitle=sub)
                
                status_badge = Gtk.Image()
                status_badge.set_from_icon_name("media-record-symbolic")
                status_badge.set_pixel_size(10)
                if net['driver']:
                    status_badge.add_css_class("success-icon")
                else:
                    status_badge.add_css_class("warning-icon")
                row.add_prefix(status_badge)
                
                hw_list.append(row)
        else:
            row = Adw.ActionRow(title=_("No Network devices detected"))
            row.set_sensitive(False)
            hw_list.append(row)

        self.net_profiles = DriverProfiles.get_network_profiles()
        main_box.append(self._create_profile_widgets(self.net_profiles, "Network"))
        self.stack.add_named(scrolled, _("Network"))

    def _build_audio_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        scrolled.set_child(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_vexpand(False)
        clamp.set_child(main_box)

        hw_group = Adw.PreferencesGroup(title=_("Detected Hardware"))
        main_box.append(hw_group)
        
        hw_list = Gtk.ListBox()
        hw_list.add_css_class("boxed-list")
        hw_group.add(hw_list)

        auds = [d for d in self.hardware_devices if d['category'] == 'Audio']
        if auds:
            for aud in auds:
                driver_text = aud['driver'] if aud['driver'] else _('None')
                sub = f"{_('Driver')}: {driver_text}"
                row = Adw.ActionRow(title=aud['name'], subtitle=sub)
                
                status_badge = Gtk.Image()
                status_badge.set_from_icon_name("media-record-symbolic")
                status_badge.set_pixel_size(10)
                if aud['driver']:
                    status_badge.add_css_class("success-icon")
                else:
                    status_badge.add_css_class("warning-icon")
                row.add_prefix(status_badge)
                
                hw_list.append(row)
        else:
            row = Adw.ActionRow(title=_("No Audio devices detected"))
            row.set_sensitive(False)
            hw_list.append(row)

        self.audio_profiles = DriverProfiles.get_audio_profiles()
        main_box.append(self._create_profile_widgets(self.audio_profiles, "Audio"))
        self.stack.add_named(scrolled, _("Audio"))

    def _build_bluetooth_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        scrolled.set_child(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_vexpand(False)
        clamp.set_child(main_box)

        hw_group = Adw.PreferencesGroup(title=_("Detected Hardware"))
        main_box.append(hw_group)
        
        hw_list = Gtk.ListBox()
        hw_list.add_css_class("boxed-list")
        hw_group.add(hw_list)

        bts = [d for d in self.hardware_devices if d['category'] == 'Bluetooth']
        if bts:
            for bt in bts:
                driver_text = bt['driver'] if bt['driver'] else _('None')
                sub = f"{_('Driver')}: {driver_text}"
                row = Adw.ActionRow(title=bt['name'], subtitle=sub)
                
                status_badge = Gtk.Image()
                status_badge.set_from_icon_name("media-record-symbolic")
                status_badge.set_pixel_size(10)
                if bt['driver']:
                    status_badge.add_css_class("success-icon")
                else:
                    status_badge.add_css_class("warning-icon")
                row.add_prefix(status_badge)
                
                hw_list.append(row)
        else:
            row = Adw.ActionRow(title=_("No Bluetooth devices detected"))
            row.set_sensitive(False)
            hw_list.append(row)

        self.bt_profiles = DriverProfiles.get_bluetooth_profiles()
        main_box.append(self._create_profile_widgets(self.bt_profiles, "Bluetooth"))
        self.stack.add_named(scrolled, _("Bluetooth"))

    def _build_info_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        scrolled.set_child(clamp)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        box.set_vexpand(False)
        clamp.set_child(box)

        info_group = Adw.PreferencesGroup(title=_("Hardware"))
        box.append(info_group)
        
        cpu_row = Adw.ActionRow(title=_("Processor"))
        cpu_row.set_subtitle(self.system_info.get("cpu", "Unknown"))
        info_group.add(cpu_row)

        vendor_row = Adw.ActionRow(title=_("GPU"))
        gpu_text = self.gpu_info.get("vendor", "Unknown")
        if self.gpu_info.get("model"):
            gpu_text = f"{gpu_text} - {self.gpu_info.get('model')}"
        vendor_row.set_subtitle(gpu_text)
        info_group.add(vendor_row)
        
        memory_row = Adw.ActionRow(title=_("Memory"))
        memory_row.set_subtitle(self.system_info.get("memory", "Unknown"))
        info_group.add(memory_row)

        system_group = Adw.PreferencesGroup(title=_("System"))
        box.append(system_group)
        
        if self.system_info.get("vendor") or self.system_info.get("model"):
            device_row = Adw.ActionRow(title=_("Device"))
            device_text = f"{self.system_info.get('vendor', '')} {self.system_info.get('model', '')}".strip()
            device_row.set_subtitle(device_text or "Unknown")
            system_group.add(device_row)
        
        os_row = Adw.ActionRow(title=_("Operating System"))
        os_row.set_subtitle(self.system_info.get("os", "Unknown"))
        system_group.add(os_row)
        
        kernel_row = Adw.ActionRow(title=_("Kernel"))
        kernel_row.set_subtitle(self.kernel_info.get("version", "Unknown"))
        system_group.add(kernel_row)
        
        hostname_row = Adw.ActionRow(title=_("Hostname"))
        hostname_row.set_subtitle(self.system_info.get("hostname", "Unknown"))
        system_group.add(hostname_row)

        session_row = Adw.ActionRow(title=_("Display Server"))
        session_row.set_subtitle(self.session_type.upper())
        system_group.add(session_row)

        features_group = Adw.PreferencesGroup(title=_("Features"))
        box.append(features_group)

        hybrid_row = Adw.ActionRow(title=_("Hybrid Graphics"))
        hybrid_status = _("Enabled") if self.hybrid else _("Disabled")
        hybrid_row.set_subtitle(hybrid_status)
        features_group.add(hybrid_row)

        secure_row = Adw.ActionRow(title=_("Secure Boot"))
        secure_status = _("Enabled") if self.secure_boot else _("Disabled")
        secure_row.set_subtitle(secure_status)
        features_group.add(secure_row)

        lang_group = Adw.PreferencesGroup(title=_("Appearance"))
        box.append(lang_group)

        lang_row = Adw.ComboRow(title=_("Language"))
        string_list = Gtk.StringList()
        string_list.append("English")
        string_list.append("فارسی")
        lang_row.set_model(string_list)
        lang_row.set_selected(0 if current_language == 'en' else 1)
        lang_row.connect("notify::selected", self.on_language_changed)
        lang_group.add(lang_row)

        theme_row = Adw.ComboRow(title=_("Theme"))
        theme_list = Gtk.StringList()
        theme_list.append(_("Light"))
        theme_list.append(_("Dark"))
        theme_list.append(_("Auto"))
        theme_row.set_model(theme_list)
        
        current_theme = self.style_manager.get_color_scheme()
        if current_theme == Adw.ColorScheme.FORCE_LIGHT:
            theme_row.set_selected(0)
        elif current_theme == Adw.ColorScheme.FORCE_DARK:
            theme_row.set_selected(1)
        else:
            theme_row.set_selected(2)
        
        theme_row.connect("notify::selected", self.on_theme_changed)
        lang_group.add(theme_row)

        self.stack.add_named(scrolled, _("System Info"))

    def _build_logs_page(self):
        scrolled_outer = Gtk.ScrolledWindow()
        scrolled_outer.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_outer.set_vexpand(True)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        scrolled_outer.set_child(clamp)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        clamp.set_child(box)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.append(header_box)
        
        log_label = Gtk.Label(label=_("Operation log"))
        log_label.set_xalign(0)
        log_label.add_css_class("title-3")
        log_label.set_hexpand(True)
        header_box.append(log_label)

        clear_button = Gtk.Button(label=_("Clear"))
        clear_button.set_icon_name("edit-clear-symbolic")
        clear_button.add_css_class("flat")
        clear_button.connect("clicked", self.on_clear_logs)
        header_box.append(clear_button)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)
        scrolled.add_css_class("card")
        box.append(scrolled)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_monospace(True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_view.set_top_margin(12)
        self.log_view.set_bottom_margin(12)
        self.log_view.set_left_margin(12)
        self.log_view.set_right_margin(12)
        scrolled.set_child(self.log_view)

        self.log_buffer = LogBuffer(self.log_view)

        self.stack.add_named(scrolled_outer, _("Logs"))

    def on_sidebar_selected(self, listbox, row):
        if row:
            title = row.get_title()
            self.content_title.set_label(title)
            self.stack.set_visible_child_name(title)
            
            if title == _("GPU"): 
                self.profiles = self.gpu_profiles
            elif title == _("Network"): 
                self.profiles = self.net_profiles
            elif title == _("Audio"): 
                self.profiles = self.audio_profiles
            elif title == _("Bluetooth"): 
                self.profiles = self.bt_profiles
            else: 
                self.profiles = []

    def on_profile_row_activated(self, row: Adw.ActionRow, idx: int, category: str):
        profiles_attr = f"{category.lower()}_profiles"
        profiles = getattr(self, profiles_attr, [])
        
        if idx < len(profiles):
            self.current_profile = profiles[idx]
            self.current_category = category
            self._show_toast(f"✓ {self.current_profile.name}")

    def _run_in_thread(self, target: Callable, *args, **kwargs):
        def wrapper():
            try:
                target(*args, **kwargs)
            except CommandError as e:
                msg = f"✗ Command error: {' '.join(e.cmd)}\nExit code: {e.returncode}\n{e.stderr}"
                debug_log(msg)
                GLib.idle_add(self._show_toast, _("Operation failed. See log for details."))
                GLib.idle_add(self._end_operation)
                self.log_buffer.append(msg)
            except Exception as e:
                msg = f"✗ Unexpected exception: {e}"
                debug_log(msg)
                GLib.idle_add(self._show_toast, _("Unexpected error. See log for details."))
                GLib.idle_add(self._end_operation)
                self.log_buffer.append(msg)

        self.current_operation = threading.Thread(target=wrapper, daemon=True)
        self.current_operation.start()

    def _start_operation(self):
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()
        GLib.timeout_add(100, self._pulse_progress)

    def _pulse_progress(self):
        if self.progress_bar.get_visible():
            self.progress_bar.pulse()
            return True
        return False

    def _end_operation(self):
        self.progress_bar.set_visible(False)

    def on_search_changed(self, entry: Gtk.SearchEntry, category: str):
        pass

    def on_language_changed(self, combo_row, param):
        selected = combo_row.get_selected()
        new_lang = 'en' if selected == 0 else 'fa'
        
        if new_lang != current_language:
            config = load_config()
            config['language'] = new_lang
            save_config(config)
            
            dialog = Adw.MessageDialog(
                transient_for=self,
                heading=_("Language Changed"),
                body=_("Please restart the application to apply changes"),
            )
            dialog.add_response("ok", _("OK"))
            dialog.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
            dialog.present()

    def on_theme_changed(self, combo_row, param):
        selected = combo_row.get_selected()
        
        if selected == 0:
            self.style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif selected == 1:
            self.style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            self.style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def on_clear_logs(self, button):
        buffer = self.log_view.get_buffer()
        buffer.set_text("")

    def _load_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        .navigation-sidebar row {
            min-height: 40px;
            padding: 4px 8px;
        }
        
        .navigation-sidebar row label.title {
            font-size: 0.9em;
        }
        
        .navigation-sidebar row image {
            margin-right: 4px;
            opacity: 0.8;
        }
        
        .success-icon {
            color: @success_color;
        }
        .warning-icon {
            color: @warning_color;
        }
        .card {
            background: @window_bg_color;
            border-radius: 12px;
            padding: 2px;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_install_clicked(self, button: Gtk.Button, category: str = None):
        if not self.current_profile:
            self._show_toast(_("No profile selected."))
            return

        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=_("Are you sure?"),
            body=_("This action will install the driver packages."),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("install", _("Confirm"))
        dialog.set_response_appearance("install", Adw.ResponseAppearance.SUGGESTED)
        dialog.connect("response", self._on_install_confirmed)
        dialog.present()

    def _on_install_confirmed(self, dialog, response):
        if response != "install":
            return

        def progress(msg: str):
            self.log_buffer.append(msg)

        def task():
            GLib.idle_add(self._start_operation)
            self.log_buffer.append(f"➤ {_('Starting installation')}: {self.current_profile.name}")
            self.manager.install_profile(self.current_profile, progress_cb=progress)
            self.log_buffer.append(f"✓ {_('Profile installation finished.')}")
            GLib.idle_add(self._end_operation)
            GLib.idle_add(self._show_toast, _("Profile installed successfully."))

        self._run_in_thread(task)

    def on_remove_clicked(self, button: Gtk.Button, category: str = None):
        if not self.current_profile:
            self._show_toast(_("No profile selected."))
            return

        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=_("Are you sure?"),
            body=_("This action will remove the driver packages."),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("remove", _("Confirm"))
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_remove_confirmed)
        dialog.present()

    def _on_remove_confirmed(self, dialog, response):
        if response != "remove":
            return

        def progress(msg: str):
            self.log_buffer.append(msg)

        def task():
            GLib.idle_add(self._start_operation)
            self.log_buffer.append(f"➤ {_('Starting removal')}: {self.current_profile.name}")
            self.manager.remove_profile(self.current_profile, progress_cb=progress)
            self.log_buffer.append(f"✓ {_('Profile removal finished.')}")
            GLib.idle_add(self._end_operation)
            GLib.idle_add(self._show_toast, _("Profile removed successfully."))

        self._run_in_thread(task)

    def on_disable_clicked(self, button: Gtk.Button, category: str = None):
        if not self.current_profile:
            self._show_toast(_("No profile selected."))
            return
        if not self.current_profile.module:
            self._show_toast(_("This profile has no associated kernel module to disable."))
            return

        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=_("Are you sure?"),
            body=_("This action will disable the hardware module."),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("disable", _("Confirm"))
        dialog.set_response_appearance("disable", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_disable_confirmed)
        dialog.present()

    def _on_disable_confirmed(self, dialog, response):
        if response != "disable":
            return

        def progress(msg: str):
            self.log_buffer.append(msg)

        def task():
            GLib.idle_add(self._start_operation)
            self.log_buffer.append(f"➤ {_('Disabling hardware module')}: {self.current_profile.name}")
            self.manager.disable_driver(self.current_profile, progress_cb=progress)
            GLib.idle_add(self._end_operation)
            GLib.idle_add(self._show_toast, _("Hardware disabled. Reboot might be required."))

        self._run_in_thread(task)

    def on_enable_clicked(self, button: Gtk.Button, category: str = None):
        if not self.current_profile:
            self._show_toast(_("No profile selected."))
            return
        if not self.current_profile.module:
            self._show_toast(_("This profile has no associated kernel module to enable."))
            return

        def progress(msg: str):
            self.log_buffer.append(msg)

        def task():
            GLib.idle_add(self._start_operation)
            self.log_buffer.append(f"➤ {_('Enabling hardware module')}: {self.current_profile.name}")
            self.manager.enable_driver(self.current_profile, progress_cb=progress)
            GLib.idle_add(self._end_operation)
            GLib.idle_add(self._show_toast, _("Hardware enabled."))

        self._run_in_thread(task)

    def _show_toast(self, text: str):
        toast = Adw.Toast.new(text)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

class ParchDriverManagerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(self)
        win.present()

def main(argv: List[str]) -> int:
    app = ParchDriverManagerApp()
    return app.run(argv)
