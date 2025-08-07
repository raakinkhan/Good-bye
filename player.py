import tkinter as tk
from tkinter import filedialog
import os
import security_checks
import vlc
import time
import shutil
import glob
import tempfile

password = input("password-")


def clear_recent_files():
    recent_path = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Recent")
    for filename in os.listdir(recent_path):
        file_path = os.path.join(recent_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception:
            pass


def clear_media_player_history():
    wmp_path = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows Media")
    if os.path.exists(wmp_path):
        for root, dirs, files in os.walk(wmp_path):
            for file in files:
                if file.endswith(".wmdb") or file.startswith("Recent"):
                    try:
                        os.unlink(os.path.join(root, file))
                    except Exception as e:
                        print(e)
    mp_app_path = os.path.join(os.getenv("LOCALAPPDATA"), r"Packages\Microsoft.ZuneVideo_*\LocalState\Database")
    if os.path.exists(mp_app_path):
        for root, dirs, files in os.walk(mp_app_path):
            for file in files:
                if file.endswith(".db"):
                    try:
                        os.unlink(os.path.join(root, file))
                    except Exception as e:
                        print(e)

class StealthPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("CacheCleaner")
        self.instance = vlc.Instance(["--no-video-title", "--intf", "dummy", "--no-media-library", "--play-and-exit"])
        self.player = None
        # self.temp_file = None

        self.video_frame = tk.Frame(self.root, bg="black", width=800, height=600)
        self.video_frame.pack(fill="both", expand=True)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill="x", pady=5)

        self.load_button = tk.Button(self.control_frame, text="Load Encrypted File", command=self.load_and_play)
        self.load_button.pack(side="left", padx=5)
        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play)
        self.play_button.pack(side="left", padx=5)
        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side="left", padx=5)
        self.update_but = tk.Button(self.control_frame, text="update", command=self.update)
        self.update_but.pack(side="left", padx=5)


        self.seek_bar = tk.Scale(self.control_frame, from_=0, to=100, orient="horizontal", length=400,
                                 command=self.seek, showvalue=0)
        self.seek_bar.pack(side="left", padx=5, fill="x", expand=True)

        self.playing = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_and_play(self):
        enc_file = filedialog.askopenfilename(filetypes=[("Encrypted files", "*.enc")])
        if enc_file:
            try:
                s = time.time()
                decrypted_buffer = security_checks.AES_dec(enc_file, password)
                d = time.time()
                print("time-"+str(s-d))
                if decrypted_buffer.getbuffer().nbytes == 0:
                    raise ValueError("Decrypted buffer is empty. Wrong password or corrupted file?")

                # Save decrypted file for manual testing
                # debug_file = r"C:\Users\AZEEM\Desktop\programs\python\GOOD_BYE\safe\decrypted_test.enc"
                # with open(debug_file, "wb") as temp:
                #     temp.write(decrypted_buffer.read())
                # print(f"Decrypted file saved to: {debug_file}")
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp.write(decrypted_buffer.read())
                temp.flush()
                temp.close()  # close but NOT delete
                self.temp_path = temp.name  # keep the path around

                # Now hand it to VLC
                self.player = self.instance.media_player_new()
                media = self.instance.media_new(self.temp_path)
                self.player.set_media(media)
                self.player.set_hwnd(self.video_frame.winfo_id())
                self.play()



                # self.player = self.instance.media_player_new()
                # media = self.instance.media_new(debug_file)
                # self.player.set_media(media)



                # self.temp_file = debug_file  # Keep track for cleanup
            except Exception as e:
                print(f"Error loading file: {e}")
                self.on_close()

    def play(self):
        if self.player:
            self.player.play()
            self.playing = True
            # self.root.after(100, self.update)

    def pause(self):
        if self.player and self.playing:
            self.player.pause()
            self.playing = False

    def stop(self):
        if self.player:
            self.player.stop()
            self.playing = False
            self.seek_bar.set(0)

    def seek(self, value):
        if self.player:
            seek_time = int(float(value) * 1000)
            self.player.set_time(seek_time)
            print(f"Seeking to: {value} seconds")

    def update(self):
        print(self.player.video_get_width())
        print(self.player.video_get_height())
        print(self.player.get_length())
        total_length = self.player.get_length() / 1000
        self.seek_bar.config(to=total_length)
        if self.playing and self.player:
            current_time = self.player.get_time() / 1000
            total_length = self.player.get_length() / 1000
            if total_length > 0 and self.seek_bar["to"] != total_length:
                self.seek_bar.config(to=total_length)
            if total_length > 0:
                self.seek_bar.set(current_time)
            state = self.player.get_state()
            if state in [vlc.State.Ended, vlc.State.Error]:
                self.playing = False
                self.on_close()


    def on_close(self):
        if self.player:
            self.player.stop()
        if hasattr(self, "temp_path") and os.path.exists(self.temp_path):
            security_checks.secure_shred(self.temp_path)
            print("shreded")
        # if self.temp_file and os.path.exists(self.temp_file):
        #     security_checks.secure_shred(self.temp_file)
        # clear_recent_files()
        clear_media_player_history()
        self.root.destroy()

        # Expand env vars properly
        local_app_data = os.path.expandvars(r"%LocalAppData%")
        app_data = os.path.expandvars(r"%AppData%")

        # Clear thumbnail caches
        thumbcache_path = os.path.join(local_app_data, "Microsoft", "Windows", "Explorer")
        for db_file in glob.glob(os.path.join(thumbcache_path, "thumbcache_*.db")):
            try:
                os.remove(db_file)
            except PermissionError:
                # Force delete if locked (needs admin or killing Explorer)
                os.system(f"del /f /q \"{db_file}\"")  # /f forces it

        # Clear File Explorer recent files
        recent_path = os.path.join(local_app_data, "Microsoft", "Windows", "Recent")
        if os.path.exists(recent_path):
            for item in os.listdir(recent_path):
                item_path = os.path.join(recent_path, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:
                        shutil.rmtree(item_path)  # Nuke folders too
                except PermissionError:
                    pass  # Skip if locked—could force with admin

        # Clear VLC history without trashing all settings
        vlc_ini = os.path.join(app_data, "vlc", "vlc-qt-interface.ini")
        if os.path.exists(vlc_ini):
            try:
                with open(vlc_ini, "r") as f:
                    lines = f.readlines()
                with open(vlc_ini, "w") as f:
                    for line in lines:
                        if not line.strip().startswith("Recent"):  # Keep non-recent settings
                            f.write(line)
            except PermissionError:
                os.system(f"del /f /q \"{vlc_ini}\"")  # Force delete if locked

        # Clear VLC logs if they exist
        vlc_log = os.path.join(app_data, "vlc", "vlc.log")
        if os.path.exists(vlc_log):
            try:
                os.remove(vlc_log)
            except PermissionError:
                os.system(f"del /f /q \"{vlc_log}\"")
        clear_recent_files()
        print("closed successfully")




if __name__ == "__main__":
    root = tk.Tk()
    app = StealthPlayer(root)
    root.mainloop()
