import tkinter as tk
from tkinter import filedialog, messagebox
import re
from collections import defaultdict

# Prøv å lese filen med utf-8 først, og fall tilbake til iso-8859-1 om nødvendig
def read_file_with_fallback(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='strict') as file:
            return file.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='iso-8859-1', errors='replace') as file:
            return file.readlines()

def extract_months_from_file(filepath):
    months = defaultdict(list)
    try:
        lines = read_file_with_fallback(filepath)

        # Bruk regex for å finne linjer som begynner med "15" og hente datoene
        for line in lines:
            if line.startswith('"15"'):
                # Ekstrakter dato fra linjen (format er "YYYYMMDD")
                match = re.search(r'"(\d{8})"', line)
                if match:
                    date_str = match.group(1)
                    year = date_str[:4]
                    month = date_str[4:6]
                    months[f"{month}-{year}"].append(line)
    except Exception as e:
        messagebox.showerror("Feil", f"Det oppstod en feil ved lesing av filen: {str(e)}")

    return sorted(months.keys())  # Returner sortert liste av måneder i format MM-YYYY

def show_month_popup(months):
    month_window = tk.Toplevel()  # Opprett et nytt Toplevel-vindu for månedslisten
    month_window.title("Eksisterende måneder i målfilen")
    
    label = tk.Label(month_window, text="Måneder i filen:", font=("Arial", 12, "bold"))
    label.pack(pady=10)

    listbox = tk.Listbox(month_window, font=("Arial", 10), width=20, height=10)
    for month in months:
        listbox.insert(tk.END, month)
    listbox.pack(pady=10)

    ok_button = tk.Button(month_window, text="OK", command=month_window.destroy, font=("Arial", 10, "bold"), bg="lightblue", fg="black")
    ok_button.pack(pady=10)

    # Venter til brukeren lukker popup-vinduet før scriptet fortsetter
    month_window.transient()  # Gjør pop-up modal (brukeren må håndtere den før de kan gå tilbake)
    month_window.grab_set()  # Sett fokus på pop-up-vinduet
    month_window.wait_window()  # Stopp utførelsen av resten av koden til vinduet lukkes

def merge_txt_files():
    # Opprett en Tk-interaksjon
    root = tk.Tk()
    root.withdraw()  # Skjul hovedvinduet

    # Velg målfil som allerede inneholder data
    target_file = filedialog.askopenfilename(title="Velg .txt-fil som de andre skal slås sammen med", filetypes=[("Text files", "*.txt")])

    if not target_file:
        messagebox.showinfo("Ingen målfil valgt", "Ingen fil ble valgt for sammenslåing.")
        return

    # Finn månedene som allerede finnes i målfilen
    months_in_target_file = extract_months_from_file(target_file)

    if months_in_target_file:
        # Vis popup for å vise hvilke måneder som finnes
        show_month_popup(months_in_target_file)
    else:
        messagebox.showinfo("Ingen data", "Ingen måneder funnet i målfilen.")

    # Velg flere .txt-filer som skal slås sammen
    files_to_merge = filedialog.askopenfilenames(title="Velg .txt-filer som skal slås sammen", filetypes=[("Text files", "*.txt")])

    if not files_to_merge:
        messagebox.showinfo("Ingen filer valgt", "Ingen filer ble valgt.")
        return

    try:
        # Les innholdet av målfilen, ignorer feil med ukjente tegn
        target_content = "".join(read_file_with_fallback(target_file)).rstrip()  # Fjern unødvendige linjeskift fra slutten

        # Slå sammen innholdet fra alle valgte filer uten å legge til ekstra linjer
        for file in files_to_merge:
            file_content = "".join(read_file_with_fallback(file)).strip()  # Fjern unødvendige linjeskift fra begynnelsen og slutten
            if target_content:
                target_content += "\n"  # Legg til et enkelt linjeskift mellom filer
            target_content += file_content

        # Skriv det nye innholdet tilbake til målfilen
        with open(target_file, 'w', encoding='utf-8', errors='replace') as outfile:
            outfile.write(target_content)

        messagebox.showinfo("Suksess", f"Filene ble vellykket slått sammen med {target_file}")

    except Exception as e:
        messagebox.showerror("Feil", f"Det oppstod en feil under sammenslåingen: {str(e)}")


if __name__ == "__main__":
    merge_txt_files()
