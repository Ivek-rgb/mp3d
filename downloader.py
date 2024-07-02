# integrated libs
import subprocess
import argparse
import os
import sys
import math
import threading
import time

# dependent libs
print("Pregled modula potrebnih za funkcionalnost programa...")

installThread1 = threading.Thread(target = lambda : subprocess.run("pip install pytube", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True), args=())
installThread2 = threading.Thread(target = lambda : subprocess.run("pip install pydub", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True), args=())

installThread1.start()
installThread2.start()

installThread1.join()
installThread2.join()

from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from pydub import AudioSegment

parser = argparse.ArgumentParser("Youtube to MP3 converter argument parser.")

parser.add_argument("-cp", "--custompath", type=str, help="Enable saving to custom path")
parser.add_argument("yt_links", nargs="*", help="Youtube links to be converted")

loader_states = ("|", "/", "─", "\\")

def loader_thread(current_task: list, num_of_converts: int, line_num: int):
    
    global file_counter
    symbol_iter = 0
    
    while True:
        
        if symbol_iter != 0: 
            print("\033[2K\033[2F", end="")

        percentage_done = file_counter / num_of_converts

        print("[", end="")
        for i in range(0, math.ceil(percentage_done * line_num)): 
            print("█", end="")
        for i in range(math.ceil(percentage_done * line_num), line_num):
            print(" ", end="")
        print("]  " + f"{math.ceil(percentage_done * 100)}" + '% gotovo')
        print(loader_states[symbol_iter % 4] + " " + current_task[0])
        
        symbol_iter += 1
        time.sleep(0.1)
        
        
file_counter = 0

def transform_and_save(url_list: list, path_to_save = "./transformed_files/"): 
    
    global file_counter
    line_num = 30
    
    num_of_converts = len(url_list)
    
    task_list = ["Inicijalizacija veze na link..."]
    
    thread = threading.Thread(target=loader_thread, args=(task_list,num_of_converts,line_num,))
    thread.daemon = True
    thread.start()
    
    for link in url_list: 
        
        yt = YouTube(link)
        video_stream = yt.streams.filter(only_audio=True).first()
        
        task_list[0] = f"Skidanje videja - {yt.title[:10]}..."
        
        downloaded_file_path = video_stream.download(output_path=path_to_save)
        
        base, ext = os.path.splitext(downloaded_file_path)
        mp3_file_path = base + ".mp3"
        
        counter = 1
        while os.path.isfile(mp3_file_path): 
            mp3_file_path = base + f"({counter})" + ".mp3" 
            counter += 1
        
        task_list[0] = f"Transformacija {yt.title[:10]}... u mp3 format..."    
        
        audio = AudioSegment.from_file(downloaded_file_path)
        audio.export(mp3_file_path, format="mp3")
        
        os.remove(downloaded_file_path)
        
        file_counter += 1

def main():
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception: 
        print("Modul 'ffmpeg' nije instaliran i trazen je za nastavak. Pritisnite [Y] za instalaciju, te [N] za gasenje programa.", end="\t")
        if input() == "Y":
            result = subprocess.run('winget install "FFmpeg (Essentials Build)"', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            if result.returncode == 0: 
                print("Instalacija je uspjesna nastavak programa.")
            else: 
                print("Instalacija nije uspjesna!")
                exit(-1)
        else:
            print("Nije odabrana opcija za nastavak instalacije... Gasenje programa!")
            exit(0)
        
    args = parser.parse_args()
    
    home_dir = "./transformed_files/"
    num_of_args = len(sys.argv) - 1
    
    if args.custompath: 
        home_dir = args.custompath
        num_of_args -= 2
    
    if(num_of_args):
        sys.stdout.write("\033[?25l")
        transform_and_save(args.yt_links, home_dir)
    else: 
        input_url = ""
        input_url = input("Unesi link za convert:\t")
        url_list = []
        while len(input_url): 
            try: 
                yt = YouTube(input_url)
                url_list.append(input_url)
            except VideoUnavailable:
                print("Unesen videozapis nije pronadjen ili je neispravan.\nMolim ponovni unos linka!\n")
            input_url = input("Unesi link za convert:\t")
        sys.stdout.write("\033[?25l")
        transform_and_save(url_list, home_dir)
    time.sleep(0.5)
    sys.stdout.write("\033[?25h")
    print("\033[K\033[F", end="Program je završio sa zadatkom. Molimo pregledajte odabrani folder.")

if __name__ == "__main__": 
    main()