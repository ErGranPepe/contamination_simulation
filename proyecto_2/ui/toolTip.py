import tkinter as tk

class ToolTip:
    """
    Clase para crear un tooltip asociado a un widget de Tkinter.
    El tooltip se muestra con un retraso cuando el ratón se posa sobre el widget
    y desaparece cuando el ratón se retira.
    """

    def __init__(self, widget, text="Tooltip text", delay=500):
        """
        Inicializa el tooltip.

        Args:
            widget (tk.Widget): El widget al que se asociará el tooltip.
            text (str): El texto que se mostrará en el tooltip.
            delay (int): Tiempo en milisegundos antes de mostrar el tooltip.
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.id_after = None

        # Vincular eventos del ratón al widget
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)

    def _on_enter(self, event):
        """Evento que se dispara cuando el ratón entra en el widget."""
        # Programar la aparición del tooltip después del retraso especificado
        self.id_after = self.widget.after(self.delay, self._show_tooltip)

    def _on_leave(self, event):
        """Evento que se dispara cuando el ratón sale del widget."""
        # Cancelar la aparición del tooltip si aún no ha aparecido
        if self.id_after:
            self.widget.after_cancel(self.id_after)
            self.id_after = None
        # Ocultar el tooltip si ya está visible
        self._hide_tooltip()

    def _on_motion(self, event):
        """Evento que se dispara cuando el ratón se mueve dentro del widget."""
        # Actualizar la posición del tooltip si ya está visible
        if self.tooltip_window:
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 20  # Ajuste horizontal
            y += self.widget.winfo_rooty() + 20  # Ajuste vertical
            self.tooltip_window.geometry(f"+{x}+{y}")

    def _show_tooltip(self):
        """Muestra el tooltip en una nueva ventana flotante."""
        if not self.tooltip_window:
            # Crear una ventana Toplevel para mostrar el tooltip
            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)  # Sin bordes ni barra de título

            # Posicionar la ventana cerca del cursor
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 20  # Ajuste horizontal
            y += self.widget.winfo_rooty() + 20  # Ajuste vertical
            self.tooltip_window.geometry(f"+{x}+{y}")

            # Crear un Label dentro de la ventana para mostrar el texto del tooltip
            label = tk.Label(
                self.tooltip_window,
                text=self.text,
                background="lightyellow",
                relief="solid",
                borderwidth=1,
                font=("Arial", 10)
            )
            label.pack(ipadx=5, ipady=2)

    def _hide_tooltip(self):
        """Oculta y destruye la ventana del tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ejemplo de ToolTip")

    label = tk.Label(root, text="Pasa el ratón por aquí", font=("Arial", 14))
    label.pack(pady=20, padx=20)

    button = tk.Button(root, text="Haz clic aquí")
    button.pack(pady=20)

    # Asociar tooltips a los widgets
    ToolTip(label, text="Este es un Label con información adicional.")
    ToolTip(button, text="Este es un botón. Haz clic para realizar una acción.")

    root.mainloop()
