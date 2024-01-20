import os
import pygame
from tkinter import Tk, filedialog, Button, Listbox, Scrollbar, Label, Canvas, PhotoImage
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter
import eyed3
import io

class MusicPlayer:
    def __init__(self, master):
        self.master = master
        master.title("Simple Music Player")

        self.current_track = None
        self.playing = False
        self.playlist = []

        # Create a canvas with no background
        self.canvas = Canvas(master, width=750, height=600, bd=0, highlightthickness=0)
        self.canvas.pack()

        # Create GUI elements
        self.album_art_label = Label(self.canvas)
        self.album_art_label_window = self.canvas.create_window(375, 275, anchor="center", window=self.album_art_label)

        style = ttk.Style()
        style.configure("TButton", padding=10, font=("Helvetica", 10))

        self.select_button = ttk.Button(self.canvas, text="Select Track", command=self.select_track)
        self.select_button_window = self.canvas.create_window(375, 120, anchor="center", window=self.select_button)

        self.play_button = ttk.Button(self.canvas, text="Play", command=self.toggle_play)
        self.play_button_window = self.canvas.create_window(200, 200, anchor="center", window=self.play_button)

        self.next_button = ttk.Button(self.canvas, text="Next", command=self.play_next)
        self.next_button_window = self.canvas.create_window(375, 200, anchor="center", window=self.next_button)

        self.prev_button = ttk.Button(self.canvas, text="Previous", command=self.play_previous)
        self.prev_button_window = self.canvas.create_window(550, 200, anchor="center", window=self.prev_button)

        self.song_library_label = ttk.Label(self.canvas, text="Song Library", font=("Helvetica", 12))
        self.song_library_label_window = self.canvas.create_window(375, 300, anchor="center", window=self.song_library_label)

        self.song_listbox = Listbox(self.canvas, selectmode="SINGLE", font=("Helvetica", 10))
        self.song_listbox_window = self.canvas.create_window(375, 400, anchor="center", window=self.song_listbox)

        self.scrollbar = Scrollbar(self.canvas, orient="vertical")
        self.scrollbar.config(command=self.song_listbox.yview)
        self.scrollbar_window = self.canvas.create_window(570, 400, anchor="center", window=self.scrollbar)

        self.song_listbox.config(yscrollcommand=self.scrollbar.set)

        # Example songs for the song library
        self.populate_song_library()

        self.song_listbox.bind("<Double-Button-1>", self.load_selected_song)

        # Progress bar
        style.configure("TProgressbar",
                        thickness=20, troughcolor="gray", background="light blue", troughrelief="flat", borderwidth=0)
        self.progress_bar = ttk.Progressbar(self.canvas, orient="horizontal", length=600, mode="determinate",
                                            style="TProgressbar")
        self.progress_bar_window = self.canvas.create_window(375, 500, anchor="center", window=self.progress_bar)

        # Set initial value for the progress bar
        self.progress_bar["value"] = 0

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
                self.update_progress_bar()
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

        # Extract and display album art
        album_art = self.extract_album_art(file_path)
        if album_art:
            self.display_album_art(album_art)

        # Update progress bar
        self.update_progress_bar()

    def update_progress_bar(self):
        # Update progress bar based on the current position of the song
        if self.playing:
            length = pygame.mixer.music.get_pos() / 1000
            total_length = eyed3.load(self.current_track).info.time_secs
            progress_percentage = (length / total_length) * 100
            self.progress_bar["value"] = progress_percentage
            self.master.after(100, self.update_progress_bar)

    def extract_album_art(self, file_path):
        try:
            audiofile = eyed3.load(file_path)
            if audiofile.tag and audiofile.tag.images:
                # Assume the first image is the album art
                return audiofile.tag.images[0].image_data
        except Exception as e:
            print(f"Error extracting album art: {e}")
        return None

    def display_album_art(self, image_data):
        # Convert the image data to a Tkinter PhotoImage
        image = Image.open(io.BytesIO(image_data))
        thumbnail = image.copy()
        thumbnail.thumbnail((750, 550))  # Resize to match the canvas size

        # Apply a blur effect to the thumbnail
        thumbnail = thumbnail.filter(ImageFilter.BLUR)

        album_art_photo = ImageTk.PhotoImage(thumbnail)

        # Set the thumbnail as the background
        self.canvas.create_image(375, 275, anchor="center", image=album_art_photo)

        # Update the album art label
        self.album_art_label.configure(image=album_art_photo)
        self.album_art_label.image = album_art_photo

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

# Create the Tkinter window
root = Tk()

# Create an instance of the MusicPlayer class
music_player = MusicPlayer(root)

# Run the Tkinter event loop
root.mainloop()
