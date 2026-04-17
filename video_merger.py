#!/usr/bin/env python3
"""
Module de fusion des stories en une seule vidéo
Utilise FFmpeg pour concaténer les vidéos et créer des transitions
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
import shutil


class VideoMerger:
    """Fusionne plusieurs vidéos/images en une seule vidéo"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
        
    def _check_ffmpeg(self) -> bool:
        """Vérifie que FFmpeg est installé"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ FFmpeg détecté: {version_line}")
                return True
        except Exception as e:
            print(f"⚠️  FFmpeg non trouvé: {e}")
            print("💡 Veuillez installer FFmpeg: https://ffmpeg.org/download.html")
        return False
    
    def get_video_info(self, video_path: Path) -> Tuple[int, int, float]:
        """Récupère les infos d'une vidéo (width, height, duration)"""
        try:
            cmd = [
                self.ffmpeg_path, "-i", str(video_path),
                "-f", "null", "-"
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            
            # Parser la sortie stderr pour trouver la durée et la résolution
            output = result.stderr
            
            # Extraire la résolution
            resolution_match = None
            for line in output.split('\n'):
                if 'Video:' in line:
                    parts = line.split(',')
                    for part in parts:
                        if 'x' in part and not '0x' in part:
                            try:
                                res = part.strip().split(' ')[0]
                                if 'x' in res:
                                    w, h = res.split('x')
                                    resolution_match = (int(w), int(h))
                            except:
                                pass
            
            # Extraire la durée
            duration = 0.0
            for line in output.split('\n'):
                if 'Duration:' in line:
                    try:
                        time_str = line.split('Duration: ')[1].split(',')[0]
                        h, m, s = time_str.split(':')
                        duration = float(h) * 3600 + float(m) * 60 + float(s)
                    except:
                        pass
            
            if resolution_match:
                return (*resolution_match, duration)
            return (1920, 1080, duration)  # Valeurs par défaut
            
        except Exception as e:
            print(f"⚠️  Impossible d'analyser {video_path}: {e}")
            return (1920, 1080, 0.0)
    
    def normalize_videos(self, video_files: List[Path], target_resolution: Tuple[int, int] = (1080, 1920)) -> List[Path]:
        """
        Normalise toutes les vidéos à la même résolution
        Format vertical 9:16 pour mobile (1080x1920)
        """
        normalized_files = []
        target_w, target_h = target_resolution
        
        print(f"\n🎬 Normalisation des vidéos en {target_w}x{target_h} (format 9:16)...")
        
        for i, video_path in enumerate(video_files, 1):
            output_path = video_path.parent / f"normalized_{i:04d}_{video_path.name}"
            
            cmd = [
                self.ffmpeg_path, "-y",
                "-i", str(video_path),
                "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                str(output_path)
            ]
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=300
                )
                if result.returncode == 0:
                    normalized_files.append(output_path)
                    print(f"  ✓ {video_path.name}")
                else:
                    print(f"  ✗ Erreur normalisation {video_path.name}")
                    normalized_files.append(video_path)  # Utiliser l'original
            except Exception as e:
                print(f"  ✗ Erreur: {e}")
                normalized_files.append(video_path)
                
        return normalized_files
    
    def create_concat_file(self, video_files: List[Path]) -> str:
        """Crée un fichier de concaténation FFmpeg"""
        concat_content = ""
        for video_path in video_files:
            # Échapper les caractères spéciaux pour FFmpeg
            escaped_path = str(video_path.absolute()).replace("'", "'\\''")
            concat_content += f"file '{escaped_path}'\n"
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(concat_content)
            return f.name
    
    def merge_videos_simple(self, video_files: List[Path], output_path: Path, 
                           add_transitions: bool = True) -> bool:
        """
        Fusionne les vidéos avec FFmpeg
        
        Args:
            video_files: Liste des chemins des vidéos
            output_path: Chemin de sortie
            add_transitions: Ajouter des transitions entre les vidéos
        """
        if not video_files:
            print("❌ Aucune vidéo à fusionner")
            return False
        
        print(f"\n🎬 Fusion de {len(video_files)} vidéos...")
        
        # Normaliser les vidéos si nécessaire
        normalized_files = self.normalize_videos(video_files)
        
        # Méthode simple: concaténation directe
        concat_file = self.create_concat_file(normalized_files)
        
        try:
            cmd = [
                self.ffmpeg_path, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                str(output_path)
            ]
            
            print(f"⏳ Concaténation en cours...")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600
            )
            
            # Nettoyer
            os.unlink(concat_file)
            
            if result.returncode == 0:
                print(f"✅ Vidéo fusionnée créée: {output_path}")
                
                # Afficher les infos
                w, h, duration = self.get_video_info(output_path)
                print(f"   📊 Résolution: {w}x{h}")
                print(f"   ⏱️  Durée: {duration:.1f}s")
                print(f"   📦 Taille: {output_path.stat().st_size / (1024*1024):.1f} MB")
                
                return True
            else:
                print(f"❌ Erreur FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la fusion: {e}")
            # Nettoyer en cas d'erreur
            try:
                os.unlink(concat_file)
            except:
                pass
            return False
        finally:
            # Nettoyer les fichiers normalisés
            for f in normalized_files:
                if 'normalized_' in f.name:
                    try:
                        f.unlink()
                    except:
                        pass
    
    def merge_with_transitions(self, video_files: List[Path], output_path: Path,
                               transition_duration: float = 0.5) -> bool:
        """
        Fusionne avec des transitions douces (fade)
        Plus complexe mais meilleur rendu
        """
        if len(video_files) < 2:
            # Une seule vidéo, pas besoin de transition
            return self.merge_videos_simple(video_files, output_path, False)
        
        print(f"\n🎬 Fusion avec transitions (fade {transition_duration}s)...")
        
        # Normaliser
        normalized_files = self.normalize_videos(video_files)
        
        # Créer le filtre complexe pour les transitions
        filter_parts = []
        inputs = []
        
        for i, video in enumerate(normalized_files):
            inputs.extend(["-i", str(video)])
        
        # Construire le filtre de transition
        # Format: [0:v][1:v]xfade=transition=fade:duration=0.5:offset=END[vt1];[vt1][2:v]...
        stream_count = len(normalized_files)
        
        if stream_count == 2:
            # Cas simple avec 2 vidéos
            filter_str = "[0:v][1:v]xfade=transition=fade:duration={dur}:offset={off}[v];[0:a][1:a]acrossfade=d={dur}[a]"
            # Calculer l'offset
            w, h, dur1 = self.get_video_info(normalized_files[0])
            offset = dur1 - transition_duration
            filter_str = filter_str.format(dur=transition_duration, off=offset)
            
        else:
            # Cas avec plus de vidéos
            parts = []
            current_offset = 0
            
            for i in range(stream_count - 1):
                if i == 0:
                    parts.append(f"[{i}:v][{i+1}:v]")
                else:
                    parts.append(f"[vt{i}][{i+1}:v]")
                
                w, h, dur = self.get_video_info(normalized_files[i])
                current_offset += dur - transition_duration
                parts.append(f"xfade=transition=fade:duration={transition_duration}:offset={current_offset}")
                
                if i < stream_count - 2:
                    parts.append(f"[vt{i+1}];")
                else:
                    parts.append("[v];")
            
            # Audio
            audio_parts = ["[0:a]"]
            for i in range(1, stream_count):
                audio_parts.append(f"[{i}:a]")
            audio_parts.append(f"amix=inputs={stream_count}:duration=longest[a]")
            
            filter_str = "".join(parts) + "".join(audio_parts)
        
        cmd = [
            self.ffmpeg_path, "-y",
            *inputs,
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600
            )
            
            if result.returncode == 0:
                print(f"✅ Vidéo avec transitions créée: {output_path}")
                w, h, duration = self.get_video_info(output_path)
                print(f"   📊 Résolution: {w}x{h}")
                print(f"   ⏱️  Durée: {duration:.1f}s")
                return True
            else:
                print(f"⚠️  Transitions échouées, utilisation méthode simple")
                print(f"   Erreur: {result.stderr[:200]}")
                return self.merge_videos_simple(video_files, output_path, False)
                
        except Exception as e:
            print(f"⚠️  Erreur transitions: {e}")
            return self.merge_videos_simple(video_files, output_path, False)
    
    def create_montage(self, input_dir: Path, output_filename: str = "story_montage.mp4",
                       keep_individual: bool = True, use_transitions: bool = True) -> Optional[Path]:
        """
        Crée un montage à partir de toutes les vidéos dans un dossier
        
        Args:
            input_dir: Dossier contenant les vidéos
            output_filename: Nom du fichier de sortie
            keep_individual: Garder les fichiers individuels
            use_transitions: Utiliser des transitions
            
        Returns:
            Path du fichier créé ou None
        """
        # Trouver tous les fichiers vidéo
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(input_dir.glob(f"*{ext}"))
            video_files.extend(input_dir.glob(f"*{ext.upper()}"))
        
        # Trier par nom (qui contient l'index)
        video_files.sort(key=lambda x: x.name)
        
        if not video_files:
            print("❌ Aucune vidéo trouvée dans le dossier")
            return None
        
        print(f"\n🎥 {len(video_files)} vidéos trouvées dans {input_dir}")
        
        output_path = input_dir / output_filename
        
        if use_transitions:
            success = self.merge_with_transitions(video_files, output_path)
        else:
            success = self.merge_videos_simple(video_files, output_path)
        
        if success and not keep_individual:
            print("🗑️  Suppression des fichiers individuels...")
            for video in video_files:
                try:
                    video.unlink()
                except:
                    pass
        
        return output_path if success else None


def check_ffmpeg_installed() -> bool:
    """Vérifie si FFmpeg est installé"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def install_ffmpeg_instructions():
    """Affiche les instructions d'installation FFmpeg"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║  FFmpeg n'est pas installé sur votre système                    ║
╠════════════════════════════════════════════════════════════════╣
║  Installation rapide:                                           ║
║                                                                 ║
║  Windows (avec Chocolatey):                                     ║
║    choco install ffmpeg                                         ║
║                                                                 ║
║  Windows (avec Scoop):                                          ║
║    scoop install ffmpeg                                         ║
║                                                                 ║
║  Téléchargement manuel:                                         ║
║    https://ffmpeg.org/download.html                             ║
║                                                                 ║
║  macOS:                                                         ║
║    brew install ffmpeg                                          ║
║                                                                 ║
║  Linux (Ubuntu/Debian):                                         ║
║    sudo apt-get install ffmpeg                                  ║
╚════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    # Test
    if not check_ffmpeg_installed():
        install_ffmpeg_instructions()
    else:
        print("✅ FFmpeg est installé et fonctionnel!")
        
        # Test basique
        merger = VideoMerger()
        print("\n🧪 Test du fusionneur de vidéos")