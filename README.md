# Real-Time E-commerce Analytics (PostgreSQL + ClickHouse)

Este proyecto implementa un flujo completo de captura de datos de cambio (CDC) en tiempo real para una tienda de e-commerce simulada. Utiliza PostgreSQL como base de datos transaccional (OLTP) y el motor `MaterializedPostgreSQL` de ClickHouse para ingesta analítica en tiempo real (OLAP), finalizando con un dashboard interactivo en Streamlit.

## Requisitos Previos

Para ejecutar este proyecto en cualquier computadora, solo necesitas tener instalados:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)

No necesitas instalar Python, PostgreSQL ni ClickHouse localmente, ya que todo está 100% contenerizado.

## Pasos para Desplegar

1. **Clonar el repositorio**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd real-time-analytics
   ```

2. **Levantar los servicios con Docker Compose**
   Ejecuta el siguiente comando en la raíz del proyecto (donde está el archivo `docker-compose.yml`):
   ```bash
   docker compose up -d --build
   ```
   *Esto descargará las imágenes necesarias, inicializará las bases de datos, creará el generador de tráfico y levantará el dashboard.*

3. **Verificar el funcionamiento**
   Asegúrate de que los 4 contenedores estén corriendo correctamente:
   ```bash
   docker compose ps
   ```
   Deberías ver los servicios `postgres`, `clickhouse`, `generator` y `dashboard` en estado "Up".

4. **Acceder al Dashboard**
   Abre tu navegador web y visita:
   👉 **http://localhost:8501**

   Podrás ver las gráficas de ingresos y órdenes actualizándose en tiempo real.

## Arquitectura

- **Generator (`generator/`):** Script en Python que inserta y actualiza miles de órdenes aleatorias en PostgreSQL de manera continua.
- **PostgreSQL (`postgres/`):** Base de datos configurada con `wal_level = logical` y `REPLICA IDENTITY DEFAULT` en sus tablas para registrar cada mínimo cambio.
- **ClickHouse (`clickhouse/`):** Base de datos analítica columnar. Se conecta al Logical Replication de PostgreSQL y clona cada cambio en tablas `ReplacingMergeTree` en milisegundos.
- **Dashboard (`dashboard/`):** App en Streamlit que consulta las tablas de ClickHouse utilizando filtros `FINAL` para deduplicar los registros actualizados en tiempo real.

## Detener el entorno

Para detener todos los contenedores y limpiar los recursos, ejecuta:
```bash
docker compose down
```

*Si quieres también borrar la persistencia (eliminar los datos guardados en las bases de datos para empezar desde cero), agrega el flag `-v`:*
```bash
docker compose down -v
```
