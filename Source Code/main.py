import tkinter as tk
from pathlib import Path

import geometry, interface, input

def on_solve():
    inputs = ui.get_inputs_on_solve()

    input_errors = input.process_inputs_on_solve(inputs)
    if input_errors:
        ui.errors = input_errors
        ui.show_errors()
        return
    
    results, solver_errors = geometry.generate_aerospike_contour(inputs)
    if solver_errors:
        ui.errors = solver_errors
        ui.show_errors()
        return
    
    ui.results = results
    ui.show_output()
    ui.show_results()


def on_save():
    ui.save_file()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Aerospike')
    root.geometry('570x330')
    root.resizable(False, False)

    ICON = Path(__file__).resolve().parent / "assets" / "icon.ico"
    root.iconbitmap(ICON)

    ui = interface.Interface(root=root, on_solve=on_solve, on_save=on_save, results=None, errors=None)

    root.mainloop()