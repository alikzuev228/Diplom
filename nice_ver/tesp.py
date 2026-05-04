import os

current_dir = os.path.dirname(os.path.abspath(__file__))

conf_file = []

#ip_test = "192.168.20.101"

name = r"c:\Unik\Diplom\Diplom\nice_ver\audio\audio_192.168.18.43_1234_1776935525.wav"

ip_test = name.strip().split("_")[len(name.strip().split("_"))-3]
print(ip_test)

with open(fr"{current_dir}\config.txt", encoding="utf-8") as file:
    for line in file:
        splt = line.strip().split(";")

        if len(splt) != 2:
            continue

        name_zone, ip = splt
        conf_file.append([name_zone, ip])


for row in conf_file:

    if ip_test == row[1]:
        print(f"IP однакові з {row[0]}")
        break