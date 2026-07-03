import tkinter as tk

import solver, interface

def on_solve():
    inputs = ui.get_inputs_on_solve()
    
    results, solver_errors = solver.generate_aerospike_contour(inputs)

    ui.results, ui.errors = results, solver_errors
    ui.show_results()

    if solver_errors:
        ui.show_errors()
        return
    

def on_save():
    ui.save_file()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Aerospike Nozzle Geometry')
    root.geometry('350x370')
    root.resizable(False, True)

    ui = interface.Interface(root=root, on_solve=on_solve, on_save=on_save, results=None, errors=None)

    root.mainloop()