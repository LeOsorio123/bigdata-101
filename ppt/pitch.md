# Pitch / Guión de clase — De Data Lakes a Lakehouse

## Slide 1 — Portada (30 seg)
> Hoy vamos a hablar de cómo han evolucionado las arquitecturas de datos, desde los Data Warehouses tradicionales hasta lo que hoy conocemos como Data Lakehouse, y vamos a entender el patrón Medallion que organiza los datos en capas Bronze, Silver y Gold. Además vamos a ver cómo gobernar todo esto con Unity Catalog.

## Slide 2 — Agenda (1 min)
> Vamos a recorrer 7 bloques. Primero entendemos de dónde venimos con los warehouses, luego la promesa de los data lakes, por qué muchos fracasaron, cómo el lakehouse resuelve eso, la arquitectura Medallion, gobierno de datos con Unity Catalog, y cerramos con la evolución histórica.

## Slide 3 — Capítulo 01: Data Warehouse (30 seg)
> Empecemos por el principio. Los Data Warehouses llevan décadas con nosotros.

## Slide 4 — Data Warehouse: ¿Qué es? (2 min)
> Un warehouse es un repositorio centralizado donde los datos llegan ya limpios y transformados. Schema-on-Write. Excelente para BI y reportes con SQL. Piensen en Teradata, Oracle, Redshift.

## Slide 5 — Data Warehouse: Limitaciones (2 min)
> Pero tiene limitaciones importantes: solo datos estructurados. Si quieren meter logs, JSON anidado, imágenes... no se puede. Además es caro y el ETL es rígido. Los científicos de datos necesitan datos crudos y el warehouse no se los da.
>
> **Pregunta**: ¿Alguien ha trabajado con un warehouse? ¿Qué herramienta usaron?

## Slide 6 — Capítulo 02: Data Lake (30 seg)
> Ante esas limitaciones, a mediados de los 2000 nace el Data Lake. La idea: guardemos todo, en cualquier formato, y ya después vemos.

## Slide 7 — Data Lake: ¿Qué es? (2 min)
> El Data Lake almacena datos en formato crudo. Schema-on-Read. Pueden meter CSV, JSON, Parquet, imágenes, audio, logs... todo cabe. Y el almacenamiento es barato: S3 cuesta centavos por gigabyte. Fue la base que permitió que el ML a escala fuera viable.

## Slide 8 — Data Lake: Tecnologías (2 min)
> Las tecnologías clave: Hadoop fue el pionero, Spark para procesamiento, Parquet y ORC como formatos columnares. En la nube: S3, ADLS, GCS. Para consultas: Athena, Presto, Spark SQL.

## Slide 9 — Capítulo 03: Data Swamp (30 seg)
> Pero la realidad fue menos bonita. Muchas organizaciones descubrieron que su lago se había convertido en un pantano.

## Slide 10 — Data Swamp: Problemas (2 min)
> ¿Qué pasó? Nadie gobernaba el lago. Datos sin documentar, duplicados, inconsistentes. Y algo crítico: no hay transacciones ACID. Si un job falla a mitad de escritura, quedan datos corruptos. No hay rollback.
>
> **Analogía**: biblioteca sin catálogo donde cualquiera deja libros en cualquier estante.

## Slide 11 — Data Swamp: Consecuencias (2 min)
> Los analistas dejaron de confiar en el lake. Las empresas terminaron copiando datos del lake a un warehouse — lo peor de ambos mundos. Doble costo, doble complejidad.

## Slide 12 — Capítulo 04: Data Lakehouse (30 seg)
> Entonces la industria se preguntó: ¿podemos tener lo mejor del warehouse sobre la infraestructura barata del lake? La respuesta es el Lakehouse.

## Slide 13 — Lakehouse: La convergencia (3 min)
> Veamos la comparación. Antes: warehouse para BI (confiable pero caro) y lake para data science (barato pero caótico). El Lakehouse unifica ambos: ACID sobre el lake, schema enforcement, SQL + ML + Streaming en un solo lugar, almacenamiento abierto.
>
> 📓 **Vamos al notebook `01-concepts/01_warehouse_vs_lake.py`** — ahí van a ver la diferencia entre Schema-on-Write, Schema-on-Read y cómo Delta Lake combina ambos.

## Slide 14 — Lakehouse: ¿Cómo funciona? (3 min)
> Agrega una capa de metadatos transaccional sobre Parquet. Transaction log para rollback automático. Time travel para consultar datos históricos. Schema enforcement para rechazar datos inválidos. El Lakehouse NO es un producto — es un patrón arquitectónico.

## Slide 15 — Formatos de tabla abiertos (3 min)
> Tres formatos hacen posible el Lakehouse: Delta Lake de Databricks (ACID, time travel), Apache Iceberg de Netflix (partitioning oculto, snapshots), y Apache Hudi de Uber (upserts, CDC incremental). Los tres son open source, sobre Parquet, compatibles con Spark/Flink/Trino.
>
> 📓 **Vamos al notebook `03-delta-lake/01_delta_features.py`** — ahí van a experimentar con ACID, Time Travel, Schema Evolution y MERGE en vivo.

## Slide 16 — Plataformas Lakehouse (2 min)
> Databricks es el líder. AWS con Lake Formation, Azure con Synapse, Google con BigLake, Snowflake con Iceberg Tables. Nosotros vamos a trabajar con Databricks + Azure Data Lake Storage Gen2.

## Slide 17 — Capítulo 05: Arquitectura Medallion (30 seg)
> Ahora que tenemos el Lakehouse como plataforma, necesitamos un patrón para organizar los datos dentro. Ese patrón es Medallion.

## Slide 18 — El mundo ANTES de Medallion (2 min)
> Tenemos Delta Lake, ACID, time travel... genial. Pero ¿cómo organizamos los datos dentro del lake? Sin un estándar, cada equipo hacía lo que quería: `/datos/ventas_v2_final_FINAL.parquet`, carpetas sin documentar, nadie sabe qué está limpio y qué no.
>
> Si un pipeline falla, ¿de dónde reprocesas? No hay separación entre datos crudos y datos listos para consumo. Los analistas no saben si pueden confiar en una tabla o no. Básicamente, el mismo caos del Data Swamp pero ahora con ACID — datos consistentemente desordenados.

## Slide 19 — ¿Qué es Medallion? (2 min)
> Es un patrón de diseño popularizado por Databricks que hoy es estándar de la industria. La idea: los datos pasan por capas de calidad creciente, como medallas olímpicas. Bronze = materia prima. Silver = producto en proceso. Gold = producto terminado.
>
> **Analogía**: piensen en una fábrica. Bronze es el almacén donde llega la materia prima tal cual. Silver es la línea de control de calidad y ensamblaje. Gold es la vitrina con el producto listo para el cliente.

## Slide 20 — ¿Qué resuelve Medallion? (2 min)
> Cinco cosas concretas: organización clara (cada dato tiene un lugar), reprocesamiento (si Gold falla, volvés a Bronze), confianza (Gold está validado, punto), separación de responsabilidades (ingenieros en Bronze/Silver, analistas en Gold), y linaje trazable (Bronze → Silver → Gold = origen claro).

## Slide 21 — Bronze: Capa de ingesta (2 min)
> Las fuentes pueden llegar en cualquier formato: CSV, JSON, XML, desde una API, una base de datos por JDBC... lo que sea. Lo que hacemos en Bronze es leer esos datos en su formato original y escribirlos en Delta. No transformamos el contenido — solo cambiamos el formato de almacenamiento para tener ACID y time travel.
>
> Un tip importante: en Bronze leemos todo como STRING. ¿Por qué? Porque si un campo que debería ser número viene con un texto raro, no queremos perder ese registro. La validación de tipos es trabajo de Silver, no de Bronze. Bronze es append-only e inmutable — nunca borramos ni sobrescribimos. Es la fuente de verdad histórica.
>
> 📓 **Vamos al notebook `02-medallion/01_bronze_ingestion.py`** — van a ingestar los CSVs de Uber desde su ADLS Gen2 a una tabla Delta Bronze. Fíjense cómo leemos todo como STRING y agregamos metadatos de ingesta.

## Slide 22 — Silver: Capa de limpieza (2 min)
> Deduplicación, validación de tipos, filtrado, joins entre fuentes. Schema enforcement. Los datos de Silver son confiables para análisis y data science.
>
> 📓 **Vamos al notebook `02-medallion/02_silver_cleaning.py`** — van a limpiar los datos de Bronze: renombrar columnas, castear tipos, extraer la ciudad del nombre del archivo, filtrar registros inválidos y deduplicar.

## Slide 23 — Gold: Capa de negocio (2 min)
> Agregaciones, KPIs, star schema, feature stores para ML. Optimizado para dashboards de BI. Se consume vía SQL o APIs.
>
> 📓 **Vamos al notebook `02-medallion/03_gold_aggregations.py`** — van a crear dos tablas Gold: métricas por ciudad y ranking de las rutas más lentas. Estas tablas están listas para conectar con Power BI.
>
> **Pregunta**: si un dashboard muestra datos incorrectos, ¿en qué capa buscarían el problema primero?

## Slide 24 — Medallion: Comparación (1 min)
> Tabla rápida comparando Bronze, Silver y Gold en calidad, esquema, usuarios, formato y ejemplos.

## Slide 25 — Beneficios (2 min)
> Para el equipo: organización clara, reprocesamiento fácil, linaje trazable. Para el negocio: datos confiables, menor time-to-insight, un solo sistema para BI + ML, costos reducidos.

## Slide 26 — Limitaciones y críticas de Medallion (2 min)
> Medallion no es perfecto. Tres copias del dato (Bronze + Silver + Gold) multiplican el costo de storage. El flujo secuencial agrega latencia — complicado para real-time. Silver requiere mucha ingeniería. Y el negocio solo aparece en Gold — los consumidores deben esperar.
>
> Esto no significa que Medallion sea malo — significa que hay que conocer sus trade-offs.

## Slide 27 — Más allá de Medallion (3 min)
> Data Mesh no reemplaza Medallion — opera a otro nivel. Medallion organiza datos dentro de un pipeline; Data Mesh organiza la propiedad entre dominios. Pueden coexistir: cada dominio tiene su propio Bronze/Silver/Gold.
>
> Data Vault es una técnica de modelado para Silver cuando necesitan auditoría histórica fuerte. Data Fabric es más un concepto de conectividad con AI. Y algunos equipos agregan una capa Platinum encima de Gold para real-time y feature stores de ML.

## Slide 28 — ¿Cuándo usar qué? (2 min)
> La mayoría de empresas medianas arrancan con Medallion — es el punto de partida recomendado. Si la organización es grande con múltiples dominios, combinan Data Mesh + Medallion. Si hay regulación fuerte, Data Vault dentro de Silver. Si todo es real-time (IoT, fraude), Kappa architecture. En la práctica, la mayoría combina patrones según la necesidad. No hay una arquitectura que "supere" a todas las demás.
>
> **Pregunta**: ¿en qué caso de uso de su trabajo o proyecto creen que Medallion no sería suficiente?

## Slide 29 — Capítulo 06: Catálogo y Gobierno de Datos (30 seg)
> Tenemos los datos organizados en Medallion, pero falta una pieza clave: ¿quién puede acceder a qué? ¿cómo rastreamos el origen de cada dato? Ahí entra Unity Catalog.

## Slide 30 — El mundo ANTES de Unity Catalog (2 min)
> Antes de Unity Catalog, Databricks usaba Hive Metastore. Cada workspace tenía su propio catálogo aislado. Si el equipo de ingeniería creaba una tabla en su workspace, el equipo de analytics no la podía ver. Para compartir datos había que copiar archivos o dar acceso directo al storage — un desastre de seguridad.
>
> Los permisos se manejaban a nivel de storage (S3, ADLS), no a nivel de tabla. No había GRANT/REVOKE. No había linaje. No había auditoría. Y el namespace era de solo 2 niveles: `schema.tabla`, sin forma de separar dominios o ambientes.
>
> Básicamente, los mismos problemas del Data Swamp pero ahora dentro de Databricks.

## Slide 31 — ¿Qué es Unity Catalog? (3 min)
> Unity Catalog es la capa de gobernanza centralizada de Databricks. Lanzado en 2022, open source desde 2024. La idea clave: UN solo metastore compartido por todos los workspaces de la región. Se acabaron los silos.
>
> Gobierna no solo tablas, sino todos los activos: vistas, volúmenes (archivos), modelos de ML, funciones. Y usa un namespace de 3 niveles: `catálogo.esquema.tabla`. Ese nivel extra es lo que permite separar dominios de negocio, ambientes dev/prod, o proyectos.
>
> **Analogía**: Hive Metastore era como tener una biblioteca por piso del edificio, cada una con su propio catálogo. Unity Catalog es UNA biblioteca central con un catálogo unificado donde todos pueden buscar, pero con acceso controlado por sección.

## Slide 32 — ¿Qué resuelve Unity Catalog? (2 min)
> Resuelve 4 problemas concretos: descubrimiento (¿existe una tabla de clientes?), control de acceso (GRANT/REVOKE con SQL estándar), linaje automático (de dónde viene cada dato sin escribir código), y auditoría completa (quién accedió a qué y cuándo, para compliance).

## Slide 33 — Control de acceso en Medallion (2 min)
> Acá es donde Medallion y Unity Catalog se complementan perfecto. Cada capa tiene permisos diferenciados: ingenieros acceden a todo, científicos de datos a Silver y Gold, analistas solo a Gold, ejecutivos solo ven dashboards. Los permisos se definen con SQL estándar y viajan con los datos — no dependen del workspace.

## Slide 34 — Linaje, tags y auditoría (2 min)
> El linaje es automático: Databricks rastrea cada transformación sin que escriban código. Si un dashboard muestra datos raros, siguen el linaje hasta Bronze. Los tags permiten clasificar columnas sensibles (PII, confidencial) y aplicar políticas automáticas. Y la auditoría registra cada operación — esencial para GDPR, Habeas Data, o simplemente para saber quién tocó qué.

## Slide 35 — Estructura recomendada (1 min)
> La estructura que van a usar: catálogo `medallion`, esquemas `bronze`, `silver`, `gold`. Volúmenes para archivos no tabulares. Cada capa con permisos por rol. Esto es lo que van a ver en su workspace de Databricks.

## Slide 36 — Evolución histórica (2 min)
> 1990s: warehouses. 2006: Hadoop y el data lake. 2010s: cloud + Spark. 2020+: Lakehouse con Delta/Iceberg/Hudi. Cada generación aprende de los errores de la anterior.

## Slide 37 — Resumen (1 min)
> El Lakehouse no es magia — es almacenamiento barato + formatos abiertos + metadatos transaccionales + gobernanza. Y Medallion es el patrón que le da orden al caos.

## Slide 38 — Cierre
> ¿Preguntas?

---

## Notebooks y cuándo usarlos

| Momento en la clase | Notebook |
|---|---|
| Después de slide 15 (Lakehouse convergencia) | `01-concepts/01_warehouse_vs_lake.py` |
| Después de slide 17 (Formatos de tabla) | `03-delta-lake/01_delta_features.py` |
| Después de slide 21 (Bronze) | `02-medallion/01_bronze_ingestion.py` |
| Después de slide 22 (Silver) | `02-medallion/02_silver_cleaning.py` |
| Después de slide 23 (Gold) | `02-medallion/03_gold_aggregations.py` |

---
**Tiempo total estimado: ~60-70 minutos** (incluyendo demos en notebooks)
