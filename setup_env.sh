#!/bin/bash

# Configuration pour s'arreter en cas d'erreur
set -e

echo "=== Debut de la configuration de l'environnement ==="

# 1. Verification de la presence de Python
if ! command -v python3 &> /dev/null
then
    echo "[ERREUR] Python3 n'est pas installe sur ce systeme."
    exit 1
fi

# 2. Creation du fichier temporaire requirements.txt
echo "Creation du fichier de dependances temporaire..."
cat << EOF > requirements.txt
altgraph==0.17.5
beautifulsoup4==4.14.3
certifi==2026.5.20
charset-normalizer==3.4.7
deep-translator==1.11.4
idna==3.16
packaging==26.2
pillow==12.2.0
pyinstaller==6.20.0
pyinstaller-hooks-contrib==2026.5
PyQt6==6.11.0
PyQt6-Qt6==6.11.1
PyQt6-WebEngine==6.11.0
PyQt6-WebEngine-Qt6==6.11.1
PyQt6_sip==13.11.1
requests==2.34.2
setuptools==82.0.1
soupsieve==2.8.3
typing_extensions==4.15.0
urllib3==2.7.0
EOF

# 3. Creation du venv nomme env
if [ -d "env" ]; then
    echo "Le dossier env existe deja. Suppression de l'ancien dossier..."
    rm -rf env
fi

echo "Creation de l'environnement virtuel venv..."
python3 -m venv env

# 4. Activation du venv et mise a jour de pip
echo "Activation de l'environnement virtuel..."
source env/bin/activate

echo "Mise a jour de pip..."
pip install --upgrade pip

# 5. Installation des paquets
echo "Installation des dependances depuis requirements.txt..."
pip install -r requirements.txt

# 6. Nettoyage du fichier temporaire
echo "Nettoyage des fichiers temporaires..."
rm requirements.txt

echo "=== Configuration terminee avec succes ==="
echo "Pour activer l'environnement manuellement, tapez: source env/bin/activate"
