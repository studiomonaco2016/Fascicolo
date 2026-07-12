import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import re


class PDFRenamer:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.pdf_files = []
        self.preview_data = []
        
    def find_pdfs(self):
        """Trova tutti i file PDF nella cartella e sottocartelle"""
        self.pdf_files = []
        for root, dirs, files in os.walk(self.root_dir):
            for file in sorted(files):
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    self.pdf_files.append(full_path)
        return self.pdf_files
    
    def generate_preview(self, prefix=""):
        """Genera un'anteprima dei rinominamenti"""
        self.preview_data = []
        
        for idx, old_path in enumerate(self.pdf_files, 1):
            directory = os.path.dirname(old_path)
            
            # Formatta il numero con due cifre (01, 02, etc)
            number = f"{idx:02d}"
            
            # Crea il nuovo nome
            if prefix:
                new_filename = f"{prefix}_{number}.pdf"
            else:
                new_filename = f"{number}.pdf"
            
            new_path = os.path.join(directory, new_filename)
            
            self.preview_data.append({
                'old_path': old_path,
                'new_path': new_path,
                'old_name': os.path.basename(old_path),
                'new_name': new_filename,
                'directory': directory
            })
        
        return self.preview_data
    
    def rename_files(self):
        """Applica i rinominamenti"""
        results = {'success': 0, 'error': 0, 'errors': []}
        
        for item in self.preview_data:
            try:
                if os.path.exists(item['old_path']):
                    os.rename(item['old_path'], item['new_path'])
                    results['success'] += 1
                else:
                    results['error'] += 1
                    results['errors'].append(f"File non trovato: {item['old_path']}")
            except Exception as e:
                results['error'] += 1
                results['errors'].append(f"Errore rinominando {item['old_name']}: {str(e)}")
        
        return results


class PDFRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Renamer - Fascicolo")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.renamer = None
        self.selected_folder = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia grafica"""
        
        # Frame superiore - Selezione cartella
        top_frame = ttk.LabelFrame(self.root, text="Selezione Cartella", padding="10")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Seleziona Cartella", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        self.folder_label = ttk.Label(top_frame, text="Nessuna cartella selezionata", foreground="gray")
        self.folder_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Frame configurazione
        config_frame = ttk.LabelFrame(self.root, text="Configurazione", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(config_frame, text="Prefisso (opzionale):").pack(side=tk.LEFT, padx=5)
        self.prefix_entry = ttk.Entry(config_frame, width=30)
        self.prefix_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(config_frame, text="Anteprima", command=self.show_preview).pack(side=tk.LEFT, padx=5)
        
        # Frame preview
        preview_frame = ttk.LabelFrame(self.root, text="Anteprima Rinominamenti", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar e Treeview
        scrollbar = ttk.Scrollbar(preview_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            preview_frame,
            columns=("num", "old_name", "new_name", "folder"),
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # Definisci le colonne
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("num", anchor=tk.CENTER, width=40, heading="N.")
        self.tree.column("old_name", anchor=tk.W, width=250, heading="Nome Originale")
        self.tree.column("new_name", anchor=tk.W, width=200, heading="Nuovo Nome")
        self.tree.column("folder", anchor=tk.W, width=200, heading="Cartella")
        
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("num", text="N.", anchor=tk.CENTER)
        self.tree.heading("old_name", text="Nome Originale", anchor=tk.W)
        self.tree.heading("new_name", text="Nuovo Nome", anchor=tk.W)
        self.tree.heading("folder", text="Cartella", anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame azioni
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.count_label = ttk.Label(action_frame, text="File trovati: 0", foreground="blue")
        self.count_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Applica Modifiche", command=self.apply_rename).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Cancella", command=self.clear_preview).pack(side=tk.RIGHT, padx=5)
    
    def select_folder(self):
        """Seleziona la cartella di lavoro"""
        folder = filedialog.askdirectory(title="Seleziona cartella con PDF")
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=folder, foreground="black")
            self.renamer = PDFRenamer(folder)
    
    def show_preview(self):
        """Mostra l'anteprima dei rinominamenti"""
        if not self.renamer:
            messagebox.showwarning("Attenzione", "Seleziona prima una cartella")
            return
        
        # Cerca i file PDF
        pdfs = self.renamer.find_pdfs()
        
        if not pdfs:
            messagebox.showinfo("Info", "Nessun file PDF trovato nella cartella")
            self.count_label.config(text="File trovati: 0")
            return
        
        # Genera l'anteprima
        prefix = self.prefix_entry.get().strip()
        preview = self.renamer.generate_preview(prefix)
        
        # Pulisci il treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Popola il treeview
        for idx, item in enumerate(preview, 1):
            relative_path = os.path.relpath(item['directory'], self.selected_folder)
            self.tree.insert("", tk.END, values=(
                idx,
                item['old_name'],
                item['new_name'],
                relative_path if relative_path != "." else "(principale)"
            ))
        
        self.count_label.config(text=f"File trovati: {len(pdfs)}")
        messagebox.showinfo("Anteprima", f"Trovati {len(pdfs)} file PDF.\nControlla l'anteprima sopra.")
    
    def apply_rename(self):
        """Applica i rinominamenti"""
        if not self.renamer or not self.renamer.preview_data:
            messagebox.showwarning("Attenzione", "Genera prima un'anteprima")
            return
        
        # Conferma
        response = messagebox.askyesno(
            "Conferma",
            f"Rinominare {len(self.renamer.preview_data)} file?\nQuesta azione non può essere annullata."
        )
        
        if not response:
            return
        
        # Applica i cambiamenti
        results = self.renamer.rename_files()
        
        # Mostra risultati
        message = f"Operazione completata!\n\nFile rinominati: {results['success']}"
        if results['error'] > 0:
            message += f"\nErrori: {results['error']}"
            if results['errors']:
                message += "\n\nDettagli errori:\n" + "\n".join(results['errors'][:5])
        
        messagebox.showinfo("Risultati", message)
        self.clear_preview()
    
    def clear_preview(self):
        """Pulisce l'anteprima"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.count_label.config(text="File trovati: 0")


def main():
    root = tk.Tk()
    app = PDFRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
