import os
import pygame
from tkinter import Tk, filedialog, Button, Label, Listbox, Scrollbar, DoubleVar
from tkinter import ttk, Canvas

class MusicPlayer:
    def __init__(self, master):
        self.master = master
        master.title("Music Player")

        self.current_track = None
        self.playing = False
        self.playlist = []

        # Create a canvas
        self.canvas = Canvas(master, width=750, height=550, bg="#a7cf70")
        self.canvas.pack()

        # Create GUI elements
        self.label = Label(self.canvas, text="No track selected", font=("Helvetica", 12))
        self.label_window = self.canvas.create_window(375, 50, anchor="center", window=self.label)

        style = ttk.Style()
        style.configure("TButton", padding=10, font=("Helvetica", 10), background="#4CAF50", foreground="black")
        style.map("TButton", background=[("active", "#45a049")])

        self.select_button = ttk.Button(self.canvas, text="Select Track", command=self.select_track, style="TButton")
        self.select_button_window = self.canvas.create_window(375, 120, anchor="center", window=self.select_button)

        self.play_button = ttk.Button(self.canvas, text="Play", command=self.toggle_play, style="TButton")
        self.play_button_window = self.canvas.create_window(200, 200, anchor="center", window=self.play_button)

        self.next_button = ttk.Button(self.canvas, text="Next", command=self.play_next, style="TButton")
        self.next_button_window = self.canvas.create_window(375, 200, anchor="center", window=self.next_button)

        self.prev_button = ttk.Button(self.canvas, text="Previous", command=self.play_previous, style="TButton")
        self.prev_button_window = self.canvas.create_window(550, 200, anchor="center", window=self.prev_button)

        # Create a progress bar
        self.progress_bar_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(self.canvas, variable=self.progress_bar_var, length=600, mode="determinate")
        self.progress_bar_window = self.canvas.create_window(375, 300, anchor="center", window=self.progress_bar)

        self.song_library_label = ttk.Label(self.canvas, text="Song Library", font=("Helvetica", 12))
        self.song_library_label_window = self.canvas.create_window(375, 420, anchor="center", window=self.song_library_label)

        self.song_listbox = Listbox(self.canvas, selectmode="SINGLE", font=("Helvetica", 10))
        self.song_listbox_window = self.canvas.create_window(375, 500, anchor="center", window=self.song_listbox)

        self.scrollbar = Scrollbar(self.canvas, orient="vertical")
        self.scrollbar.config(command=self.song_listbox.yview)
        self.scrollbar_window = self.canvas.create_window(570, 500, anchor="center", window=self.scrollbar)

        self.song_listbox.config(yscrollcommand=self.scrollbar.set)

        # Example songs for the song library
        self.populate_song_library()

        self.song_listbox.bind("<Double-Button-1>", self.load_selected_song)

        # Initialize Pygame
        pygame.init()

        # Update the progress bar periodically
        self.update_progress_bar()

    def select_track(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if file_path:
            self.playlist.append(file_path)
            self.update_song_library()
            if not self.current_track:
                self.load_and_play(file_path)

    def toggle_play(self):
        if self.current_track:
            if not self.playing:
                pygame.mixer.music.unpause()
                self.playing = True
                self.play_button.configure(text="Pause", style="TButton")
            else:
                pygame.mixer.music.pause()
                self.playing = False
                self.play_button.configure(text="Play", style="TButton")

    def play_next(self):
        if self.playlist:
            current_index = self.playlist.index(self.current_track)
            next_index = (current_index + 1) % len(self.playlist)
            self.load_and_play(self.playlist[next_index])

    def play_previous(self):
        if self.playlist:
            current_index = self.playlist.index(self.current_track)
            prev_index = (current_index - 1) % len(self.playlist)
            self.load_and_play(self.playlist[prev_index])

    def load_and_play(self, file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        self.playing = True
        self.play_button.configure(text="Pause", style="TButton")
        self.current_track = file_path
        self.label.configure(text=os.path.basename(file_path))

        # Reset progress bar
        self.progress_bar_var.set(0)

        # Update progress bar length based on the song's duration
        total_time = pygame.mixer.Sound(self.current_track).get_length()
        self.progress_bar.configure(maximum=total_time)

    def populate_song_library(self):
        # Example songs for the song library
        songs = ["Song 1", "Song 2", "Song 3"]
        for song in songs:
            self.song_listbox.insert("end", song)

    def update_song_library(self):
        self.song_listbox.delete(0, "end")
        for song in self.playlist:
            self.song_listbox.insert("end", os.path.basename(song))

    def load_selected_song(self, event):
        selected_song_index = self.song_listbox.curselection()
        if selected_song_index:
            selected_song = self.playlist[selected_song_index[0]]
            self.load_and_play(selected_song)

    def update_progress_bar(self):
        if self.playing:
            current_time = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
            self.progress_bar_var.set(current_time)
        self.master.after(100, self.update_progress_bar)

# Create the Tkinter window
root = Tk()

# Create an instance of the MusicPlayer class
music_player = MusicPlayer(root)

# Run the Tkinter event loop
root.mainloop()
