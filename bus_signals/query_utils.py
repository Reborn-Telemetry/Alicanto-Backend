import psycopg2

dbname = 'alicanto-db-dev'
user = 'postgres'
password = 'postgres'
host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
port = '5432'

def daily_bus_km(id_bus):
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = connection.cursor()
    query = """WITH all_days AS (
    SELECT generate_series(1, 31) AS dia
)
SELECT
    all_days.dia,
    LAST_VALUE(CASE WHEN mes = 1 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS enero,
    LAST_VALUE(CASE WHEN mes = 2 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS febrero,
    LAST_VALUE(CASE WHEN mes = 3 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS marzo,
    LAST_VALUE(CASE WHEN mes = 4 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS abril,
    LAST_VALUE(CASE WHEN mes = 5 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS mayo,
    LAST_VALUE(CASE WHEN mes = 6 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS junio,
    LAST_VALUE(CASE WHEN mes = 7 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS julio,
    LAST_VALUE(CASE WHEN mes = 8 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS agosto,
    LAST_VALUE(CASE WHEN mes = 9 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS septiembre,
    LAST_VALUE(CASE WHEN mes = 10 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS octubre,
    LAST_VALUE(CASE WHEN mes = 11 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS noviembre,
    LAST_VALUE(CASE WHEN mes = 12 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS diciembre
FROM
    all_days

LEFT JOIN (
    SELECT
        EXTRACT(DAY FROM "TimeStamp") AS dia,
        bus_id,
        odometer_value as max_odometer,
        EXTRACT(MONTH FROM "TimeStamp") AS mes
    FROM
       (
            WITH ranked_data AS (
                SELECT
                    bus_id,
                    odometer_value,
                    "TimeStamp",
                    ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('day', "TimeStamp") ORDER BY odometer_value DESC) AS rnk
                FROM
                    bus_signals_odometer
            )
            SELECT
                bus_id,
                odometer_value,
                "TimeStamp"
            FROM
                ranked_data
            WHERE
                rnk = 1
            ORDER BY
                bus_id, "TimeStamp" DESC
        ) A WHERE bus_id =%s
) A ON all_days.dia = A.dia;"""
    cursor.execute(query, (id_bus,))
    results = cursor.fetchall()
# Cerrar el cursor y la conexión
    cursor.close()
    connection.close()
    return results

    
  





