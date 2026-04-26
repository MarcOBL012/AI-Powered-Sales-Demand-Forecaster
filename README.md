# 🔮AI-Powered Sales Demand Forecaster (100% Offline) 🚀

**AI-Powered Sales Demand Forecaster** is a desktop application designed for **demand forecasting** using artificial intelligence (predictive time-series models), operating in a **100% offline and secure** environment.

The tool processes historical sales data and automatically projects expected demand, optimizing logistics, procurement, and strategic planning processes.

## 🚀 Key Features

*   🔒 **100% Offline (Local):** All data is stored and processed on your own machine using an embedded **DuckDB** database. There are no external server calls and zero risk of data leaks.
*   🧠 **Artificial Intelligence (Prophet):** Automatic prediction engine that evaluates trends and seasonality to generate a robust forecast.
*   📅 **Dynamic Projection:** The system calculates the necessary periods to project demand consistently until December 2027.
*   📊 **Interactive Visualization:** Tabs for monthly and yearly analysis, with charts that include historical data, projections, and confidence intervals (optimistic and pessimistic).
*   💾 **Export to CSV/Excel:** Easily export the projection tables to cross-reference with other enterprise systems.
*   🪟 **Modern Interface:** Built with `CustomTkinter` to provide a friendly, modern, and responsive dark/light design.



## 🛠️ Technology Stack

*   **Python 3.10+**
*   **CustomTkinter:** Modern graphical user interface.
*   **DuckDB:** Ultra-fast local analytical database.
*   **Prophet / Pandas / Numpy:** Data processing and AI predictive engine.
*   **Matplotlib:** Chart generation embedded in the UI.
*   **PyInstaller:** Compiling the project into a standalone executable (`.exe`).



## 📦 Installation & Execution

### Option 1: Run the compiled version (.exe)
If you have the `DemandaSanFernando.exe` file (typically located in the `dist/` folder), simply **double-click** it. You do not need to have Python installed.

### Option 2: Run from source code
If you want to modify the code or run it directly from Python:

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

### Option 3: Compile the project
If you have made changes and want to generate your own `.exe`:
```bash
python build.py
```
*The final executable will be generated in the `dist/` folder.*



## 📖 Quick Start

1. **Create Workspace:** Go to the side panel and click "Nuevo espacio de trabajo" (New workspace).
2. **Load Data:** Click "Importar datos CSV" (Import CSV data). Make sure the CSV strictly follows this column order (header names do not matter):
   * `SKU` (Product) -> `Date` (YYYY-MM-DD) -> `Volume` (Quantity) -> `Category` (Optional).
3. **Select Product:** Select an SKU from the top menu to view its historical chart.
4. **Forecast:** Click "Correr proyección" (Run forecast). The AI will process the data and display the projected chart.
5. **Export:** Save the results to an Excel file using the top button "Exportar a Excel (CSV)".



## 📋 Project Structure

```text
demand_forecaster_offline/
├── app.py                  # Main UI (CustomTkinter + Matplotlib)
├── build.py                # Build script using PyInstaller
├── requirements.txt        # Project dependencies
├── engine/
│   ├── db_handler.py       # Local data management using DuckDB
│   └── forecaster.py       # Predictive engine powered by Prophet
└── README.md               # Documentation
```

## 📝 License
This project is for internal/private use. Modify it according to your organization's needs.
