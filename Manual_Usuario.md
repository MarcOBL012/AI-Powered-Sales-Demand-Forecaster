# Manual de Usuario - Demanda San Fernando

Bienvenido al manual descriptivo del aplicativo **Demanda San Fernando**. Esta herramienta es una aplicación de escritorio diseñada para ejecutarse 100% de manera local (offline), permitiendo a los analistas cargar datos históricos de ventas y generar proyecciones de demanda utilizando modelos de inteligencia artificial avanzados (Prophet).

---

## 1. Características Principales

*   **100% Offline y Seguro:** Los datos nunca salen de tu computadora. Toda la información se procesa y almacena localmente usando una base de datos DuckDB integrada.
*   **Inteligencia Artificial Integrada:** Utiliza algoritmos de predicción de series temporales para encontrar patrones estacionales y tendencias.
*   **Proyección Automática:** Calcula automáticamente el pronóstico de demanda futuro extendiendo la predicción exactamente hasta el **31 de diciembre de 2027**.
*   **Visualización Interactiva:** Ofrece gráficas interactivas con intervalos de confianza (optimista y pesimista) y vistas agregadas mensuales o anuales.
*   **Exportación Sencilla:** Permite exportar los resultados proyectados a un formato compatible con Excel (.csv) con un solo clic.

---

## 2. Preparación de los Datos (Formato CSV)

Para que la aplicación pueda ingerir tus datos correctamente, debes preparar un archivo `.csv`. El sistema lee las columnas estrictamente por su **orden de posición**, no por sus nombres. El orden debe ser exactamente el siguiente:

1.  **Columna 1 (Producto/SKU):** El identificador único del producto (ej: `SKU-100`, `Laptop-X`).
2.  **Columna 2 (Fecha):** La fecha correspondiente a la venta, preferiblemente en formato `YYYY-MM-DD` (ej: `2023-01-01`).
3.  **Columna 3 (Cantidad/Volumen):** El valor numérico de las ventas o la demanda histórica (ej: `150.5`).
4.  **Columna 4 (Tipo/Categoría) - *Opcional*:** Una categoría para el producto (ej: `Electrónica`, `Abarrotes`).

> [!IMPORTANT]
> El modelo de IA requiere un **mínimo de 10 registros históricos** por cada producto para poder generar una proyección matemáticamente válida.

---

## 3. Guía de Uso Paso a Paso

### Paso 1: Iniciar la Aplicación
Haz doble clic en el archivo ejecutable compilado `DemandaSanFernando.exe` (ubicado en tu carpeta `dist`). No requiere instalación previa ni conexión a internet.

### Paso 2: Crear un Espacio de Trabajo
1. En el panel lateral izquierdo, verás la sección "Espacio de trabajo".
2. Si es la primera vez que lo usas, haz clic en el botón **Nuevo espacio de trabajo**.
3. Ingresa un nombre para tu proyecto (por ejemplo: `Ventas 2024`) y acepta.

### Paso 3: Importar Datos
1. Haz clic en el botón **Importar datos CSV** en el panel lateral.
2. Selecciona tu archivo `.csv` previamente preparado.
3. El sistema cargará los datos en la base de datos interna y te mostrará un mensaje de éxito.

### Paso 4: Visualizar el Histórico
1. En la parte superior de la pantalla principal, abre el menú desplegable **Seleccionar producto**.
2. Elige el producto (SKU) que deseas analizar.
3. Se mostrará inmediatamente una gráfica con la curva de volumen de demanda histórica de dicho producto.

### Paso 5: Correr la Proyección de IA
1. Una vez seleccionado un producto, haz clic en el botón azul **Correr proyección**.
2. El botón cambiará su texto a "Entrenando..." mientras la inteligencia artificial procesa la matemática de la serie de tiempo.
3. Al finalizar, la pantalla se actualizará mostrando dos pestañas: **Mensual** y **Anual**.
    *   **Gráfica:** Verás la línea azul (histórico) conectada a una línea naranja (predicción futura), envuelta por un área sombreada que representa el *intervalo de confianza* (valores optimistas y pesimistas).
    *   **Tabla de Datos:** Debajo de la gráfica tendrás el detalle exacto con fechas, proyecciones puntuales y los márgenes de error.

### Paso 6: Exportar Resultados
1. Cuando la proyección termine exitosamente, el botón **Exportar a Excel (CSV)** se activará en la barra superior.
2. Haz clic en él, elige dónde guardar el archivo en tu computadora y ponle un nombre.
3. Podrás abrir este archivo directamente en Microsoft Excel para cruzarlo con otros reportes financieros o logísticos.

---

## 4. Notas Técnicas

*   **Motor de Base de Datos:** `DuckDB`. Se genera un archivo físico `local_forecaster.duckdb` en la carpeta donde ejecutas el software. No elimines este archivo si deseas conservar tus espacios de trabajo y el historial cargado.
*   **Métricas de Error:** El título de la gráfica proyectada incluye el valor **RMSE** (Error Cuadrático Medio). Un RMSE más cercano a 0 indica que el modelo encontró un patrón muy claro y preciso en tus datos históricos.
