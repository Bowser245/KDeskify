import sys
import os
import stat
import locale
import requests
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urlparse
from deep_translator import GoogleTranslator
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QTextEdit)

# Modele de code de base pour les applications crees
CODE_MODELE = """import sys
import os
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView

class NavigateurWeb(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("__NOM_SITE__")
        self.setWindowIcon(QIcon("__CHEMIN_ICONE__"))
        self.setGeometry(100, 100, 1024, 768)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.vue_web = QWebEngineView()
        layout_principal.addWidget(self.vue_web)
        profil = self.vue_web.page().profile()
        profil.downloadRequested.connect(self.gerer_telechargement)

        self.url_verrouillee = QUrl("__URL_SITE__")
        self.vue_web.setUrl(self.url_verrouillee)

    def gerer_telechargement(self, download_item: QWebEngineDownloadRequest):
        nom_suggere = download_item.downloadFileName()
        chemin_sauvegarde, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le fichier",
            os.path.join(os.path.expanduser("~"), "Downloads", nom_suggere)
        )
        if not chemin_sauvegarde:
            return

        download_item.setDownloadDirectory(os.path.dirname(chemin_sauvegarde))
        download_item.setDownloadFileName(os.path.basename(chemin_sauvegarde))

        download_item.receivedBytesChanged.connect(
            lambda: self.mettre_a_jour_progression(nom_suggere, download_item.receivedBytes(), download_item.totalBytes())
        )
        download_item.isFinishedChanged.connect(
            lambda: self.telechargement_termine(download_item)
        )
        download_item.accept()

    def mettre_a_jour_progression(self, nom, recus, total):
        if total > 0:
            pourcentage = int((recus / total) * 100)
            print(f"Telechargement de {nom} : {pourcentage}% ({recus}/{total} octets)")
        else:
            print(f"Telechargement de {nom} en cours (taille inconnue)...")

    def telechargement_termine(self, download_item: QWebEngineDownloadRequest):
        if download_item.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            print(f"Succes ! Fichier enregistre ici : {download_item.downloadDirectory()}/{download_item.downloadFileName()}")
        elif download_item.state() == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            print("Le telechargement a ete annule.")
        elif download_item.state() == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            print(f"Erreur : Le telechargement a ete interrompu. Code : {download_item.interruptReason()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = NavigateurWeb()
    fenetre.show()
    sys.exit(app.exec())
"""
from PyQt6.QtGui import QIcon
class KDeskify(QWidget):
    def __init__(self):
        super().__init__()

        # Trouver le dossier contenant le script kdeskify.py
        self.chemin_exec = os.path.dirname(os.path.abspath(__file__))

        self.init_ui()
        self.detecter_langue_systeme()

    def init_ui(self):
        self.setWindowTitle("KDeskify")
        self.setWindowIcon(QIcon("pythoncreator.png"))
        self.resize(500, 400)

        layout = QVBoxLayout()

        self.label_url = QLabel("Entrez l'URL du site web :")
        layout.addWidget(self.label_url)

        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://example.com")
        layout.addWidget(self.input_url)

        self.btn_generer = QPushButton("Generer l'application")
        self.btn_generer.clicked.connect(self.lancer_generation)
        layout.addWidget(self.btn_generer)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        self.setLayout(layout)

    def detecter_langue_systeme(self):
        try:
            lang, _ = locale.getlocale()
            if lang:
                self.langue_cible = lang.split('_')[0]
            else:
                self.langue_cible = 'fr'
        except Exception:
            self.langue_cible = 'fr'

    def log(self, message):
        self.logs.append(message)
        QApplication.processEvents()

    def lancer_generation(self):
        url = self.input_url.text().strip()
        if not url:
            self.log("Erreur : L'URL est vide.")
            return

        try:
            parsed_url = urlparse(url)
            nom_site = parsed_url.netloc.replace("www.", "").split('.')[0]

            self.log(f"--- Debut de la generation pour {nom_site} ---")

            # 1. Extraction HTML et traduction de la description
            self.log("Recuperation des donnees du site...")
            reponse = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(reponse.text, 'html.parser')

            description = "Application web creee automatiquement"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc_originale = meta_desc.get('content').strip()
                try:
                    self.log(f"Traduction de la description en langue : {self.langue_cible}")
                    description = GoogleTranslator(source='auto', target=self.langue_cible).translate(desc_originale)
                except Exception as e:
                    self.log(f"Impossible de traduire, conservation du texte original. Erreur : {e}")
                    description = desc_originale

            # Extraction de l'icone
            self.log("Recherche de l'icone...")
            url_icone = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
            icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())

            if icon_link and icon_link.get('href'):
                href = icon_link.get('href')
                if href.startswith('http'):
                    url_icone = href
                else:
                    url_icone = f"{parsed_url.scheme}://{parsed_url.netloc}{href if href.startswith('/') else '/' + href}"

            chemin_icone_temporaire = os.path.join(self.chemin_exec, f"temp_{nom_site}_icon")
            chemin_icone_png = os.path.join(self.chemin_exec, f"{nom_site}_icon.png")

            try:
                img_data = requests.get(url_icone).content
                with open(chemin_icone_temporaire, 'wb') as f:
                    f.write(img_data)
                img = Image.open(chemin_icone_temporaire)
                img.save(chemin_icone_png, 'PNG')
                os.remove(chemin_icone_temporaire)
                self.log(f"Icone creee : {chemin_icone_png}")
            except Exception as e:
                self.log(f"Impossible de recuperer l'icone, utilisation d'une icone vide. Erreur : {e}")
                img = Image.new('RGB', (64, 64), color = 'blue')
                img.save(chemin_icone_png, 'PNG')

            # 2. Ecriture du fichier Python cible
            nom_fichier_py = f"{nom_site}.py"
            chemin_py = os.path.join(self.chemin_exec, nom_fichier_py)

            code_final = CODE_MODELE
            code_final = code_final.replace("__NOM_SITE__", nom_site.capitalize())
            code_final = code_final.replace("__CHEMIN_ICONE__", chemin_icone_png)
            code_final = code_final.replace("__URL_SITE__", url)

            with open(chemin_py, "w", encoding="utf-8") as f:
                f.write(code_final)
            self.log(f"Fichier Python cree : {chemin_py}")

            # 3. Compilation PyInstaller (on force l'execution dans le bon dossier)
            self.log("Compilation avec PyInstaller (veuillez patienter)...")
            os.chdir(self.chemin_exec)
            commande_pyinstaller = f"pyinstaller --onefile --windowed --noconsole --icon='{chemin_icone_png}' {nom_fichier_py}"
            os.system(commande_pyinstaller)

            # Trouver le chemin absolu vers le binaire cree dans le dossier dist/
            chemin_binaire = os.path.join(self.chemin_exec, "dist", nom_site)
            self.log(f"Chemin du binaire autonome detecte : {chemin_binaire}")

            # 4. Script Shell .sh modifié pour executer le binaire directement
            nom_sh = f"{nom_site}.sh"
            chemin_sh = os.path.join(self.chemin_exec, nom_sh)
            chemin_env_activate = os.path.join(self.chemin_exec, 'env/bin/activate')

            with open(chemin_sh, "w", encoding="utf-8") as f:
                f.write("#!/bin/bash\n")
                # On execute directement le binaire autonome entre guillemets pour securiser les espaces
                f.write(f'"{chemin_binaire}"\n')

            st = os.stat(chemin_sh)
            os.chmod(chemin_sh, st.st_mode | stat.S_IEXEC)
            self.log(f"Script Shell cree (execution du binaire) : {chemin_sh}")

            # 5. Raccourci .desktop pour Kubuntu
            dossier_desktop = os.path.expanduser("~/.local/share/applications")
            os.makedirs(dossier_desktop, exist_ok=True)
            chemin_desktop = os.path.join(dossier_desktop, f"{nom_site}.desktop")

            with open(chemin_desktop, "w", encoding="utf-8") as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write(f"Name={nom_site.capitalize()}\n")
                f.write(f"Comment={description}\n")
                f.write(f"Exec={chemin_sh}\n")
                f.write(f"Icon={chemin_icone_png}\n")
                f.write("Terminal=false\n")
                f.write("Categories=Network;WebBrowser;\n")

            st_d = os.stat(chemin_desktop)
            os.chmod(chemin_desktop, st_d.st_mode | stat.S_IEXEC)

            self.log(f"Raccourci Bureau cree : {chemin_desktop}")
            self.log("--- Generation terminee avec succes ! ---")

        except Exception as e:
            self.log(f"Une erreur critique est survenue : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    generateur = KDeskify()
    generateur.show()
    sys.exit(app.exec())
