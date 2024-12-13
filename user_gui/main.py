import requests
import json
import subprocess
import sys
from tkinter import *
from customtkinter import *
import time

def get_external_ip():
    try:
        ip = subprocess.check_output(['curl', 'ifconfig.me']).strip().decode('utf-8')
        return ip
    except subprocess.CalledProcessError as ex:
        print(f"Error fetching IP address: {ex}")
        return None

def submit_data(name, address, pincode):
    ip = get_external_ip()
    
    if ip:
        url = "https://0aed-115-245-68-162.ngrok-free.app/api/postmaster/"
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json")
            response.raise_for_status()
            ipinfo = response.json()
    
            data = {
                "name": name,
                "latitude": float(ipinfo['loc'].split(',')[0]),
                "longitude": float(ipinfo['loc'].split(',')[1]),
                "address": address,
                "pincode": pincode
            }

            response = requests.post(url, headers=headers, json=data)
            print("Status Code:", response.status_code)
            print("Response JSON:", response.json())

        except requests.exceptions.RequestException as ex:
            print(f"ERROR: {ex}")
    else:
        print("Failed to fetch external IP.")

def onclick_submitbtn():
    global name_entry, address_entry, pincode_entry
    name = name_entry.get()
    address = address_entry.get()
    pincode = pincode_entry.get()
    submit_data(name, address, pincode)
    
def gui_main():
    wind = CTk()

    wind.geometry("500x300")
    wind.title("IP INFO")

    wind.configure(bg="#1a1a1a")

    time.sleep(3)
    frame1 = CTkFrame(wind)
    frame1.pack(pady=(10,5), padx=10, fill=BOTH)

    label1 = CTkLabel(frame1, text='Name:', font=CTkFont(family="Race Sport"))
    label1.pack(padx=10, pady=5)
    global name_entry
    name_entry = CTkEntry(frame1)
    name_entry.pack(padx=10, pady=5)

    label2 = CTkLabel(frame1, text='Address:', anchor="center", font=CTkFont(family="Race Sport"))
    label2.pack(padx=10, pady=5)
    global address_entry
    address_entry = CTkEntry(frame1)
    address_entry.pack(padx=10, pady=5)

    label3 = CTkLabel(frame1, text='Pincode:', font=CTkFont(family="Race Sport"))
    label3.pack(padx=10, pady=5)
    global pincode_entry
    pincode_entry = CTkEntry(frame1)
    pincode_entry.pack(padx=10, pady=5)

    submitbtn = CTkButton(frame1, text='Submit', fg_color='transparent', text_color='black', border_color="#ffcc70", border_width=2, corner_radius=32, hover_color='#ba0606', font=CTkFont(family="Race Sport"), command=onclick_submitbtn)
    submitbtn.pack(pady=10)

    wind.mainloop()
