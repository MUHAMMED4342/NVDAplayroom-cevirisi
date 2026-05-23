import os
import sys
import tkinter as tk
from tkinter import messagebox
import requests
import winreg

# Mesaj kutusu için gizli bir pencere
root = tk.Tk()
root.withdraw()

# --- AYARLAR ---
VERSION_URL = "https://raw.githubusercontent.com/MUHAMMED4342/NVDAplayroom-cevirisi/main/version.txt"
DIC_FILE_URL = "https://raw.githubusercontent.com/MUHAMMED4342/NVDAplayroom-cevirisi/main/qcgC.dic"
HEDEF_KLASOR = os.path.join(os.environ.get('APPDATA', ''), "nvda", "speechDicts", "appDicts")
HEDEF_SOZLUK_YOLU = os.path.join(HEDEF_KLASOR, "qcgC.dic")
YEREL_VERSIYON_YOLU = os.path.join(HEDEF_KLASOR, "yerel_versiyon.txt")

def baslangica_ekle():
    """Programın başlangıca kendini eklemesini yönetir."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "PlayRoomCevirici"
    # sys.executable o an çalışan exe'nin tam yolunu verir
    app_path = f'"{sys.executable}" --sessiz'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        if messagebox.askyesno("Başlangıçta Çalıştır", "Windows her açıldığında güncelleme kontrolü otomatik yapılsın mı?"):
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)

def internet_kontrol():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

def yerel_versiyon_oku():
    if os.path.exists(YEREL_VERSIYON_YOLU):
        try:
            with open(YEREL_VERSIYON_YOLU, "r", encoding="utf-8") as f:
                return f.read().strip()
        except: return "0.0.0"
    return "0.0.0"

def yerel_versiyon_yaz(yeni_versiyon):
    with open(YEREL_VERSIYON_YOLU, "w", encoding="utf-8") as f:
        f.write(yeni_versiyon)

def dosyayi_indir_ve_kur(guncel_versiyon):
    try:
        dic_response = requests.get(DIC_FILE_URL, timeout=15)
        if dic_response.status_code == 200:
            if not os.path.exists(HEDEF_KLASOR): os.makedirs(HEDEF_KLASOR)
            with open(HEDEF_SOZLUK_YOLU, "wb") as f:
                f.write(dic_response.content)
            yerel_versiyon_yaz(guncel_versiyon)
            return True
    except: return False
    return False

def ana_islem(sessiz_mod):
    if not os.path.exists(HEDEF_KLASOR):
        if not sessiz_mod: messagebox.showerror("Hata", "NVDA klasörü bulunamadı.")
        return

    if not internet_kontrol(): return

    try:
        response = requests.get(VERSION_URL, timeout=5)
        guncel_versiyon = response.text.strip()
        yerel_versiyon = yerel_versiyon_oku()

        if guncel_versiyon != yerel_versiyon:
            if sessiz_mod:
                dosyayi_indir_ve_kur(guncel_versiyon)
            else:
                if messagebox.askyesno("Güncelleme", f"Yeni sürüm ({guncel_versiyon}) var. Güncellensin mi?"):
                    if dosyayi_indir_ve_kur(guncel_versiyon):
                        messagebox.showinfo("Başarılı", "Güncelleme tamamlandı.")
        else:
            if not sessiz_mod:
                messagebox.showinfo("Güncel", "Sözlüğünüz zaten güncel.")
    except: pass

if __name__ == "__main__":
    # Parametre kontrolü: --sessiz varsa sessiz modda çalış
    sessiz = "--sessiz" in sys.argv
    
    if not sessiz:
        baslangica_ekle()
    
    ana_islem(sessiz)
    sys.exit()