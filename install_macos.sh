#!/bin/bash

##############################################################################
# PDF Renamer - Installation Script for macOS
# Script di installazione automatico per PDF Renamer
##############################################################################

set -e  # Interrompi se c'è un errore

# Colori per il terminale
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni di output
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  PDF Renamer - Installation Script${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Controlla se siamo nella directory corretta
check_directory() {
    print_step "Verifica directory..."
    
    if [ ! -f "pdf_renamer.py" ]; then
        print_error "pdf_renamer.py non trovato!"
        echo "Assicurati di eseguire questo script dalla cartella Fascicolo"
        exit 1
    fi
    
    print_success "Directory corretta"
}

# Controlla Python 3.9
check_python() {
    print_step "Verifica Python 3.9..."
    
    if ! command -v python3.9 &> /dev/null; then
        print_error "Python 3.9 non trovato!"
        echo "Installa Python 3.9 con: brew install python@3.9"
        exit 1
    fi
    
    VERSION=$(python3.9 --version)
    print_success "Trovato: $VERSION"
}

# Controlla tkinter
check_tkinter() {
    print_step "Verifica tkinter..."
    
    if ! python3.9 -c "import tkinter" 2>/dev/null; then
        print_error "tkinter non trovato!"
        echo "Installa con: brew install python-tk@3.9"
        exit 1
    fi
    
    print_success "tkinter disponibile"
}

# Installa PyInstaller
install_pyinstaller() {
    print_step "Installa PyInstaller..."
    
    if python3.9 -c "import PyInstaller" 2>/dev/null; then
        print_success "PyInstaller già installato"
    else
        echo "Installazione in corso..."
        python3.9 -m pip install --quiet pyinstaller
        print_success "PyInstaller installato"
    fi
}

# Pulisci build precedenti
clean_build() {
    print_step "Pulizia build precedenti..."
    
    rm -rf build/ dist/ pdf_renamer.spec 2>/dev/null || true
    print_success "Directory di build pulite"
}

# Crea l'app
build_app() {
    print_step "Creazione dell'app (questo potrebbe impiegare 1-2 minuti)..."
    
    python3.9 -m PyInstaller \
        --onefile \
        --windowed \
        --name "PDF Renamer" \
        --osx-bundle-identifier "com.studiomonaco.pdfrenamer" \
        pdf_renamer.py > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "App creata con successo"
    else
        print_error "Errore durante la creazione dell'app"
        exit 1
    fi
}

# Installa nella cartella Applicazioni
install_app() {
    print_step "Installazione nella cartella Applicazioni..."
    
    # Rimuovi versione precedente se esiste
    if [ -d "/Applications/PDF Renamer.app" ]; then
        rm -rf "/Applications/PDF Renamer.app"
        print_success "Versione precedente rimossa"
    fi
    
    # Copia l'app
    cp -r "dist/PDF Renamer.app" "/Applications/"
    
    if [ $? -eq 0 ]; then
        print_success "App installata in /Applications"
    else
        print_error "Errore durante l'installazione"
        exit 1
    fi
}

# Pulisci file temporanei
cleanup_temp() {
    print_step "Pulizia file temporanei..."
    
    rm -rf build/ pdf_renamer.spec
    print_success "File temporanei rimossi"
}

# Main
main() {
    print_header
    
    check_directory
    check_python
    check_tkinter
    install_pyinstaller
    clean_build
    build_app
    install_app
    cleanup_temp
    
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ Installazione completata con successo!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "\n${BLUE}Come avviare l'app:${NC}"
    echo "  1. Apri Spotlight (Cmd + Space)"
    echo "  2. Digita 'PDF Renamer'"
    echo "  3. Premi Enter"
    echo ""
    echo -e "Oppure cerca l'app in ${BLUE}Finder → Applicazioni${NC}\n"
}

# Esegui
main
