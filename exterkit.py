# https://raw.githubusercontent.com/voody139/ExterKit/main/exterkit.py
import json, os, urllib.request, sys
from android.widget import LinearLayout, TextView, EditText, FrameLayout
from android.view import Gravity, ViewGroup
from android.graphics.drawable import GradientDrawable
from org.telegram.messenger import AndroidUtilities, SendMessagesHelper, MessagesController, UserConfig, ApplicationLoader
from org.telegram.ui.ActionBar import Theme
from android_utils import run_on_ui_thread
from ui.alert_dialog import AlertDialogBuilder
from client_utils import get_current_account
from hook_utils import find_class, find_method
from base_plugin import MethodHook
from org.telegram.tgnet import TLRPC

__version__ = "0.2.0"

class Action:
    @staticmethod
    def reply(did, txt):
        try: SendMessagesHelper.getInstance(get_current_account()).sendMessage(txt, did, None, None, None, True, None, None, None, True, 0, 0, False)
        except: pass

class UIBuilder:
    @staticmethod
    def card(c):
        l = LinearLayout(c); l.setOrientation(1); d = GradientDrawable(); d.setColor(Theme.getColor(Theme.key_windowBackgroundWhite)); d.setCornerRadius(AndroidUtilities.dp(12)); l.setBackground(d); p = AndroidUtilities.dp(16); l.setPadding(p, p, p, p); m = LinearLayout.LayoutParams(-1, -2); m.setMargins(AndroidUtilities.dp(14), AndroidUtilities.dp(8), AndroidUtilities.dp(14), AndroidUtilities.dp(8)); l.setLayoutParams(m); return l
    @staticmethod
    def title(c, t):
        v = TextView(c); v.setText(t); v.setTextSize(1, 16.0); v.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText)); v.setTypeface(AndroidUtilities.getTypeface("fonts/rmedium.ttf")); v.setPadding(0, 0, 0, AndroidUtilities.dp(8)); return v
    @staticmethod
    def button(c, t, cb):
        v = TextView(c); v.setText(t); v.setTextSize(1, 14.0); v.setTextColor(Theme.getColor(Theme.key_featuredStickers_buttonText)); v.setGravity(Gravity.CENTER); d = GradientDrawable(); d.setColor(Theme.getColor(Theme.key_featuredStickers_addButton)); d.setCornerRadius(AndroidUtilities.dp(8)); v.setBackground(d); v.setPadding(0, AndroidUtilities.dp(10), 0, AndroidUtilities.dp(10)); v.setOnClickListener(lambda view: cb()); m = LinearLayout.LayoutParams(-1, -2); m.setMargins(0, AndroidUtilities.dp(8), 0, 0); v.setLayoutParams(m); return v

class SmartStorage:
    def __init__(self, p): self.p = p
    def get_j(self, k, d=None):
        try: r = self.p.get_setting(k, ""); return json.loads(r) if r else (d or {})
        except: return d or {}
    def set_j(self, k, v):
        try: self.p.set_setting(k, json.dumps(v))
        except: pass

class AccountStorage(SmartStorage):
    def _k(self, k): return f"a_{get_current_account()}_{k}"
    def get(self, k, d=None): return self.p.get_setting(self._k(k), d)
    def set(self, k, v): self.p.set_setting(self._k(k), v)
    def get_j(self, k, d=None): return super().get_j(self._k(k), d)
    def set_j(self, k, v): super().set_j(self._k(k), v)

class _MsgHook(MethodHook):
    def __init__(self, cb): super().__init__(); self.cb = cb
    def after_hooked_method(self, p):
        try:
            u = p.args[0]
            if not isinstance(u, TLRPC.Updates): return
            for x in u.updates:
                if isinstance(x, TLRPC.UpdateNewMessage) and isinstance(x.message, TLRPC.TL_message) and not x.message.out: self.cb(x.message)
        except: pass

class Events:
    @staticmethod
    def on_message(hm, cb):
        try: hm.add(find_method(find_class("org.telegram.messenger.MessagesController"), "processUpdates", ["org.telegram.tgnet.TLRPC$Updates", "boolean"]), _MsgHook(cb))
        except: pass

class HookManager:
    def __init__(self, p): self.p = p; self.h = []
    def add(self, m, h):
        try: self.p.add_hook(m, h); self.h.append((m, h))
        except: pass
    def clear(self):
        for m, h in self.h:
            try: self.p.remove_hook(m, h)
            except: pass
        self.h.clear()

class TG:
    @staticmethod
    def user(uid=None):
        try: a = get_current_account(); return MessagesController.getInstance(a).getUser(uid or UserConfig.getInstance(a).getClientUserId())
        except: return None
    @staticmethod
    def chat(cid):
        try: return MessagesController.getInstance(get_current_account()).getChat(cid)
        except: return None
    @staticmethod
    def is_premium():
        try: return UserConfig.getInstance(get_current_account()).isPremium()
        except: return False

class Dialogs:
    @staticmethod
    @run_on_ui_thread
    def show_confirm(f, t, m, y, n=None, yt="OK", nt="Cancel"):
        try:
            if not f or f.isFinishing() or not f.getParentActivity(): return
            b = AlertDialogBuilder(f.getParentActivity()).setTitle(t).setMessage(m)
            b.setPositiveButton(yt, lambda d, w: y()).setNegativeButton(nt, lambda d, w: n() if n else None)
            f.showDialog(b.create())
        except: pass
    @staticmethod
    @run_on_ui_thread
    def show_input(f, t, h, d="", s=None, c=None):
        try:
            if not f or f.isFinishing() or not f.getParentActivity(): return
            a = f.getParentActivity(); b = AlertDialogBuilder(a).setTitle(t)
            e = EditText(a); e.setText(d); e.setHint(h); e.setTextColor(Theme.getColor(Theme.key_dialogTextBlack)); e.setHintTextColor(Theme.getColor(Theme.key_dialogTextGray))
            fr = FrameLayout(a); fr.addView(e); m = AndroidUtilities.dp(20); fr.setPadding(m, AndroidUtilities.dp(10), m, AndroidUtilities.dp(10)); b.setView(fr)
            b.setPositiveButton("Save", lambda d, w: s(e.getText().toString()) if s else None).setNegativeButton("Cancel", lambda d, w: c() if c else None)
            f.showDialog(b.create())
        except: pass

class ViewFinder:
    @staticmethod
    def by_class(v, c):
        r = []
        try:
            if not v: return r
            if c in str(v.getClass()): r.append(v)
            if isinstance(v, ViewGroup):
                for i in range(v.getChildCount()): r.extend(ViewFinder.by_class(v.getChildAt(i), c))
        except: pass
        return r
