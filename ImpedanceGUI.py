import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class ImpedanceGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Impedance Analysis Tool")
        self.root.geometry("1200x800")

        self.frequency = None
        self.real = None
        self.imag = None
        self.current_plot = None
        self.file_path = tk.StringVar()
        self.title_var = tk.StringVar(value="Impedance Plot")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Data File:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(top, textvariable=self.file_path, width=70).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(top, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        ttk.Button(top, text="Load", command=self.load_file).grid(row=0, column=3, padx=5)

        ttk.Label(top, text="Plot Title:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        ttk.Entry(top, textvariable=self.title_var, width=40).grid(row=1, column=1, sticky="w", padx=5, pady=(10, 0))

        plot_frame = ttk.LabelFrame(self.root, text="Plot Options", padding=10)
        plot_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(plot_frame, text="Nyquist Plot", command=self.plot_nyquist).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(plot_frame, text="Bode Magnitude", command=self.plot_bode_magnitude).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(plot_frame, text="Bode Phase", command=self.plot_bode_phase).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(plot_frame, text="Show All in New Windows", command=self.show_all).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(plot_frame, text="Save Current Plot", command=self.save_plot).grid(row=0, column=4, padx=5, pady=5)

        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Load a file to begin")
        self.ax.grid(True, linestyle="--", alpha=0.6)

        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, canvas_frame)
        toolbar.update()

        top.columnconfigure(1, weight=1)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select impedance data file",
            filetypes=[
                ("Data files", "*.dat *.txt *.csv"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.file_path.set(path)

    def load_file(self):
        path = self.file_path.get().strip()
        if not path:
            messagebox.showwarning("No file selected", "Please choose a data file first.")
            return

        try:
            try:
                data = np.loadtxt(path, skiprows=1)
                if data.ndim == 1:
                    data = np.expand_dims(data, axis=0)
                if data.shape[1] < 3:
                    raise ValueError
            except Exception:
                data = np.loadtxt(path, delimiter=",", skiprows=1)
                if data.ndim == 1:
                    data = np.expand_dims(data, axis=0)
                if data.shape[1] < 3:
                    raise ValueError("The file must contain at least 3 columns: frequency, Z', Z''.")

            self.frequency = data[:, 0]
            self.real = data[:, 1]
            self.imag = data[:, 2]

            messagebox.showinfo("Success", "Data loaded successfully.")
            self.plot_nyquist()
        except Exception as e:
            messagebox.showerror("File Error", f"Could not load file:\n{e}")

    def _check_data(self):
        if self.frequency is None or self.real is None or self.imag is None:
            messagebox.showwarning("No data", "Please load a valid file first.")
            return False
        return True

    def _clear_ax(self):
        self.ax.clear()
        self.ax.grid(True, linestyle="--", alpha=0.6)

    def plot_nyquist(self):
        if not self._check_data():
            return
        self._clear_ax()
        self.ax.plot(self.real, -self.imag, "o-", label="Nyquist Plot")
        self.ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        self.ax.axvline(0, color="gray", linestyle="--", linewidth=0.8)
        self.ax.set_xlabel(r"Real Impedance ($Z'$) [$\Omega$]")
        self.ax.set_ylabel(r"Imaginary Impedance ($-Z''$) [$\Omega$]")
        self.ax.set_title(self.title_var.get() or "Nyquist Plot")
        self.ax.legend()
        self.ax.set_aspect("equal", adjustable="datalim")
        self.canvas.draw()
        self.current_plot = "nyquist"

    def plot_bode_magnitude(self):
        if not self._check_data():
            return
        magnitude = np.sqrt(self.real**2 + self.imag**2)
        self._clear_ax()
        self.ax.semilogx(self.frequency, 20 * np.log10(magnitude), "o-", label="Magnitude")
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Magnitude [dB]")
        self.ax.set_title(self.title_var.get() or "Bode Plot - Magnitude")
        self.ax.legend()
        self.canvas.draw()
        self.current_plot = "bode_magnitude"

    def plot_bode_phase(self):
        if not self._check_data():
            return
        phase = np.arctan2(self.imag, self.real) * 180 / np.pi
        self._clear_ax()
        self.ax.semilogx(self.frequency, phase, "o-", label="Phase", color="orange")
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Phase [Degrees]")
        self.ax.set_title(self.title_var.get() or "Bode Plot - Phase")
        self.ax.legend()
        self.canvas.draw()
        self.current_plot = "bode_phase"

    def show_all(self):
        if not self._check_data():
            return

        title = self.title_var.get() or "Impedance Analysis"

        plt.figure(f"{title} - Nyquist")
        plt.plot(self.real, -self.imag, "o-", label="Nyquist Plot")
        plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        plt.axvline(0, color="gray", linestyle="--", linewidth=0.8)
        plt.xlabel(r"Real Impedance ($Z'$) [$\Omega$]")
        plt.ylabel(r"Imaginary Impedance ($-Z''$) [$\Omega$]")
        plt.title("Nyquist Plot")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.axis("equal")

        magnitude = np.sqrt(self.real**2 + self.imag**2)
        plt.figure(f"{title} - Bode Magnitude")
        plt.semilogx(self.frequency, 20 * np.log10(magnitude), "o-", label="Magnitude")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Magnitude [dB]")
        plt.title("Bode Plot - Magnitude")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()

        phase = np.arctan2(self.imag, self.real) * 180 / np.pi
        plt.figure(f"{title} - Bode Phase")
        plt.semilogx(self.frequency, phase, "o-", label="Phase", color="orange")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Phase [Degrees]")
        plt.title("Bode Plot - Phase")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()

        plt.show()

    def save_plot(self):
        if self.current_plot is None:
            messagebox.showwarning("No plot", "Please generate a plot first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save plot",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
        )
        if path:
            self.figure.savefig(path, bbox_inches="tight")
            messagebox.showinfo("Saved", "Plot saved successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImpedanceGUI(root)
    root.mainloop()
