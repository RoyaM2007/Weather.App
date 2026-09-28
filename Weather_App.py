import tkinter as tk
from tkinter import messagebox
from urllib.request import urlopen, Request
from urllib.parse import quote
import json


# =========================================================
# HAVA VƏZİYYƏTİNİ MƏTNƏ ÇEVİRƏN FUNKSİYA
# =========================================================

def get_weather_description(code):
    weather_codes = {
        0: ("Açıq hava", "☀️"),
        1: ("Əsasən açıq", "🌤️"),
        2: ("Qismən buludlu", "⛅"),
        3: ("Buludlu", "☁️"),
        45: ("Dumanlı", "🌫️"),
        48: ("Çox dumanlı", "🌫️"),
        51: ("Yüngül çiskin", "🌦️"),
        53: ("Çiskin", "🌦️"),
        55: ("Güclü çiskin", "🌧️"),
        61: ("Yüngül yağış", "🌦️"),
        63: ("Yağışlı", "🌧️"),
        65: ("Güclü yağış", "🌧️"),
        71: ("Yüngül qar", "🌨️"),
        73: ("Qarlı", "❄️"),
        75: ("Güclü qar", "❄️"),
        80: ("Yağışlı", "🌦️"),
        81: ("Güclü yağış", "🌧️"),
        82: ("Çox güclü yağış", "⛈️"),
        95: ("Tufan", "⛈️"),
        96: ("Tufan və dolu", "⛈️"),
        99: ("Güclü tufan və dolu", "⛈️")
    }

    return weather_codes.get(code, ("Naməlum hava", "🌡️"))


# =========================================================
# ŞƏHƏRİN KOORDİNATLARINI TAPIR
# =========================================================

def get_city_coordinates(city):

    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            "?name=" + quote(city) +
            "&count=1&language=az&format=json"
        )

        request = Request(
            url,
            headers={"User-Agent": "WeatherApp/1.0"}
        )

        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if "results" not in data:
            return None

        result = data["results"][0]

        return (
            result["latitude"],
            result["longitude"],
            result["name"],
            result.get("country", "")
        )

    except Exception:
        return None


# =========================================================
# HAVA MƏLUMATLARINI GƏTİRİR
# =========================================================

def get_weather(latitude, longitude):

    try:

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            "&current=temperature_2m,relative_humidity_2m,"
            "apparent_temperature,weather_code,wind_speed_10m"
            "&daily=weather_code,temperature_2m_max,"
            "temperature_2m_min"
            "&timezone=auto"
            "&forecast_days=7"
        )

        request = Request(
            url,
            headers={"User-Agent": "WeatherApp/1.0"}
        )

        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data

    except Exception:
        return None


# =========================================================
# AXTARIŞ FUNKSİYASI
# =========================================================

def search_weather():

    city = city_entry.get().strip()

    if city == "":
        messagebox.showwarning(
            "Xəbərdarlıq",
            "Zəhmət olmasa şəhərin adını daxil edin."
        )
        return

    status_label.config(
        text="Hava məlumatları yüklənir..."
    )

    root.update()

    location = get_city_coordinates(city)

    if location is None:
        status_label.config(text="Şəhər tapılmadı.")
        messagebox.showerror(
            "Xəta",
            "Bu şəhər tapılmadı.\n\nŞəhərin adını düzgün yazdığınızdan əmin olun."
        )
        return

    latitude, longitude, city_name, country = location

    weather = get_weather(latitude, longitude)

    if weather is None:
        status_label.config(
            text="Məlumat əldə etmək mümkün olmadı."
        )
        messagebox.showerror(
            "Xəta",
            "Hava məlumatlarını əldə etmək mümkün olmadı.\n"
            "İnternet bağlantınızı yoxlayın."
        )
        return

    display_weather(
        weather,
        city_name,
        country
    )


# =========================================================
# MƏLUMATLARI EKRANDA GÖSTƏRİR
# =========================================================

def display_weather(weather, city_name, country):

    current = weather["current"]
    daily = weather["daily"]

    temperature = round(current["temperature_2m"])
    feels_like = round(current["apparent_temperature"])
    humidity = current["relative_humidity_2m"]
    wind = round(current["wind_speed_10m"])
    weather_code = current["weather_code"]

    description, icon = get_weather_description(weather_code)

    # Şəhər
    location_label.config(
        text=f"📍 {city_name}, {country}"
    )

    # Böyük hava ikonu
    weather_icon_label.config(
        text=icon
    )

    # Temperatur
    temperature_label.config(
        text=f"{temperature}°C"
    )

    # Hava vəziyyəti
    description_label.config(
        text=description
    )

    # Hiss olunan temperatur
    feels_label.config(
        text=f"Hiss olunan: {feels_like}°C"
    )

    # Rütubət
    humidity_value.config(
        text=f"{humidity}%"
    )

    # Külək
    wind_value.config(
        text=f"{wind} km/s"
    )

    # 7 günlük proqnoz
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    days = [
        "Bazar ertəsi",
        "Çərşənbə axşamı",
        "Çərşənbə",
        "Cümə axşamı",
        "Cümə",
        "Şənbə",
        "Bazar"
    ]

    for i in range(7):

        date = daily["time"][i]

        max_temp = round(
            daily["temperature_2m_max"][i]
        )

        min_temp = round(
            daily["temperature_2m_min"][i]
        )

        code = daily["weather_code"][i]

        day_description, day_icon = get_weather_description(code)

        # Tarixi parçalayırıq
        year, month, day = date.split("-")

        card = tk.Frame(
            forecast_frame,
            bg="#172033",
            width=130,
            height=145
        )

        card.grid(
            row=0,
            column=i,
            padx=5,
            pady=5
        )

        card.grid_propagate(False)

        day_name = days[i]

        tk.Label(
            card,
            text=day_name,
            bg="#172033",
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(10, 2))

        tk.Label(
            card,
            text=f"{day}.{month}",
            bg="#172033",
            fg="#8b9bb4",
            font=("Segoe UI", 8)
        ).pack()

        tk.Label(
            card,
            text=day_icon,
            bg="#172033",
            font=("Segoe UI Emoji", 25)
        ).pack(pady=3)

        tk.Label(
            card,
            text=f"{max_temp}° / {min_temp}°",
            bg="#172033",
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).pack()

    status_label.config(
        text="Məlumat uğurla yeniləndi ✓"
    )


# =========================================================
# ENTER BASILANDA AXTARIŞ
# =========================================================

def enter_pressed(event):
    search_weather()


# =========================================================
# ƏSAS PƏNCƏRƏ
# =========================================================

root = tk.Tk()

root.title("Weather App")
root.geometry("950x650")
root.resizable(False, False)

root.configure(
    bg="#0f172a"
)


# =========================================================
# BAŞLIQ
# =========================================================

title_label = tk.Label(
    root,
    text="🌤️ Weather App",
    bg="#0f172a",
    fg="white",
    font=("Segoe UI", 28, "bold")
)

title_label.pack(
    pady=(25, 5)
)


subtitle_label = tk.Label(
    root,
    text="Real vaxt hava proqnozunu öyrənin",
    bg="#0f172a",
    fg="#94a3b8",
    font=("Segoe UI", 11)
)

subtitle_label.pack(
    pady=(0, 20)
)


# =========================================================
# AXTARIŞ PANELİ
# =========================================================

search_frame = tk.Frame(
    root,
    bg="#0f172a"
)

search_frame.pack()


city_entry = tk.Entry(
    search_frame,
    width=30,
    bg="#1e293b",
    fg="white",
    insertbackground="white",
    relief="flat",
    font=("Segoe UI", 13)
)

city_entry.grid(
    row=0,
    column=0,
    ipady=10,
    padx=(0, 10)
)


search_button = tk.Button(
    search_frame,
    text="🔍 Axtar",
    command=search_weather,
    bg="#2563eb",
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    font=("Segoe UI", 11, "bold"),
    padx=20,
    pady=9
)

search_button.grid(
    row=0,
    column=1
)


city_entry.bind(
    "<Return>",
    enter_pressed
)


# =========================================================
# ƏSAS HAVA PANELİ
# =========================================================

main_card = tk.Frame(
    root,
    bg="#1e293b",
    width=850,
    height=230
)

main_card.pack(
    pady=25
)

main_card.pack_propagate(False)


# Sol hissə
left_frame = tk.Frame(
    main_card,
    bg="#1e293b"
)

left_frame.pack(
    side="left",
    fill="both",
    expand=True
)


location_label = tk.Label(
    left_frame,
    text="📍 Şəhər seçin",
    bg="#1e293b",
    fg="#cbd5e1",
    font=("Segoe UI", 14, "bold")
)

location_label.pack(
    pady=(20, 5)
)


weather_icon_label = tk.Label(
    left_frame,
    text="🌤️",
    bg="#1e293b",
    font=("Segoe UI Emoji", 55)
)

weather_icon_label.pack()


description_label = tk.Label(
    left_frame,
    text="Hava vəziyyəti",
    bg="#1e293b",
    fg="white",
    font=("Segoe UI", 16, "bold")
)

description_label.pack()


# Sağ hissə
right_frame = tk.Frame(
    main_card,
    bg="#1e293b"
)

right_frame.pack(
    side="right",
    fill="both",
    expand=True
)


temperature_label = tk.Label(
    right_frame,
    text="--°C",
    bg="#1e293b",
    fg="white",
    font=("Segoe UI", 48, "bold")
)

temperature_label.pack(
    pady=(30, 0)
)


feels_label = tk.Label(
    right_frame,
    text="Hiss olunan: --°C",
    bg="#1e293b",
    fg="#94a3b8",
    font=("Segoe UI", 11)
)

feels_label.pack()


# =========================================================
# RÜTUBƏT VƏ KÜLƏK
# =========================================================

info_frame = tk.Frame(
    main_card,
    bg="#1e293b"
)

info_frame.place(
    x=600,
    y=150
)


humidity_value = tk.Label(
    info_frame,
    text="--%",
    bg="#1e293b",
    fg="#38bdf8",
    font=("Segoe UI", 12, "bold")
)

humidity_value.grid(
    row=0,
    column=0,
    padx=20
)


tk.Label(
    info_frame,
    text="💧 Rütubət",
    bg="#1e293b",
    fg="#94a3b8",
    font=("Segoe UI", 9)
).grid(
    row=1,
    column=0
)


wind_value = tk.Label(
    info_frame,
    text="-- km/s",
    bg="#1e293b",
    fg="#38bdf8",
    font=("Segoe UI", 12, "bold")
)

wind_value.grid(
    row=0,
    column=1,
    padx=20
)


tk.Label(
    info_frame,
    text="💨 Külək",
    bg="#1e293b",
    fg="#94a3b8",
    font=("Segoe UI", 9)
).grid(
    row=1,
    column=1
)


# =========================================================
# 7 GÜNLÜK PROQNOZ BAŞLIĞI
# =========================================================

forecast_title = tk.Label(
    root,
    text="7 günlük proqnoz",
    bg="#0f172a",
    fg="white",
    font=("Segoe UI", 16, "bold")
)

forecast_title.pack(
    pady=(0, 5)
)


# =========================================================
# 7 GÜNLÜK PROQNOZ PANELİ
# =========================================================

forecast_frame = tk.Frame(
    root,
    bg="#0f172a"
)

forecast_frame.pack()


# =========================================================
# STATUS
# =========================================================

status_label = tk.Label(
    root,
    text="Şəhər adını daxil edin",
    bg="#0f172a",
    fg="#64748b",
    font=("Segoe UI", 9)
)

status_label.pack(
    pady=12
)


# =========================================================
# PROQRAMI BAŞLAT
# =========================================================

root.mainloop()