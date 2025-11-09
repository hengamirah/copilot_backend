# %%
COMPLEX_GEMINI_MODEL="gemini-2.5-flash"
GEMINI_API_KEY="xxx"

from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat

class CustomVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(
            self, 
            config=config
        )
        GoogleGeminiChat.__init__(
            self, 
            config={
                'api_key': GEMINI_API_KEY, 
                'model_name': COMPLEX_GEMINI_MODEL
            }
        )

    def generate_query_explanation(self, sql: str):
        my_prompt = [
            self.system_message("You are a helpful assistant that will explain a SQL query"),
            self.user_message("Explain this SQL query: " + sql),
        ]
        return self.submit_prompt(prompt=my_prompt)


# Initialize Vanna instance globally
dataAgent = CustomVanna({"path":r"C:\Users\Lim Fang Wei\Downloads\personal\data_agent\chroma_path"})
# dataAgent.connect_to_mssql(
#     odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,54180;DATABASE=historian;UID=n8n;PWD=password'
# )

dataAgent.connect_to_postgres(
    host="localhost",
    dbname="historian",
    user="postgres",
    password="password",
    port=5432,
)

# %%
dataAgent.train(ddl="""
                    CREATE TABLE IF NOT EXISTS public.historian
                    (
                        "tagname" text COLLATE pg_catalog."default",
                        "datetime" text COLLATE pg_catalog."default",
                        "value" double precision,
                        "vvalue" double precision,
                        "minraw" double precision,
                        "maxraw" double precision,
                        "mineu" double precision,
                        "maxeu" double precision,
                        "unit" text COLLATE pg_catalog."default",
                        "quality" boolean,
                        "qualitydetail" bigint,
                        "qualitystring" text COLLATE pg_catalog."default",
                        "wwresolution" bigint,
                        "startdatetime" timestamp without time zone
                    )
                """)

# %%
df_information_schema = dataAgent.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = dataAgent.get_training_plan_generic(df_information_schema)
# plan

# If you like the plan, then uncomment this and run it to train
dataAgent.train(plan=plan)

# %%
dataAgent.train(
    question="Compare LOOP_2_SP vs LOOP_2_PV for the past 30 minutes.", 
    sql="""Select ""startdatetime"", ""tagname"", ""value"" FROM public.historian WHERE ""tagname"" IN ('Cluster1.LOOP_2_SP','Cluster1.LOOP_2_PV') AND ""startdatetime"" > now() - interval '30 minutes' ORDER BY ""startdatetime";"""
)

# %%
dataAgent.train(
    question="What is the total kWh consumed by mixers vs pumps this month?", 
    sql="""SELECT CASE WHEN ""tagname"" ILIKE '%Mixer%' THEN 'Mixer' ELSE 'Pump' END AS equipment_type, SUM(""value"") AS total_kWh FROM public.historian WHERE (""tagname"" ILIKE '%Mixer%TotkWh%' OR ""tagname"" ILIKE '%Pump%TotkWh%') AND ""startdatetime"" >= date_trunc('month', current_date) GROUP BY equipment_type;"""
)

# %%
dataAgent.train(
    question="What is the entry speed and accumulator length for today's shift?", 
    sql="""SELECT ""tagname"", AVG(""value"") AS avg_val FROM public.historian WHERE ""tagname"" IN ('Cluster1.EntrySpeed','Cluster1.EntryAccumulatorLength') AND ""startdatetime"" > date_trunc('day', now()) GROUP BY ""tagname"";"""
)

# %%
dataAgent.train(
    question="Was the agitator in Tank 1 overloaded yesterday?", 
    sql="""SELECT MAX(""value"") AS max_power FROM public.historian WHERE ""tagname"" ILIKE '%Bottler_Tank1_Agitator%TotW1S%' AND ""startdatetime""::date = current_date - interval '1 day';"""
)

# %%
dataAgent.train(
    question="Did Line 1 meet its setpoint speed yesterday?", 
    sql="""SELECT AVG(CASE WHEN ""tagname""='Cluster1.LOOP_3_SP' THEN ""value"" END) AS avg_sp, AVG(CASE WHEN ""tagname""='Cluster1.LOOP_3_PV' THEN ""value"" END) AS avg_pv FROM public.historian WHERE (""tagname""='Cluster1.LOOP_3_SP' OR ""tagname""='Cluster1.LOOP_3_PV') AND ""startdatetime""::date = current_date - interval '1 day';"""
)

# %%
dataAgent.train(
    question="How much did energy tariffs cost for Cluster1 today?", 
    sql="""SELECT SUM(""value"") AS tariff_cost FROM public.historian WHERE ""tagname""='Cluster1.Tariff' AND  ""startdatetime""::date=current_date;"""
)

# %%
dataAgent.train(
    question="Forecast total energy cost for this week.", 
    sql="""SELECT SUM(""value"") AS forecast_kWh FROM public.historian WHERE ""tagname"" ILIKE '%TotkWh%' AND ""startdatetime"" > date_trunc('week', current_date);"""
)

# %%
dataAgent.train(
    question="Suggest best schedule to minimize electricity tariff cost.", 
    sql="""SELECT EXTRACT(HOUR FROM ""startdatetime"") AS hour, AVG(""value"") AS avg_tariff FROM public.historian WHERE""tagname""='Cluster1.Tariff' AND ""startdatetime"" > now() - interval '7 days' GROUP BY hour ORDER BY avg_tariff;"""
)

# %%
dataAgent.train(
    question="Show me the real kWh usage of Line 1 pasteurizer in the last 8 hours.", 
    sql="""SELECT "startdatetime", "value" FROM public.historian WHERE "tagname" ILIKE '%PLT_LINE1%TotkWh%' AND "startdatetime" > now() - interval '8 hours' ORDER BY "startdatetime";"""
)

# %%
dataAgent.train(
    question="What is the current power consumption of Raw Skim Milk Out Pump?", 
    sql="""SELECT "startdatetime", "value" FROM public.historian WHERE "tagname" ILIKE '%Raw_SkimMilkOutPump%TotW1S%' ORDER BY "startdatetime" DESC LIMIT 1;"""
)

# %%
dataAgent.train(
    question="How much power is the Mixer_RawMilk consuming at this moment?", 
    sql="""SELECT "startdatetime", "value" FROM public.historian WHERE "tagname" ILIKE '%Mixer_RawMilk%TotW1S%' ORDER BY "startdatetime" DESC LIMIT 1;"""
)


# %%
dataAgent.train(
    question="HWhat is the total kWh consumed by mixers vs pumps this month?", 
    sql="""SELECT CASE WHEN 'tagname' ILIKE '%Mixer%' THEN 'Mixer' ELSE 'Pump' END AS equipment_type, SUM("value") AS total_kWh FROM public.historian WHERE ("tagname" ILIKE '%Mixer%TotkWh%' OR "tagname" ILIKE '%Pump%TotkWh%');"""
)


# %%
dataAgent.train(
    question="What was the overall OEE for yesterday?", 
    sql="""SELECT AVG(oee) AS overall_oee FROM public.oee_date WHERE date = (CURRENT_DATE - INTERVAL '1 day')::DATE;"""
)


# %%
dataAgent.train(
    question="Predict today’s milk output.", 
    sql="""WITH rate AS (
            SELECT 
                SUM(qty_output - qty_defect) / (SUM(net_operation_time) / 3600) AS units_per_hr 
            FROM oee_date 
            WHERE date = CURRENT_DATE
        ),
        current_output AS (
            SELECT 
                COALESCE(SUM(qty_output - qty_defect), 0) AS total_good_units
            FROM oee_date
            WHERE date = CURRENT_DATE
        )
        SELECT 
            current_output.total_good_units + 
            (rate.units_per_hr * (24 - EXTRACT(HOUR FROM CURRENT_TIMESTAMP))) AS forecast_output 
        FROM rate, current_output;"""
)


# %%
dataAgent.train(
    question="How many hours did Line 1 and Line 2 run this week?", 
    sql="""SELECT 
        id_machine, 
            SUM(net_operation_time) / 3600 AS run_hours 
        FROM oee_date 
        WHERE date >= date_trunc('week', CURRENT_DATE) 
            AND id_machine IN (1, 2) 
        GROUP BY id_machine;
        """
)


# %%
dataAgent.train(
    question="How many hours did Line 1 run this week?", 
    sql="""SELECT 
            SUM(net_operation_time) / 3600 AS run_hours 
        FROM oee_date 
        WHERE id_machine = 1 
            AND date >= date_trunc('week', CURRENT_DATE);
        """
)


# %%
dataAgent.train(
    question="Show trend of energy consumption vs production output over last 30 days.", 
    sql="""SELECT 
            "startdatetime"::date AS day, 
            SUM("value") AS total_kWh, 
            SUM(od.qty_output - od.qty_defect) AS total_units 
        FROM public.historian r 
        JOIN public.oee_date od ON "startdatetime"::date = od.date 
        WHERE "tagname" ILIKE '%TotkWh%' 
            AND "startdatetime" > CURRENT_TIMESTAMP - INTERVAL '30 days' 
        GROUP BY day 
        ORDER BY day;
        """
)


# %%


# %%
dataAgent.get_training_data()


