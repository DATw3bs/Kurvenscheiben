import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import numpy as np
import matplotlib.pyplot as plt


# Globale Variablen
takt_data = []


# Funktionen zur Berechnung der harmonischen Übergänge
def calculate_harmonic_curves(takt_angles, x_positions, z_positions):
    theta_fine = np.linspace(0, 360, 1000)
    X_theta = np.zeros_like(theta_fine)
    Z_theta = np.zeros_like(theta_fine)
    
    for i in range(len(takt_angles) - 1):
        angle_start, angle_end = takt_angles[i], takt_angles[i + 1]
        x_start, x_end = x_positions[i], x_positions[i + 1]
        z_start, z_end = z_positions[i], z_positions[i + 1]

        mask = (theta_fine >= angle_start) & (theta_fine < angle_end)
        X_theta[mask] = (
            (x_end - x_start) / 2 * (1 - np.cos(np.pi * (theta_fine[mask] - angle_start) / (angle_end - angle_start))) + x_start
        )
        Z_theta[mask] = (
            (z_end - z_start) / 2 * (1 - np.cos(np.pi * (theta_fine[mask] - angle_start) / (angle_end - angle_start))) + z_start
        )
    
    return theta_fine, X_theta, Z_theta


# Funktionen für die GUI
def on_generate_takts():
    global takt_data
    try:
        takt_count = int(takt_count_entry.get())
        if takt_count < 2:
            raise ValueError("Die Taktanzahl muss mindestens 2 sein.")
        takt_data = [(i * (360 / takt_count), 0, 0) for i in range(takt_count + 1)]
        update_takt_table()
    except ValueError as e:
        messagebox.showerror("Fehler", f"Ungültige Taktanzahl: {e}")


def update_takt_table():
    tree.delete(*tree.get_children())
    for i, (angle, x, z) in enumerate(takt_data):
        tree.insert("", "end", values=(f"{angle:.2f}", f"{x:.2f}", f"{z:.2f}"))


def on_edit_takt():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Fehler", "Bitte einen Takt auswählen!")
        return

    index = tree.index(selected_item[0])
    try:
        new_x = simpledialog.askfloat("X-Position", f"Neue X-Position für Takt {index}:")
        new_z = simpledialog.askfloat("Z-Position", f"Neue Z-Position für Takt {index}:")
        if new_x is not None:
            takt_data[index] = (takt_data[index][0], new_x, takt_data[index][2])
        if new_z is not None:
            takt_data[index] = (takt_data[index][0], takt_data[index][1], new_z)
        update_takt_table()
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Bearbeiten: {e}")


def on_plot_curves():
    if not takt_data or len(takt_data) < 2:
        messagebox.showerror("Fehler", "Bitte zuerst Takte generieren!")
        return

    try:
        angles = [t[0] for t in takt_data]
        x_positions = [t[1] for t in takt_data]
        z_positions = [t[2] for t in takt_data]

        theta_fine, X_theta, Z_theta = calculate_harmonic_curves(angles, x_positions, z_positions)

        R_x = x_diameter_entry.get() / 2  # Radius X
        R_z = z_diameter_entry.get() / 2  # Radius Z

        x_coords_z = [(R_z + Z_theta[i]) * np.cos(np.radians(theta_fine[i])) for i in range(len(theta_fine))]
        y_coords_z = [(R_z + Z_theta[i]) * np.sin(np.radians(theta_fine[i])) for i in range(len(theta_fine))]

        x_coords_x = [(R_x + X_theta[i]) * np.cos(np.radians(theta_fine[i])) for i in range(len(theta_fine))]
        y_coords_x = [(R_x + X_theta[i]) * np.sin(np.radians(theta_fine[i])) for i in range(len(theta_fine))]

        fig, axes = plt.subplots(1, 4, figsize=(24, 6))

        axes[0].plot(theta_fine, Z_theta, label="Z(θ) [mm]", color="blue")
        axes[0].set_title("Harmonische Z(θ)-Kurve")
        axes[0].set_xlabel("Winkel θ [°]")
        axes[0].set_ylabel("Z(θ) [mm]")
        axes[0].grid(True)
        axes[0].legend()

        axes[1].plot(theta_fine, X_theta, label="X(θ) [mm]", color="orange")
        axes[1].set_title("Harmonische X(θ)-Kurve")
        axes[1].set_xlabel("Winkel θ [°]")
        axes[1].set_ylabel("X(θ) [mm]")
        axes[1].grid(True)
        axes[1].legend()

        axes[2].plot(x_coords_z, y_coords_z, label="XY für Z-Kurve", color="purple")
        axes[2].set_title("XY-Diagramm (Z-Kurve)")
        axes[2].set_xlabel("X [mm]")
        axes[2].set_ylabel("Y [mm]")
        axes[2].axis("equal")
        axes[2].grid(True)
        axes[2].legend()

        axes[3].plot(x_coords_x, y_coords_x, label="XY für X-Kurve", color="green")
        axes[3].set_title("XY-Diagramm (X-Kurve)")
        axes[3].set_xlabel("X [mm]")
        axes[3].set_ylabel("Y [mm]")
        axes[3].axis("equal")
        axes[3].grid(True)
        axes[3].legend()

        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Plotten: {e}")


# GUI-Erstellung
root = tk.Tk()
root.title("Harmonische Kurvenberechnung")

# Eingabebereich
input_frame = ttk.LabelFrame(root, text="Einstellungen", padding="10")
input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

ttk.Label(input_frame, text="Taktzahl:").grid(row=0, column=0, padx=5, pady=5)
takt_count_entry = ttk.Entry(input_frame, width=10)
takt_count_entry.grid(row=0, column=1, padx=5)
takt_count_entry.insert(0, "6")

# Funktionen zur Synchronisation von Slider und Eingabefeld
def update_x_slider(value):
    x_value_entry.delete(0, tk.END)
    x_value_entry.insert(0, f"{float(value):.0f}")

def update_x_entry(*args):
    try:
        value = float(x_value_entry.get())
        if 40 <= value <= 200:
            x_diameter_entry.set(value)
        else:
            raise ValueError
    except ValueError:
        x_value_entry.delete(0, tk.END)
        x_value_entry.insert(0, f"{x_diameter_entry.get():.0f}")

def update_z_slider(value):
    z_value_entry.delete(0, tk.END)
    z_value_entry.insert(0, f"{float(value):.0f}")

def update_z_entry(*args):
    try:
        value = float(z_value_entry.get())
        if 40 <= value <= 200:
            z_diameter_entry.set(value)
        else:
            raise ValueError
    except ValueError:
        z_value_entry.delete(0, tk.END)
        z_value_entry.insert(0, f"{z_diameter_entry.get():.0f}")

# Innen-Durchmesser X
ttk.Label(input_frame, text="Innen-Durchmesser X (mm):").grid(row=1, column=0, padx=5, pady=5)
x_value_entry = ttk.Entry(input_frame, width=6, justify="center")
x_value_entry.grid(row=1, column=2, padx=5)
x_value_entry.insert(0, "80")
x_value_entry.bind("<Return>", update_x_entry)

x_diameter_entry = ttk.Scale(input_frame, from_=40, to=200, orient="horizontal", command=update_x_slider)
x_diameter_entry.grid(row=1, column=1, padx=5)
x_diameter_entry.set(80)

# Innen-Durchmesser Z
ttk.Label(input_frame, text="Innen-Durchmesser Z (mm):").grid(row=2, column=0, padx=5, pady=5)
z_value_entry = ttk.Entry(input_frame, width=6, justify="center")
z_value_entry.grid(row=2, column=2, padx=5)
z_value_entry.insert(0, "80")
z_value_entry.bind("<Return>", update_z_entry)

z_diameter_entry = ttk.Scale(input_frame, from_=40, to=200, orient="horizontal", command=update_z_slider)
z_diameter_entry.grid(row=2, column=1, padx=5)
z_diameter_entry.set(80)

# Buttons
button_frame = ttk.Frame(root, padding="10")
button_frame.grid(row=2, column=0)

ttk.Button(button_frame, text="Takte generieren", command=on_generate_takts).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Takt bearbeiten", command=on_edit_takt).grid(row=0, column=1, padx=5)
ttk.Button(button_frame, text="Kurven anzeigen", command=on_plot_curves).grid(row=0, column=2, padx=5)

# Tabelle
table_frame = ttk.LabelFrame(root, text="Takte", padding="10")
table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
columns = ("Winkel", "X-Position", "Z-Position")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=0, column=0, sticky=(tk.W, tk.E))

root.mainloop()
