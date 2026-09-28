import json
import os
import urllib.request
from datetime import datetime

API_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"

def fetch_weather_data():
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def generate_ics(data):
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//HKO Weather Forecast//NONSGML v1.0//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:香港九天天氣預報",
        "X-WR-TIMEZONE:Asia/Hong_Kong"
    ]

    forecast_list = data.get("weatherForecast", [])
    
    for day in forecast_list:
        date_str = day["forecastDate"]  # YYYYMMDD
        
        temp_min = day.get("mintemp", {}).get("value")
        temp_max = day.get("maxtemp", {}).get("value")
        rh_min = day.get("forecastMinRH", {}).get("value")
        rh_max = day.get("forecastMaxRH", {}).get("value")
        forecast_text = day.get("forecastForecast", "")
        psr = day.get("PSR", "")

        summary = f"天氣：{temp_min}°C - {temp_max}°C ({forecast_text[:8]}...)"
        description = (
            f"天氣預測：{forecast_text}\\n"
            f"氣溫：{temp_min}°C 至 {temp_max}°C\\n"
            f"相對濕度：{rh_min}% 至 {rh_max}%\\n"
            f"顯著降雨概率：{psr}"
        )

        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:hko-forecast-{date_str}@weather.gov.hk",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"DTEND;VALUE=DATE:{date_str}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT",
            "END:VEVENT"
        ])

    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

if __name__ == "__main__":
    weather_json = fetch_weather_data()
    ics_content = generate_ics(weather_json)
    
    # 建立 output 資料夾供 GitHub Pages 發布
    os.makedirs("output", exist_ok=True)
    with open("output/hko_weather.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)
        
    print("已成功生成 hko_weather.ics")
