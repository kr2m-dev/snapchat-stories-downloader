#!/usr/bin/env python3
"""
Interface Graphique pour Snapchat Stories Downloader
Utilise CustomTkinter pour une interface moderne
"""

import os
import sys
import threading
from pathlib import Path
from typing import Optional, Callable
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import customtkinter as ctk
    from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkProgressBar, CTkCheckBox, CTkTextbox
    CTK_AVAILABLE = True
except ImportError:
    # Fallback sur tkinter standard
    CTK_AVAILABLE = False
    CTk = tk.Tk
    CTkFrame = tk.Frame
    CTkLabel = tk.Label
    CTkButton = tk.Button
    CTkEntry = tk.Entry
    CTkProgressBar = ttk.Progressbar
    CTkCheckBox = tk.Checkbutton
    CTkTextbox = tk.Text

from snapchat_downloader import SnapchatDownloader
from video_merger import VideoMerger, check_ffmpeg_installed


class DownloaderGUI:
    """Interface graphique principale"""
    
    def __init__(self):
        # Configuration du thème
        if CTK_AVAILABLE:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
        
        self.root = CTk() if CTK_AVAILABLE else tk.Tk()
        self.root.title("🚀 Snapchat Stories Downloader")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Snapchat_Stories"))
        self.concurrent_var = tk.IntVar(value=3)
        self.merge_var = tk.BooleanVar(value=True)
        self.transitions_var = tk.BooleanVar(value=True)
        self.keep_individual_var = tk.BooleanVar(value=True)
        self.is_downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title = CTkLabel(
            main_frame,
            text="📸 Snapchat Stories Downloader",
            font=("Helvetica", 24, "bold") if not CTK_AVAILABLE else ("Roboto", 24, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Description
        desc = CTkLabel(
            main_frame,
            text="Téléchargez et fusionnez les stories Snapchat\n"
                 "Collez l'URL du profil ou de la story ci-dessous",
            font=("Helvetica", 12) if not CTK_AVAILABLE else ("Roboto", 12)
        )
        desc.pack(pady=(0, 20))
        
        # URL Input
        url_frame = CTkFrame(main_frame)
        url_frame.pack(fill="x", padx=10, pady=5)
        
        url_label = CTkLabel(url_frame, text="🔗 URL Snapchat:")
        url_label.pack(side="left", padx=5)
        
        self.url_entry = CTkEntry(url_frame, textvariable=self.url_var, width=500)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        paste_btn = CTkButton(
            url_frame,
            text="📋 Coller",
            command=self.paste_url,
            width=80
        )
        paste_btn.pack(side="right", padx=5)
        
        # Exemples d'URLs
        examples_frame = CTkFrame(main_frame)
        examples_frame.pack(fill="x", padx=10, pady=5)
        
        examples_label = CTkLabel(examples_frame, text="💡 Exemples:")
        examples_label.pack(anchor="w", padx=5, pady=5)
        
        examples = [
            "https://snapchat.com/t/i9nYZgjr",
            "https://www.snapchat.com/add/citizennasri"
        ]
        
        for ex in examples:
            ex_btn = CTkButton(
                examples_frame,
                text=f"  {ex}",
                command=lambda url=ex: self.set_url(url),
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                anchor="w"
            )
            ex_btn.pack(fill="x", padx=5)
        
        # Options
        options_frame = CTkFrame(main_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        options_label = CTkLabel(options_frame, text="⚙️ Options:", font=("Helvetica", 14, "bold"))
        options_label.pack(anchor="w", padx=5, pady=5)
        
        # Dossier de sortie
        output_frame = CTkFrame(options_frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=5, pady=2)
        
        output_label = CTkLabel(output_frame, text="📁 Dossier de sortie:")
        output_label.pack(side="left")
        
        self.output_entry = CTkEntry(output_frame, textvariable=self.output_var, width=400)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        browse_btn = CTkButton(
            output_frame,
            text="Parcourir",
            command=self.browse_output,
            width=100
        )
        browse_btn.pack(side="right")
        
        # Concurrence
        concurrent_frame = CTkFrame(options_frame, fg_color="transparent")
        concurrent_frame.pack(fill="x", padx=5, pady=2)
        
        concurrent_label = CTkLabel(concurrent_frame, text="⚡ Téléchargements simultanés:")
        concurrent_label.pack(side="left")
        
        concurrent_slider = tk.Scale(
            concurrent_frame,
            from_=1,
            to=5,
            orient="horizontal",
            variable=self.concurrent_var,
            showvalue=True
        )
        concurrent_slider.pack(side="left", padx=10)
        
        # Checkboxes
        self.merge_checkbox = CTkCheckBox(
            options_frame,
            text="🎬 Fusionner les vidéos en une seule",
            variable=self.merge_var,
            command=self.on_merge_toggle
        )
        self.merge_checkbox.pack(anchor="w", padx=5, pady=5)
        
        self.transitions_checkbox = CTkCheckBox(
            options_frame,
            text="✨ Ajouter des transitions (fade)",
            variable=self.transitions_var
        )
        self.transitions_checkbox.pack(anchor="w", padx=25, pady=2)
        
        self.keep_checkbox = CTkCheckBox(
            options_frame,
            text="💾 Conserver les fichiers individuels",
            variable=self.keep_individual_var
        )
        self.keep_checkbox.pack(anchor="w", padx=25, pady=2)
        
        # Bouton principal
        self.download_btn = CTkButton(
            main_frame,
            text="🚀 Télécharger",
            command=self.start_download,
            font=("Helvetica", 16, "bold"),
            height=50
        )
        self.download_btn.pack(pady=20)
        
        # Barre de progression
        self.progress_label = CTkLabel(main_frame, text="Prêt")
        self.progress_label.pack()
        
        self.progress_bar = CTkProgressBar(main_frame, width=600)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Zone de log
        log_frame = CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        log_label = CTkLabel(log_frame, text="📋 Journal:")
        log_label.pack(anchor="w", padx=5, pady=5)
        
        self.log_text = CTkTextbox(log_frame, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Vérifier FFmpeg", command=self.check_ffmpeg)
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Initialiser l'état
        self.on_merge_toggle()
        
    def on_merge_toggle(self):
        """Active/désactive les options de fusion"""
        state = self.merge_var.get()
        if CTK_AVAILABLE:
            if state:
                self.transitions_checkbox.configure(state="normal")
                self.keep_checkbox.configure(state="normal")
            else:
                self.transitions_checkbox.configure(state="disabled")
                self.keep_checkbox.configure(state="disabled")
        else:
            self.transitions_checkbox.config(state="normal" if state else "disabled")
            self.keep_checkbox.config(state="normal" if state else "disabled")
    
    def paste_url(self):
        """Colle l'URL depuis le presse-papiers"""
        try:
            url = self.root.clipboard_get()
            self.url_var.set(url.strip())
        except:
            pass
    
    def set_url(self, url: str):
        """Définit l'URL"""
        self.url_var.set(url)
    
    def browse_output(self):
        """Ouvre le sélecteur de dossier"""
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)
    
    def log(self, message: str):
        """Ajoute un message au log"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def update_progress(self, value: float, message: str = ""):
        """Met à jour la barre de progression"""
        self.progress_bar.set(value)
        if message:
            self.progress_label.configure(text=message)
    
    def start_download(self):
        """Démarre le téléchargement dans un thread séparé"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL")
            return
        
        if "snapchat.com" not in url:
            messagebox.showerror("Erreur", "URL invalide. Doit contenir 'snapchat.com'")
            return
        
        if self.is_downloading:
            return
        
        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="⏳ Téléchargement en cours...")
        self.progress_bar.set(0)
        
        # Lancer dans un thread séparé
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_thread(self, url: str):
        """Thread de téléchargement"""
        try:
            output_dir = self.output_var.get()
            concurrent = self.concurrent_var.get()
            merge = self.merge_var.get()
            transitions = self.transitions_var.get()
            keep_individual = self.keep_individual_var.get()
            
            self.root.after(0, lambda: self.log(f"🚀 Démarrage du téléchargement..."))
            self.root.after(0, lambda: self.log(f"🔗 URL: {url}"))
            self.root.after(0, lambda: self.log(f"📁 Dossier: {output_dir}\n"))
            
            # Télécharger
            downloader = SnapchatDownloader(output_dir)
            success = downloader.download_sync(url, concurrent)
            
            if success:
                self.root.after(0, lambda: self.log("\n✅ Téléchargement terminé!"))
                
                # Fusionner si demandé
                if merge:
                    self.root.after(0, lambda: self.update_progress(0.8, "Fusion des vidéos..."))
                    self.root.after(0, lambda: self.log("\n🎬 Fusion des vidéos..."))
                    
                    if not check_ffmpeg_installed():
                        self.root.after(0, lambda: self.log("⚠️ FFmpeg non trouvé. Fusion impossible."))
                    else:
                        username = downloader.extract_username_from_url(url)
                        user_dir = Path(output_dir)
                        if username:
                            user_dir = user_dir / username
                        
                        if user_dir.exists():
                            merger = VideoMerger()
                            result = merger.create_montage(
                                user_dir,
                                output_filename=f"{username}_montage.mp4" if username else "story_montage.mp4",
                                keep_individual=keep_individual,
                                use_transitions=transitions
                            )
                            
                            if result:
                                self.root.after(0, lambda: self.log(f"\n✨ Montage créé: {result}"))
                            else:
                                self.root.after(0, lambda: self.log("\n⚠️ La fusion a échoué"))
                
                self.root.after(0, lambda: self.update_progress(1.0, "Terminé!"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Succès", 
                    "Téléchargement terminé!\n\n"
                    f"Emplacement: {output_dir}"
                ))
            else:
                self.root.after(0, lambda: self.log("\n❌ Le téléchargement a échoué"))
                self.root.after(0, lambda: self.update_progress(0, "Échec"))
                self.root.after(0, lambda: messagebox.showerror(
                    "Erreur",
                    "Le téléchargement a échoué.\n\n"
                    "Vérifiez que:\n"
                    "- Le profil est public\n"
                    "- Les stories ne sont pas expirées\n"
                    "- Votre connexion internet fonctionne"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"\n❌ Erreur: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.download_btn.configure(
                state="normal",
                text="🚀 Télécharger"
            ))
    
    def check_ffmpeg(self):
        """Vérifie FFmpeg"""
        if check_ffmpeg_installed():
            messagebox.showinfo("FFmpeg", "✅ FFmpeg est correctement installé")
        else:
            messagebox.showerror(
                "FFmpeg",
                "❌ FFmpeg n'est pas installé\n\n"
                "Téléchargez FFmpeg depuis:\n"
                "https://ffmpeg.org/download.html"
            )
    
    def show_about(self):
        """Affiche la boîte À propos"""
        messagebox.showinfo(
            "À propos",
            "🚀 Snapchat Stories Downloader v1.0\n\n"
            "Téléchargez et fusionnez les stories Snapchat\n"
            "avec un outil simple et efficace.\n\n"
            "Fonctionnalités:\n"
            "• Téléchargement parallèle\n"
            "• Fusion des vidéos\n"
            "• Transitions fluides\n"
            "• Interface graphique moderne\n\n"
            "Nécessite FFmpeg pour la fusion des vidéos."
        )
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()


def run_gui():
    """Point d'entrée pour l'interface graphique"""
    app = DownloaderGUI()
    app.run()


if __name__ == "__main__":
    run_gui()