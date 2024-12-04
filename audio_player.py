import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from pydub.playback import play
from Crypto.Cipher import AES

# AES Key (32 bytes for AES-256)
AES_KEY = bytes([
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
    0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
])

# Initialization Vector (16 bytes)
AES_IV = bytes([
    0xA0, 0xB1, 0xC2, 0xD3, 0xE4, 0xF5, 0xA6, 0xB7,
    0xC8, 0xD9, 0xE0, 0xF1, 0xA2, 0xB3, 0xC4, 0xD5
])

def decrypt_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()

    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_file, 'wb') as f:
        if len(decrypted_data) > 16:
            f.write(decrypted_data[16:])

def play_audio(file_path):
    audio = AudioSegment.from_wav(file_path)
    play(audio)

def load_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        status_label.config(text=f"Selected File: {os.path.basename(file_path)}")
        return file_path
    return None

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if file_path:
        return file_path
    return None

def decrypt_and_save():
    input_file = load_file()
    if input_file:
        output_file = save_file()
        if output_file:
            try:
                decrypt_file(input_file, output_file)
                status_label.config(text=f"Decryption successful! Saved to: {os.path.basename(output_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {e}")

def decrypt_and_play():
    input_file = load_file()
    if input_file:
        try:
            temp_file = "temp_decrypted.wav"
            decrypt_file(input_file, temp_file)
            play_audio(temp_file)
            os.remove(temp_file)
        except Exception as e:
            messagebox.showerror("Error", f"Decryption or Playback failed: {e}")

app = tk.Tk()
app.title("AES File Decryption")
app.geometry("400x200")

load_btn = tk.Button(app, text="Load Encrypted File", command=load_file)
save_btn = tk.Button(app, text="Decrypt and Save File", command=decrypt_and_save)
play_btn = tk.Button(app, text="Decrypt and Play File", command=decrypt_and_play)
status_label = tk.Label(app, text="Status: Waiting for user input", wraplength=300)

load_btn.pack(pady=10)
save_btn.pack(pady=10)
play_btn.pack(pady=10)
status_label.pack(pady=10)

app.mainloop()