import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font


class Interface:
    def __init__(self, root: tk, results: dict, errors: list[str], on_solve: callable, on_save: callable):
        self.root = root
        self.on_solve = on_solve
        self.on_save = on_save
        self.results = results
        self.errors = errors
        self.build_interface()


    # Getter function for the values
    def get_inputs_on_solve(self) -> dict:
        aerospike_type = None

        if self.sizing_var.get():
            if self.linear_var.get():
                aerospike_type = "linear"
            elif self.toroidal_var.get():
                aerospike_type = "toroidal"

        mass_flow_val, mass_flow_unit = (None, None)
        radius_val, radius_unit = (None, None)
        width_val, width_unit = (None, None)
        length_val, length_unit = (None, None)

        if aerospike_type == "linear":
            mass_flow_val, mass_flow_unit = self._get_field_value("linear_massflow")
            length_val, length_unit       = self._get_field_value("linear_length")
            width_val, width_unit         = self._get_field_value("linear_width")

        elif aerospike_type == "toroidal":
            if self.toroidal_choice.get() == "massflow" and self.toroidal_massflow_entry.get():
                mass_flow_val, mass_flow_unit = float(self.toroidal_massflow_entry.get()), self.toroidal_massflow_unit.get()
            elif self.toroidal_choice.get() == "radius" and self.toroidal_radius_entry.get():
                radius_val, radius_unit = float(self.toroidal_radius_entry.get()), self.toroidal_radius_unit.get()

        return {
            "oxidizer": self.input_oxidizer.get()    if self.input_oxidizer.get() else None,
            "fuel":     self.input_fuel.get()        if self.input_fuel.get() else None,
            "Pc":       float(self.input_Pc.get())   if self.input_Pc.get() else None,
            "unit_Pc":  self.unit_Pc.get()           if self.unit_Pc.get() else None,
            "MR":       float(self.input_MR.get())   if self.input_MR.get() else None,
            "eps":      float(self.input_eps.get())  if self.input_eps.get() else None,

            "effective_throat_eps": float(self.input_effective_throat_eps.get())  if self.input_effective_throat_eps.get() else None,
            "truncate_percent":     float(self.input_truncate_percentage.get())   if self.input_truncate_percentage.get() else None,
            "aerospike_resolution": int(self.input_aerospike_resolution.get())    if self.input_aerospike_resolution.get() else None,

            "sizing": self.sizing_var.get(),
            "aerospike_type": aerospike_type,

            "mfr":            mass_flow_val,
            "unit_mfr":       mass_flow_unit,
            "radius":         radius_val,
            "unit_radius":    radius_unit,
            "width":          width_val,
            "unit_width":     width_unit,
            "length":         length_val,
            "unit_length":    length_unit,
        }


    def on_sizing_toggle(self):
        state = 'normal' if self.sizing_var.get() else 'disabled'
        self.linear_check.configure(state=state)
        self.toroidal_check.configure(state=state)

        if not self.sizing_var.get():
            self.linear_var.set(False)
            self.toroidal_var.set(False)

        self.on_linear_toggle()
        self.on_toroidal_toggle()


    def on_linear_toggle(self):
        if self.linear_var.get() and self.sizing_var.get():
            self.toroidal_var.set(False)
            self._set_toroidal_fields_state('disabled')
            self.toroidal_choice.set("massflow")

        linear_on = self.linear_var.get() and self.sizing_var.get()
        state = 'normal' if linear_on else 'disabled'

        for key in ("linear_massflow", "linear_length", "linear_width"):
            getattr(self, f"{key}_chk").configure(state=state)

        self.on_sizing_field_toggle(None, group=("linear_massflow", "linear_length", "linear_width"), max_checked=2)

        # Grey out the Toroidal checkbutton itself while Linear is active (exclusivity)
        self.toroidal_check.configure(
            state='disabled' if linear_on else ('normal' if self.sizing_var.get() else 'disabled')
        )

    def on_toroidal_toggle(self):
        if self.toroidal_var.get() and self.sizing_var.get():
            self.linear_var.set(False)
            self._set_linear_fields_state('disabled')
            self.linear_massflow_var.set(False)
            self.linear_length_var.set(False)
            self.linear_width_var.set(False)

        toroidal_on = self.toroidal_var.get() and self.sizing_var.get()
        state = 'normal' if toroidal_on else 'disabled'

        # -- radio buttons toggle together, not per-field like the checkbutton group
        self.toroidal_massflow_radio.configure(state=state)
        self.toroidal_radius_radio.configure(state=state)
        self.on_toroidal_choice_change()

        # Grey out the Linear checkbutton itself while Toroidal is active (exclusivity)
        self.linear_check.configure(
            state='disabled' if toroidal_on else ('normal' if self.sizing_var.get() else 'disabled')
        )

    def on_toroidal_choice_change(self):
        toroidal_on = self.toroidal_var.get() and self.sizing_var.get()
        if not toroidal_on:
            self.toroidal_massflow_entry.configure(state='disabled')
            self.toroidal_massflow_unit.configure(state='disabled')
            self.toroidal_radius_entry.configure(state='disabled')
            self.toroidal_radius_unit.configure(state='disabled')
            return

        if self.toroidal_choice.get() == "massflow":
            self.toroidal_massflow_entry.configure(state='normal')
            self.toroidal_massflow_unit.configure(state='readonly')
            self.toroidal_radius_entry.configure(state='disabled')
            self.toroidal_radius_unit.configure(state='disabled')
            self.toroidal_radius_entry.delete(0, tk.END)
        else:
            self.toroidal_radius_entry.configure(state='normal')
            self.toroidal_radius_unit.configure(state='readonly')
            self.toroidal_massflow_entry.configure(state='disabled')
            self.toroidal_massflow_unit.configure(state='disabled')
            self.toroidal_massflow_entry.delete(0, tk.END)

    def on_sizing_field_toggle(self, changed_key, group=None, max_checked=None):
        """
        Generic handler for entry/unit enable-disable and max-selection enforcement
        within a field group. -- Only used by Linear's pick-2-of-3 now; Toroidal uses
        on_toroidal_choice_change() instead since it's radio-based.
        """
        if group is None:
            if changed_key and changed_key.startswith("linear_"):
                group, max_checked = ("linear_massflow", "linear_length", "linear_width"), 2
            else:
                return

        vars_ = {k: getattr(self, f"{k}_var") for k in group}
        checked = [k for k in group if vars_[k].get()]

        # enforce max_checked: if the user exceeded it, undo the older ones
        if len(checked) > max_checked and changed_key is not None:
            for k in list(checked):
                if k != changed_key and len(checked) > max_checked:
                    vars_[k].set(False)
                    checked.remove(k)

        parent_on = self._group_parent_on(group)

        for k in group:
            entry = getattr(self, f"{k}_entry")
            unit = getattr(self, f"{k}_unit")
            if parent_on and vars_[k].get():
                entry.configure(state='normal')
                unit.configure(state='readonly')
            else:
                entry.configure(state='disabled')
                unit.configure(state='disabled')
                entry.delete(0, tk.END)

        # once max_checked is reached, disable the remaining unchecked boxes
        if parent_on:
            n_checked = sum(v.get() for v in vars_.values())
            for k in group:
                chk = getattr(self, f"{k}_chk")
                if vars_[k].get():
                    chk.configure(state='normal')
                else:
                    chk.configure(state='disabled' if n_checked >= max_checked else 'normal')

    def _group_parent_on(self, group):
        if group[0].startswith("linear_"):
            return self.linear_var.get() and self.sizing_var.get()
        return self.toroidal_var.get() and self.sizing_var.get()

    def _set_linear_fields_state(self, state):
        for key in ("linear_massflow", "linear_length", "linear_width"):
            getattr(self, f"{key}_chk").configure(state=state)
            getattr(self, f"{key}_entry").configure(state='disabled')
            getattr(self, f"{key}_unit").configure(state='disabled')

    def _set_toroidal_fields_state(self, state):
        self.toroidal_massflow_radio.configure(state=state)
        self.toroidal_radius_radio.configure(state=state)
        self.toroidal_massflow_entry.configure(state='disabled')
        self.toroidal_massflow_unit.configure(state='disabled')
        self.toroidal_radius_entry.configure(state='disabled')
        self.toroidal_radius_unit.configure(state='disabled')

    def _get_field_value(self, key):
        entry = getattr(self, f"{key}_entry")
        var = getattr(self, f"{key}_var")
        unit = getattr(self, f"{key}_unit")

        if var.get() and entry.get():
            return float(entry.get()), unit.get()
        
        return None, None
    

    # Builder functions
    def build_interface(self):
        SECTION_FONT   = font.Font(family="Arial", size=10, weight="bold")

        OXIDIZER_ITEMS = ["LOX", "GOX", "N2O4", "N2O", "IRFNA", "H2O2", "Peroxide90", "Peroxide98", "MON3", "MON15", "MON25"]
        FUEL_ITEMS = ["RP1", "LH2", "CH4", "MMH", "N2H4", "UDMH", "A50", "Ethanol", "Methanol", "GH2", "GCH4", "JetA", "JP10"]

        PAD_LABEL = dict(padx=(10, 4), pady=3, sticky='W')
        PAD_INPUT = dict(padx=(0, 10), pady=3, sticky='W')

        # =========================================================
        # Engine Definition
        # =========================================================
        ttk.Label(self.root, text="Engine Definition", font=SECTION_FONT).grid(
            column=0, row=0, columnspan=2, padx=10, pady=(10, 5), sticky='W'
        )

        # Oxidizer
        ttk.Label(self.root, text='Oxidizer:').grid(column=0, row=1, **PAD_LABEL)
        self.input_oxidizer = ttk.Combobox(self.root, values=OXIDIZER_ITEMS, width=15, state='readonly')
        self.input_oxidizer.grid(column=1, row=1, **PAD_INPUT)

        # Fuel
        ttk.Label(self.root, text='Fuel:').grid(column=0, row=2, **PAD_LABEL)
        self.input_fuel = ttk.Combobox(self.root, values=FUEL_ITEMS, width=15, state='readonly')
        self.input_fuel.grid(column=1, row=2, **PAD_INPUT)

        # Chamber Pressure
        ttk.Label(self.root, text='Chamber Pressure:').grid(column=0, row=3, **PAD_LABEL)
        pc_row = ttk.Frame(self.root)
        pc_row.grid(column=1, row=3, padx=(0, 10), pady=3, sticky='W')
        self.input_Pc = ttk.Entry(pc_row, width=8)
        self.input_Pc.grid(column=0, row=0, sticky='W')
        
        self.unit_Pc = ttk.Combobox(pc_row, values=["bar", "Pa", "atm", "kPa", "psi", "MPa"], width=5, state='readonly')
        self.unit_Pc.grid(column=1, row=0, padx=(6, 0), sticky='W')
        self.unit_Pc.set("bar")

        # Mixture Ratio
        ttk.Label(self.root, text='Mixture Ratio:').grid(column=0, row=4, **PAD_LABEL)
        self.input_MR = ttk.Entry(self.root, width=18)
        self.input_MR.grid(column=1, row=4, **PAD_INPUT)

        # Design Area Ratio
        ttk.Label(self.root, text='Design Area Ratio:').grid(column=0, row=5, **PAD_LABEL)
        self.input_eps = ttk.Entry(self.root, width=18)
        self.input_eps.grid(column=1, row=5, **PAD_INPUT)

        # =========================================================
        # Aerospike Definition
        # =========================================================
        ttk.Label(self.root, text='Aerospike Definition', font=SECTION_FONT).grid(
            column=0, row=6, columnspan=2, padx=10, pady=(10, 5), sticky='W'
        )

        # Effective Throat Area Ratio
        ttk.Label(self.root, text='Effective Throat Area Ratio:').grid(column=0, row=7, **PAD_LABEL)
        self.input_effective_throat_eps = ttk.Entry(self.root, width=18)
        self.input_effective_throat_eps.grid(column=1, row=7, **PAD_INPUT)

        # Truncation
        ttk.Label(self.root, text='Truncate at (%):').grid(column=0, row=8, **PAD_LABEL)
        self.input_truncate_percentage = ttk.Entry(self.root, width=18)
        self.input_truncate_percentage.grid(column=1, row=8, **PAD_INPUT)

        # Resolution
        ttk.Label(self.root, text='Aerospike Resolution:').grid(column=0, row=9, **PAD_LABEL)
        self.input_aerospike_resolution = ttk.Entry(self.root, width=18)
        self.input_aerospike_resolution.grid(column=1, row=9, **PAD_INPUT)


        # =========================================================
        # Aerospike sizing box 
        # =========================================================
        ttk.Label(self.root, text="Aerospike Sizing Method", font=SECTION_FONT).grid(
            column=2, row=0, padx=8, pady=(6, 4), sticky='W'
        )

        self.sizing_var = tk.BooleanVar(value=False)
        self.sizing_frame = ttk.LabelFrame(self.root)
        self.sizing_frame.grid(column=2, row=1, rowspan=10, columnspan=2, padx=5, pady=1, sticky='W')

        self.sizing_check = ttk.Checkbutton(
            self.sizing_frame, text="Sizing", variable=self.sizing_var,
            command=self.on_sizing_toggle
        )
        self.sizing_frame.configure(labelwidget=self.sizing_check)


        # ---- LINEAR sub-frame ----
        self.linear_var = tk.BooleanVar(value=False)
        self.linear_frame = ttk.LabelFrame(self.sizing_frame)
        self.linear_frame.grid(column=0, row=1, padx=8, pady=(4, 4), sticky='WE')

        self.linear_check = ttk.Checkbutton(
            self.linear_frame, text="Linear", variable=self.linear_var,
            command=self.on_linear_toggle
        )
        self.linear_frame.configure(labelwidget=self.linear_check)

        self.linear_massflow_var = tk.BooleanVar(value=False)
        self.linear_length_var   = tk.BooleanVar(value=False)
        self.linear_width_var    = tk.BooleanVar(value=False)

        self._build_sizing_row(self.linear_frame, 0, "Mass Flow:", "linear_massflow", units=["kg/s", "lb/s"])
        self._build_sizing_row(self.linear_frame, 1, "Length:", "linear_length", units=["m", "cm", "mm", "in", "ft"])
        self._build_sizing_row(self.linear_frame, 2, "Width:", "linear_width", units=["m", "cm", "mm", "in", "ft"])


        # ---- TOROIDAL sub-frame -- radio choice between Mass Flow / Cowl Radius ----
        self.toroidal_var = tk.BooleanVar(value=False)
        self.toroidal_frame = ttk.LabelFrame(self.sizing_frame)
        self.toroidal_frame.grid(column=0, row=2, padx=8, pady=(4, 6), sticky='WE')

        self.toroidal_check = ttk.Checkbutton(
            self.toroidal_frame, text="Toroidal", variable=self.toroidal_var,
            command=self.on_toroidal_toggle
        )
        self.toroidal_frame.configure(labelwidget=self.toroidal_check)

        self.toroidal_choice = tk.StringVar(value="massflow")

        self.toroidal_massflow_radio = ttk.Radiobutton(
            self.toroidal_frame, text="Mass Flow:", value="massflow",
            variable=self.toroidal_choice, command=self.on_toroidal_choice_change
        )
        self.toroidal_massflow_radio.grid(column=0, row=0, padx=(20, 4), pady=2, sticky='W')
        self.toroidal_massflow_entry = ttk.Entry(self.toroidal_frame, width=10, state='disabled')
        self.toroidal_massflow_entry.grid(column=1, row=0, padx=4, pady=2, sticky='W')
        self.toroidal_massflow_unit = ttk.Combobox(self.toroidal_frame, values=["kg/s", "lb/s"], width=5, state='disabled')
        self.toroidal_massflow_unit.set("kg/s")
        self.toroidal_massflow_unit.grid(column=2, row=0, padx=2, pady=2, sticky='W')

        self.toroidal_radius_radio = ttk.Radiobutton(
            self.toroidal_frame, text="Cowl Radius:", value="radius",
            variable=self.toroidal_choice, command=self.on_toroidal_choice_change
        )
        self.toroidal_radius_radio.grid(column=0, row=1, padx=(20, 4), pady=2, sticky='W')
        self.toroidal_radius_entry = ttk.Entry(self.toroidal_frame, width=10, state='disabled')
        self.toroidal_radius_entry.grid(column=1, row=1, padx=4, pady=2, sticky='W')
        self.toroidal_radius_unit = ttk.Combobox(self.toroidal_frame, values=["m", "cm", "mm", "in", "ft"], width=5, state='disabled')
        self.toroidal_radius_unit.set("m")
        self.toroidal_radius_unit.grid(column=2, row=1, padx=2, pady=2, sticky='W')

        self.on_sizing_toggle()


        # =========================================================
        # Buttons
        # =========================================================
        button_row = ttk.Frame(self.root)
        button_row.grid(column=0, row=11, columnspan=2, padx=10, pady=(10, 10), sticky='EW')
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(button_row, text='Run', command=self.on_solve, width=15).grid(column=0, row=0, padx=(0, 5), sticky='W')
        ttk.Button(button_row, text='Save Contour', command=self.on_save, width=15).grid(column=1, row=0, padx=(5, 0), sticky='E')


    def _build_sizing_row(self, parent, row_idx, label_text, key, units):
        var = getattr(self, f"{key}_var")
        chk = ttk.Checkbutton(
            parent, text=label_text, variable=var,
            command=lambda k=key: self.on_sizing_field_toggle(k)
        )
        chk.grid(column=0, row=row_idx, padx=(20, 4), pady=2, sticky='W')

        entry = ttk.Entry(parent, width=10, state='disabled')
        entry.grid(column=1, row=row_idx, padx=4, pady=2, sticky='W')

        unit_box = ttk.Combobox(parent, values=units, width=5, state='disabled')
        unit_box.set(units[0])
        unit_box.grid(column=2, row=row_idx, padx=2, pady=2, sticky='W')

        setattr(self, f"{key}_chk", chk)
        setattr(self, f"{key}_entry", entry)
        setattr(self, f"{key}_unit", unit_box)



    def show_output(self):
        LABEL_FONT  = font.Font(family="Arial", size=9)
        VALUE_FONT  = font.Font(family="Arial", size=9, weight="bold")
        HEADER_FONT = font.Font(family="Arial", size=11, weight="bold")

        win = tk.Toplevel(self.root)
        win.title("Aerospike Results")
        win.resizable(False, False)

        outer = ttk.Frame(win, padding=16)
        outer.grid(column=0, row=0, sticky='NSEW')

        # ---- Header ----
        aerospike_type = self.results.get("aerospike_type")
        type_label = {
            "toroidal":  "Toroidal Aerospike",
            "linear":    "Linear Aerospike",
        }.get(aerospike_type, "Aerospike")

        ttk.Label(outer, text=type_label, font=HEADER_FONT).grid(column=0, row=0, columnspan=2, sticky='W', pady=(0, 10))

        # ---- Field set depends on aerospike_type ----
        if aerospike_type == "linear":
            fields = [
                ("mfr",    "Mass Flow Rate", "kg/s"),
                ("length", "Length",         "m"),
                ("width",  "Width",          "m"),
            ]
        elif aerospike_type == "toroidal":
            fields = [
                ("mfr",    "Mass Flow Rate", "kg/s"),
                ("radius", "Cowl Radius",    "m"),
            ]
        else:
            fields = []

        row = 1
        ttk.Separator(outer, orient='horizontal').grid(column=0, row=row, columnspan=2, sticky='EW', pady=(0, 8))
        row += 1

        if not fields:
            ttk.Label(outer, text="No sizing results available.", font=LABEL_FONT,
                      foreground="gray40").grid(column=0, row=row, columnspan=2, sticky='W')
            row += 1

        else:
            for key, label, unit in fields:
                value = self.results.get(key)
                display_value = "—" if value is None else f"{value:.2g} {unit}"

                ttk.Label(outer, text=f"{label}:", font=LABEL_FONT).grid(column=0, row=row, sticky='W', padx=(0, 24), pady=3)
                ttk.Label(outer, text=display_value, font=VALUE_FONT).grid(column=1, row=row, sticky='E', pady=3)
                row += 1

        # ---- Contour summary, derived only from x / R_x / eps_x ----
        x_vals = [v for v in self.results.get("x", []) if v is not None]

        if x_vals:
            ttk.Separator(outer, orient='horizontal').grid(column=0, row=row, columnspan=2, sticky='EW', pady=(8, 8))
            row += 1

            ttk.Label(outer, text="Contour Summary", font=LABEL_FONT).grid(column=0, row=row, columnspan=2, sticky='W', pady=(0, 4))
            row += 1

            ttk.Label(outer, text="Stations computed:", font=LABEL_FONT).grid(column=0, row=row, sticky='W', padx=(0, 24), pady=2)
            ttk.Label(outer, text=str(len(self.results.get("x", []))), font=VALUE_FONT).grid(column=1, row=row, sticky='E', pady=2)
            row += 1

            if x_vals:
                ttk.Label(outer, text="Axial length:", font=LABEL_FONT).grid(column=0, row=row, sticky='W', padx=(0, 24), pady=2)
                ttk.Label(outer, text=f"{max(x_vals) - min(x_vals):.4g} m", font=VALUE_FONT).grid(column=1, row=row, sticky='E', pady=2)
                row += 1

        # ---- Close button ----
        ttk.Separator(outer, orient='horizontal').grid(column=0, row=row, columnspan=2, sticky='EW', pady=(10, 10))
        row += 1

        ttk.Button(outer, text="Close", command=win.destroy).grid(column=0, row=row, columnspan=2)


    def show_results(self):
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        
        x, y = self.results["x"], self.results["R_x"]

        plt.figure()
        plt.plot(y, x, color='black')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel('R')
        plt.ylabel('x')
        plt.grid()
        plt.show()


    def show_errors(self):
        for error in self.errors:
            messagebox.showerror("Error", error)


    def save_file(self):
        try:
            x, R, eps = self.results["x"], self.results["R_x"], self.results["eps_x"]
        except Exception:
            messagebox.showerror("Error", "You must run the program before attempting to save the results.")
            return

        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("DAT files", "*.dat")])
            if not file_path:
                return
            
            # Write the points
            with open(file_path, 'w') as file:
                for x, y, eps in zip(x, R, eps):
                    file.write(f"{x} {y} {eps}\n")
            
            messagebox.showinfo("File Saved", "File Successfully Saved")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {e}")
            return