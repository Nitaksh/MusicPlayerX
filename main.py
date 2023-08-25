import os
import threading
import tkinter as tk
from moviepy.editor import *
from pygame import mixer
from pytube import *
import yt_dlp
import pandas as pd
import SpotifyAPI

class Node:
    def __init__(self, link=None):
        self.linker = link
        self.nextval = None
        self.preval = None

class LinkedList:
    def __init__(self):
        self.headval = None
        self.start = None

class MusicPlayer:
    def __init__(self):
        self.y, self.z = 0, 0
        self.var = 0
        self.le = 0
        self.cwd = os.getcwd()
        self.l = LinkedList()
        self.music_thread = None

    def inputer(self):
        self.l = LinkedList()
        w = tk.Toplevel()
        f = open(os.path.join(self.cwd, "playlist", "musicfiles.txt"), "r", encoding='utf-8')
        r = f.readlines()
        self.le = len(r)
        j = 0
        tk.Label(w, text="Your Playlist", font=('Consolas', 20)).grid(row=0, column=0)
        self.y = 0
        for i in r:
            self.y += 1
            x = i.split('[')[0].split('(')[0]
            tk.Label(w, text=x, font=('Consolas', 10)).grid(row=self.y, column=1)
        self.y += 1
        tk.Button(w, text="prev", command=self.prev, font=('Consolas', 20)).grid(row=self.y, column=0)
        tk.Button(w, text="Play", command=self.play, font=('Consolas', 20)).grid(row=self.y, column=1)
        tk.Button(w, text="next", command=self.next1, font=('Consolas', 20)).grid(row=self.y, column=2)
        tk.Button(w, text="Pause", command=self.pause, font=('Consolas', 20)).grid(row=self.y + 1, column=1)
        tk.Button(w, text="unpause", command=self.unpause, font=('Consolas', 20)).grid(row=self.y + 2, column=1)
        tk.Button(w, text="stop", command=self.stop, font=('Consolas', 20)).grid(row=self.y + 3, column=1)
        for i in r:
            j += 1
            if j == 1:
                a = Node(i)
                self.l.headval = a
                self.l.start = a
                a.nextval = self.l.start
                a.preval = self.l.start
            else:
                a = Node(i)
                self.l.start.nextval = a
                a.preval = self.l.start
                a.nextval = self.l.headval
                self.l.headval.preval = a
                self.l.start = a

    def autoplay(self):
        while True:
            if self.var != 3:
                os.chdir(os.path.join(self.cwd, 'playlist'))
                mixer.music.load(self.l.start.linker[:-1])
                mixer.music.play()
                os.chdir(self.cwd)
            else:
                mixer.music.unpause()
                self.var = 0
            while mixer.music.get_busy():
                continue
            if self.var == 1:
                self.var = 0
                break
            if self.var == 2:
                break
            self.l.start = self.l.start.nextval

    def next1(self):
        self.var = 1
        self.stop()
        self.music_thread.join()
        self.l.start = self.l.start.nextval
        self.music_thread = threading.Thread(target=self.autoplay)
        self.music_thread.start()

    def prev(self):
        self.var = 1
        self.stop()
        self.music_thread.join()
        self.l.start = self.l.start.preval
        self.music_thread = threading.Thread(target=self.autoplay)
        self.music_thread.start()

    def play(self):
        self.l.start = self.l.headval
        mixer.init()
        self.music_thread = threading.Thread(target=self.autoplay)
        self.music_thread.start()

    def pause(self):
        self.var = 2
        mixer.music.pause()
        self.music_thread.join()

    def unpause(self):
        self.var = 3
        self.music_thread = threading.Thread(target=self.autoplay)
        self.music_thread.start()

    def stop(self):
        self.var = 1
        mixer.music.stop()
        mixer.music.unload()
        self.music_thread.join()

    def download_audio(self, link):
        with yt_dlp.YoutubeDL({'extract_audio': True}) as video:
            info_dict = video.extract_info(link, download=True)
            video_title = info_dict['title']
            return video_title

    def download(self):
        win = tk.Toplevel()
        win.title("download")
        tk.Label(win, text="Enter the search string for the song you want to download ... ",
                 font=('Consolas', 20)).grid(row=1, column=0)
        self.x = tk.StringVar()
        tk.Entry(win, textvariable=self.x).grid(row=1, column=1)
        tk.Button(win, text="Search", command=self.search, font=('Consolas', 20)).grid(row=3, column=1)

    def search(self):
        s = self.x.get()
        a = Search(s)
        result = a.results
        query = ((str(result[0]).split("="))[-1])[0:-1]
        vidname = self.download_audio('https://www.youtube.com/watch?v=' + query)
        vidname += " [" + query + "]"
        vidname = vidname.replace('|', '｜')
        vidname = vidname.replace(': ', '： ')
        Mp4 = vidname + ".mp4"
        Mp3 = vidname + ".mp3"
        Video = VideoFileClip(Mp4)
        Audio = Video.audio
        try:
            os.chdir(os.path.join(self.cwd, 'playlist'))
        except:
            os.mkdir(os.path.join(self.cwd, 'playlist'))
            os.chdir(os.path.join(self.cwd, 'playlist'))
        Audio.write_audiofile(Mp3)
        os.chdir(self.cwd)
        Audio.close()
        Video.close()
        os.remove(Mp4)
        data = SpotifyAPI.get_metadata(s)
        try:
            df = pd.read_csv(os.path.join(self.cwd, "metadata", "MusicData.csv"), encoding='utf-8')
            if len(data["artists"]) <= 1:
                data["artists"].append('')
            df.loc[len(df.index)] = [data["audio_features"]["id"], data["name"],
                                     data["artists"][0] + " | " + data["artists"][1], data["album"],
                                     data["release_date"], data["popularity"],
                                     data["audio_features"]["danceability"], data["audio_features"]["energy"],
                                     data["audio_features"]["key"], data["audio_features"]["loudness"],
                                     data["audio_features"]["mode"], data["audio_features"]["speechiness"],
                                     data["audio_features"]["acousticness"],
                                     data["audio_features"]["instrumentalness"],
                                     data["audio_features"]["liveness"], data["audio_features"]["valence"],
                                     data["audio_features"]["tempo"], data["audio_features"]["duration_ms"],
                                     data["audio_features"]["time_signature"]]
            df.to_csv(os.path.join(self.cwd, "metadata", "MusicData.csv"), index=False, encoding='utf-8')
        except:
            os.mkdir(os.path.join(self.cwd, "metadata"))
            df = open(os.path.join(self.cwd, "metadata", "MusicData.csv"), 'a', encoding='utf-8')
            df.write("id,Name,Artists,Album,Release Date,Popularity,danceability,energy,key,loudness,"
                     "mode,speechiness,acousticness,instrumentalness,liveness,valence,tempo,duration_ms,"
                     "time_signature\n")
            if len(data["artists"]) <= 1:
                data["artists"].append('')
            df.write(data["audio_features"]["id"] + "," + data["name"] + "," +
                     data["artists"][0] + " | " + data["artists"][1] + "," +
                     data["album"] + "," + data["release_date"] + "," +
                     str(data["popularity"]) + "," +
                     str(data["audio_features"]["danceability"]) + "," +
                     str(data["audio_features"]["energy"]) + "," +
                     str(data["audio_features"]["key"]) + "," +
                     str(data["audio_features"]["loudness"]) + "," +
                     str(data["audio_features"]["mode"]) + "," +
                     str(data["audio_features"]["speechiness"]) + "," +
                     str(data["audio_features"]["acousticness"]) + "," +
                     str(data["audio_features"]["instrumentalness"]) + "," +
                     str(data["audio_features"]["liveness"]) + "," +
                     str(data["audio_features"]["valence"]) + "," +
                     str(data["audio_features"]["tempo"]) + "," +
                     str(data["audio_features"]["duration_ms"]) + "," +
                     str(data["audio_features"]["time_signature"]) + "\n")
            df.close()
        f = open(os.path.join(self.cwd, "playlist", "musicfiles.txt"), "a", encoding='utf-8')
        f.write(Mp3 + '\n')
        f.close()

    def main(self):
        root = tk.Tk()
        root.title("main")
        top = tk.Frame(root)
        top.pack()
        top.grid(row=0, column=0)
        tk.Label(top, text="Welcome to our music player !!!", font=('Consolas', 20)).grid(row=0, column=1)
        tk.Button(root, text="DOWNLOAD MUSIC", command=self.download, font=('Consolas', 18, 'bold'), padx=20).grid(
            row=1, column=0)
        tk.Button(root, text="YOUR LIBRARY", command=self.inputer, font=('Consolas', 18, 'bold')).grid(row=2, column=0)
        root.mainloop()

if __name__ == "__main__":
    player = MusicPlayer()
    player.main()
