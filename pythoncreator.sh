#!/bin/bash

# Force le script a se deplacer dans le dossier ou il se trouve
cd "$(dirname "${BASH_SOURCE[0]}")"

source env/bin/activate
python3 pythoncreator.py
desactivate
