import numpy as np
from datetime import datetime, date
import csv
from datetime import timedelta
import os


def generate_lookup_table(lat_deg: float, year: int):
    #Creates a CSV file with one row per day for the given year. 
    # It automatically saves in the same folder as this program.
    # Find this script's folder
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the output path (same folder)
    file_name = f"daylight_lookup_{lat_deg:.2f}deg_{year}.csv".replace(" ", "")
    out_path = os.path.join(script_dir, file_name)

    # Open the file and write data
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "doy", "declination_deg", "daylight_hours", "condition"])

        # loop through every day of the year
        d = date(year, 1, 1)
        end = date(year + 1, 1, 1)
        while d < end:
            hours, condition = calculate_daylight(lat_deg, d)
            decl_deg = float(np.degrees(solar_declination_rad(d)))
            w.writerow([d.isoformat(), day_of_year(d),
                        f"{decl_deg:.4f}", f"{hours:.4f}", condition])
            d += timedelta(days=1)

    # Tell the user where it went
    print(f"CSV file saved to:\n{out_path}")



def solar_declination_rad(d: date) -> float:
    #Returns solar declination in radians using a standard accurate series.
    # delta approximate function of the 'day angle' gamma = 2π(n-1)/365
    
    n = day_of_year(d)
    gamma = 2.0 * np.pi * (n - 1) / 365.0

    delta = (
        0.006918
        - 0.399912 * np.cos(gamma)
        + 0.070257 * np.sin(gamma)
        - 0.006758 * np.cos(2 * gamma)
        + 0.000907 * np.sin(2 * gamma)
        - 0.002697 * np.cos(3 * gamma)
        + 0.001480 * np.sin(3 * gamma)
    )
    return float(delta)

def calculate_daylight(lat_deg: float, d: date):
    #Returns (hours_of_daylight, condition_string)
    # condition is "Normal Day", "Polar Day", or "Polar Night".
    # Angles in radians
    phi = np.deg2rad(lat_deg)
    delta = solar_declination_rad(d)
    h0 = np.deg2rad(-0.833)  # apparent sunrise/sunset

    sin_phi, cos_phi = np.sin(phi), np.cos(phi)
    sin_delta, cos_delta = np.sin(delta), np.cos(delta)
    sin_h0 = np.sin(h0)

    # cos(H0) for sunrise/sunset
    cos_H0 = (sin_h0 - sin_phi * sin_delta) / (cos_phi * cos_delta)

    # Polar checks first (avoid NaN from arccos domain issues)
    if cos_H0 <= -1.0:
        return 24.0, "Polar Day"
    if cos_H0 >= 1.0:
        return 0.0, "Polar Night"

    # Normal case
    H0 = np.arccos(cos_H0)  # radians
    daylight_hours = (2.0 * np.rad2deg(H0)) / 15.0  # 15° per hour
    return float(daylight_hours), "Normal Day"

def fmt_hours(hours: float) -> str:
    h = int(hours)
    m = int(np.round((hours - h) * 60))
    if m == 60:
        h += 1
        m = 0
    return f"{h}h {m}m"

def main():
    print("Daylight Hours Calculator")
    lat_str = input("Enter latitude (degrees, +N / -S): ").strip()
    date_str = input("Enter date (YYYY-MM-DD): ").strip()

    # 1) Parse inputs FIRST so 'lat' and 'd' exist
    lat = float(lat_str)
    d = datetime.strptime(date_str, "%Y-%m-%d").date()

    # 2) Compute daylight for that single date (print to terminal)
    hours, condition = calculate_daylight(lat, d)

    print("\nResult:\n")
    print(f"Latitude : {lat:.2f}°\n")
    print(f"Date     : {d} (DOY {day_of_year(d)})\n")
    print(f"Daylight : {fmt_hours(hours)}\n")
    if condition != "Normal Day":
        print(f"Note     : {condition}\n")

    # 3) (Optional) Save a full-year CSV lookup table in the SAME folder as this script
    ans = input("Would you like to save a full-year CSV lookup table? (y/n): ").strip().lower()
    if ans == "y":
        year = d.year
        generate_lookup_table(lat, year)




def day_of_year(d: date) -> int:
    # "%j" gives day-of-year as a zero-padded string like "001".."366"
    return int(d.strftime("%j"))


if __name__ == "__main__":
    main()
