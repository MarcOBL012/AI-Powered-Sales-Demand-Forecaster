import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from engine.db_handler import DBHandler
from engine.forecaster import AutoForecaster
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class DemandForecasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Demanda San Fernando")
        self.geometry("1000x700")
        
        self.db = DBHandler("local_forecaster.duckdb")
        self.current_project_id = None
        self.current_sku_id = None
        
        self._build_ui()
        self._load_projects()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Demanda San Fernando", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Workspace
        self.project_label = ctk.CTkLabel(self.sidebar_frame, text="Espacio de trabajo:")
        self.project_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.project_combo = ctk.CTkComboBox(self.sidebar_frame, command=self._on_project_select)
        self.project_combo.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        self.new_proj_btn = ctk.CTkButton(self.sidebar_frame, text="Nuevo espacio de trabajo", command=self._create_workspace)
        self.new_proj_btn.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        # Data Import
        self.import_btn = ctk.CTkButton(self.sidebar_frame, text="Importar datos CSV", command=self._import_csv)
        self.import_btn.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        
        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Top Bar (SKU Selection)
        self.top_bar = ctk.CTkFrame(self.main_frame)
        self.top_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_bar.grid_columnconfigure(1, weight=1)
        
        self.sku_label = ctk.CTkLabel(self.top_bar, text="Seleccionar producto:")
        self.sku_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.sku_combo = ctk.CTkComboBox(self.top_bar, values=[], command=self._on_sku_select)
        self.sku_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.forecast_btn = ctk.CTkButton(self.top_bar, text="Correr proyección", command=self._run_forecast_thread)
        self.forecast_btn.grid(row=0, column=2, padx=10, pady=10)
        
        self.export_btn = ctk.CTkButton(self.top_bar, text="Exportar a Excel (CSV)", command=self._export_forecast, state="disabled")
        self.export_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Chart Area
        self.chart_frame = ctk.CTkFrame(self.main_frame)
        self.chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
    def _load_projects(self):
        df = self.db.get_projects()
        if not df.empty:
            names = df['name'].tolist()
            self.project_combo.configure(values=names)
            self.project_combo.set(names[0])
            self._on_project_select(names[0])
        else:
            self.project_combo.set("Sin proyectos")
            
    def _create_workspace(self):
        dialog = ctk.CTkInputDialog(text="Ingresar nombre del nuevo espacio:", title="Nuevo espacio de trabajo")
        name = dialog.get_input()
        if name:
            self.db.create_project(name)
            self._load_projects()
            self.project_combo.set(name)
            self._on_project_select(name)
            
    def _on_project_select(self, choice):
        df = self.db.get_projects()
        if not df.empty:
            proj = df[df['name'] == choice]
            if not proj.empty:
                self.current_project_id = int(proj['id'].iloc[0])
                self._load_skus()
                
    def _load_skus(self):
        if self.current_project_id is not None:
            df = self.db.get_skus(self.current_project_id)
            if not df.empty:
                codes = df['sku_code'].tolist()
                self.sku_combo.configure(values=codes)
                self.sku_combo.set(codes[0])
                self._on_sku_select(codes[0])
            else:
                self.sku_combo.configure(values=["Sin productos"])
                self.sku_combo.set("Sin productos")
                self.current_sku_id = None
                self._clear_chart()
                
    def _on_sku_select(self, choice):
        if choice == "Sin productos": return
        df = self.db.get_skus(self.current_project_id)
        sku = df[df['sku_code'] == choice]
        if not sku.empty:
            self.current_sku_id = int(sku['id'].iloc[0])
            self._plot_historical()
            
    def _import_csv(self):
        if not self.current_project_id:
            messagebox.showwarning("Warning", "Please create or select a workspace first.")
            return
            
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                # Auto-detect standard columns or fallback to index
                cols = df.columns.tolist()
                sku_col = cols[0]
                date_col = cols[1] if len(cols) > 1 else cols[0]
                vol_col = cols[2] if len(cols) > 2 else cols[0]
                category_col = cols[3] if len(cols) > 3 else None
                
                mapping = {'sku_code': sku_col, 'date': date_col, 'volume': vol_col}
                if category_col:
                    mapping['category'] = category_col
                
                self.db.load_sales_dataframe(self.current_project_id, df, mapping)
                messagebox.showinfo("Success", "Data imported successfully!")
                self._load_skus()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")
                
    def _clear_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
    def _plot_historical(self):
        if not self.current_sku_id: return
        df = self.db.get_sales_data(self.current_sku_id)
        if df.empty: return
        
        df['date'] = pd.to_datetime(df['date'])
        
        self._clear_chart()
        
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(df['date'], df['volume'], marker='o', label='Histórico')
        ax.set_title("Volumen Histórico")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Volumen")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _run_forecast_thread(self):
        if not self.current_sku_id:
            messagebox.showwarning("Warning", "Select a valid SKU first.")
            return
        
        self.forecast_btn.configure(state="disabled", text="Entrenando...")
        threading.Thread(target=self._run_forecast, daemon=True).start()

    def _run_forecast(self):
        df = self.db.get_sales_data(self.current_sku_id)
        if len(df) < 10:
            self.after(0, lambda: messagebox.showerror("Error", "Not enough data points (minimum 10 required)."))
            self.after(0, lambda: self.forecast_btn.configure(state="normal", text="Correr proyección"))
            return
            
        df['date'] = pd.to_datetime(df['date'])
        
        try:
            forecaster = AutoForecaster()
            forecaster.fit_auto(df, target_col='volume', date_col='date')
            
            # Calculate steps to reach 2027-12-31
            last_date = df['date'].max()
            target_date = pd.to_datetime('2027-12-31')
            
            steps = (target_date.year - last_date.year) * 12 + (target_date.month - last_date.month)
            if steps <= 0:
                steps = 12
                
            forecast_df = forecaster.predict(steps=steps)
            
            # Update UI on main thread
            self.after(0, lambda: self._plot_forecast(df, forecast_df, forecaster.metrics['rmse']))
            self.after(0, lambda: self.forecast_btn.configure(state="normal", text="Correr proyección"))
            
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Forecast failed: {e}"))
            self.after(0, lambda: self.forecast_btn.configure(state="normal", text="Correr proyección"))

    def _plot_forecast(self, df, forecast_df, rmse):
        self._clear_chart()
        
        self.last_forecast_df = forecast_df
        self.export_btn.configure(state="normal")
        
        tabview = ctk.CTkTabview(self.chart_frame)
        tabview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tab_month = tabview.add("Mensual")
        tab_year = tabview.add("Anual")
        
        self._build_forecast_tab(tab_month, df, forecast_df, rmse, time_col_hist='date', time_col_fcst='Date', freq='M')
        
        # Prepare yearly data
        df_yearly = df.copy()
        df_yearly['year'] = pd.to_datetime(df_yearly['date']).dt.year
        df_hist_yearly = df_yearly.groupby('year').agg({'volume': 'sum'}).reset_index()
        
        forecast_df_yearly = forecast_df.copy()
        forecast_df_yearly['Year'] = pd.to_datetime(forecast_df_yearly['Date']).dt.year
        yearly_fcst = forecast_df_yearly.groupby('Year').agg({
            'Forecast': 'sum',
            'Optimistic': 'sum',
            'Pessimistic': 'sum'
        }).reset_index()
        
        self._build_forecast_tab(tab_year, df_hist_yearly, yearly_fcst, rmse, time_col_hist='year', time_col_fcst='Year', freq='Y')

    def _build_forecast_tab(self, parent, hist_df, fcst_df, rmse, time_col_hist, time_col_fcst, freq):
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Historical
        ax.plot(hist_df[time_col_hist], hist_df['volume'], marker='o', label='Histórico', color='blue')
        
        # Forecast
        ax.plot(fcst_df[time_col_fcst], fcst_df['Forecast'], marker='x', label='Proyección', color='orange')
        ax.fill_between(fcst_df[time_col_fcst], fcst_df['Pessimistic'], fcst_df['Optimistic'], color='orange', alpha=0.2, label='Intervalo de Confianza')
        
        if freq == 'M':
            ax.set_title(f"Proyección de Demanda (RMSE: {rmse:.2f})")
        else:
            ax.set_title("Proyección Anual Agregada")
            
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Volumen")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add table for forecast projections
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        columns = ("Fecha", "Proyección", "Optimista", "Pesimista")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
            
        for index, row in fcst_df.iterrows():
            if freq == 'M':
                time_str = row[time_col_fcst].strftime('%Y-%m-%d') if hasattr(row[time_col_fcst], 'strftime') else str(row[time_col_fcst])
            else:
                time_str = str(row[time_col_fcst])
                
            forecast_val = f"{row['Forecast']:.2f}"
            opt_val = f"{row['Optimistic']:.2f}"
            pess_val = f"{row['Pessimistic']:.2f}"
            tree.insert("", "end", values=(time_str, forecast_val, opt_val, pess_val))
            
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _export_forecast(self):
        if not hasattr(self, 'last_forecast_df') or self.last_forecast_df is None:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Excel / CSV", "*.csv")],
            title="Exportar Proyección"
        )
        if file_path:
            try:
                export_df = self.last_forecast_df.copy()
                export_df.rename(columns={
                    'Date': 'Fecha', 
                    'Forecast': 'Proyección', 
                    'Pessimistic': 'Pesimista', 
                    'Optimistic': 'Optimista'
                }, inplace=True)
                export_df.to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", "La proyección se ha exportado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al exportar: {e}")

if __name__ == "__main__":
    app = DemandForecasterApp()
    app.mainloop()
