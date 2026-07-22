import tkinter as tk
import sys, os

import geometry, interface, input

def _resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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

    icon_path = _resource_path(os.path.join("assets", "icon.ico"))
    root.iconbitmap(icon_path)

    ui = interface.Interface(root=root, on_solve=on_solve, on_save=on_save, results=None, errors=None)

    root.mainloop()