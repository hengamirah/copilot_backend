# %%
from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat
import os
from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv(r'src\core\.env.development')
from src.core.config import (
    GEMINI_API_KEY,
    COMPLEX_GEMINI_MODEL,
    CHROMA_PATH,
    HOST,
    PORT,
    DBNAME,
    USER,
    PASSWORD,
)
# # Access the variables
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# COMPLEX_GEMINI_MODEL = os.getenv("COMPLEX_GEMINI_MODEL")
# SIMPLE_GEMINI_MODEL = os.getenv("SIMPLE_GEMINI_MODEL")
# APP_NAME = os.getenv("APP_NAME")
# MSSQL = os.getenv("MSSQL")
# CHROMA_PATH = os.getenv("CHROMA_PATH")
# HOST = os.getenv("HOST")
# PORT = os.getenv("PORT")
# DBNAME = os.getenv("DBNAME")
# USER = os.getenv("USER")
# PASSWORD = os.getenv("PASSWORD")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



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

# Ensure CHROMA_PATH exists
import os
os.makedirs(CHROMA_PATH, exist_ok=True)
# Initialize Vanna instance globally using CHROMA_PATH from env
dataAgent = CustomVanna({"path": CHROMA_PATH})

# Connect to Postgres using env values
dataAgent.connect_to_postgres(
    host=HOST,
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    port=int(PORT) if PORT else 5432,
)

# %%
dataAgent.train(ddl="""
                    CREATE TABLE IF NOT EXISTS public.power
                    (
                        sites character varying(50) COLLATE pg_catalog."default",
                        datetimegenerated timestamp with time zone,
                        tagname character varying(100) COLLATE pg_catalog."default",
                        value double precision,
                        datatype character varying(20) COLLATE pg_catalog."default",
                        address text COLLATE pg_catalog."default"
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
# Energy Consumption Analysis

# Question 1
dataAgent.train(
    question="What was the total energy consumption for site-1 last month?", 
    sql="""SELECT 
    sites,
    SUM(value) as total_energy_kwh
FROM public.power
WHERE sites = 'site-1'
    AND (tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%')
    AND datetimegenerated >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
    AND datetimegenerated < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY sites;"""
)

# Question 2
dataAgent.train(
    question="Which site had the highest energy usage in July 2025?", 
    sql="""SELECT 
    sites,
    SUM(value) as total_energy_kwh
FROM public.power
WHERE (tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%')
    AND datetimegenerated >= '2025-07-01'
    AND datetimegenerated < '2025-08-01'
GROUP BY sites
ORDER BY total_energy_kwh DESC
LIMIT 1;"""
)

# Question 3
dataAgent.train(
    question="Show me the daily energy consumption trend for pminc1 over the past week", 
    sql="""SELECT 
    DATE(datetimegenerated) as consumption_date,
    SUM(value) as daily_energy_kwh
FROM public.power
WHERE tagname LIKE 'pminc1%'
    AND (tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%')
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(datetimegenerated)
ORDER BY consumption_date;"""
)

# Question 4
dataAgent.train(
    question="Compare energy consumption between site-1 and site-2 for Q2 2025", 
    sql="""SELECT 
    sites,
    SUM(value) as total_energy_kwh,
    AVG(value) as avg_energy_kwh,
    COUNT(*) as reading_count
FROM public.power
WHERE sites IN ('site-1', 'site-2')
    AND (tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%')
    AND datetimegenerated >= '2025-04-01'
    AND datetimegenerated < '2025-07-01'
GROUP BY sites
ORDER BY total_energy_kwh DESC;"""
)


# %%
# Power Demand & Load Analysis

# Question 5
dataAgent.train(
    question="What was the peak power demand at site-1 yesterday?", 
    sql="""SELECT 
    sites,
    tagname,
    MAX(value) as peak_power_kw,
    datetimegenerated as peak_time
FROM public.power
WHERE sites = 'site-1'
    AND (tagname ILIKE '%power%' OR tagname ILIKE '%kw%')
    AND tagname NOT ILIKE '%kwh%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '1 day'
    AND datetimegenerated < CURRENT_DATE
GROUP BY sites, tagname, datetimegenerated
ORDER BY peak_power_kw DESC
LIMIT 1;"""
)


# Question 6
dataAgent.train(
    question="Show me the hourly power consumption pattern for the last 7 days", 
    sql="""SELECT 
    DATE_TRUNC('hour', datetimegenerated) as hour_timestamp,
    AVG(value) as avg_power_kw,
    MAX(value) as peak_power_kw,
    MIN(value) as min_power_kw
FROM public.power
WHERE (tagname ILIKE '%power%' OR tagname ILIKE '%kw%')
    AND tagname NOT ILIKE '%kwh%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', datetimegenerated)
ORDER BY hour_timestamp;"""
)

# Question 7
dataAgent.train(
    question="When does site-2 typically experience peak electrical load?", 
    sql="""SELECT 
    EXTRACT(HOUR FROM datetimegenerated) as hour_of_day,
    AVG(value) as avg_load_kw,
    MAX(value) as peak_load_kw
FROM public.power
WHERE sites = 'site-2'
    AND (tagname ILIKE '%power%' OR tagname ILIKE '%load%')
    AND tagname NOT ILIKE '%kwh%'
GROUP BY EXTRACT(HOUR FROM datetimegenerated)
ORDER BY peak_load_kw DESC
LIMIT 5;"""
)

# Question 8
dataAgent.train(
    question="What is the load factor for pminc2 over the past month?", 
    sql="""SELECT 
    tagname,
    AVG(value) / NULLIF(MAX(value), 0) * 100 as load_factor_percentage,
    AVG(value) as avg_load_kw,
    MAX(value) as peak_load_kw
FROM public.power
WHERE tagname LIKE 'pminc2%'
    AND (tagname ILIKE '%power%' OR tagname ILIKE '%kw%')
    AND tagname NOT ILIKE '%kwh%'
    AND datetimegenerated >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
    AND datetimegenerated < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY tagname;"""
)


# %%
# Chiller Performance

# Question 9
dataAgent.train(
    question="What is the average temperature differential (ΔT) for chiller ch2 this week?", 
    sql="""SELECT 
    AVG(supply.value) as avg_supply_temp,
    AVG(return.value) as avg_return_temp,
    AVG(return.value - supply.value) as avg_delta_t
FROM public.power supply
JOIN public.power return ON 
    supply.datetimegenerated = return.datetimegenerated
    AND supply.sites = return.sites
WHERE supply.tagname LIKE 'ch2%supply%temp%'
    AND return.tagname LIKE 'ch2%return%temp%'
    AND supply.datetimegenerated >= DATE_TRUNC('week', CURRENT_DATE)
GROUP BY supply.sites;"""
)

# Question 10
dataAgent.train(
    question="Which chiller is operating most efficiently based on supply/return temperatures?", 
    sql="""SELECT 
    SUBSTRING(supply.tagname FROM '^ch[0-9]+') as chiller_id,
    AVG(return.value - supply.value) as avg_delta_t,
    AVG(supply.value) as avg_supply_temp,
    AVG(return.value) as avg_return_temp,
    COUNT(*) as reading_count
FROM public.power supply
JOIN public.power return ON 
    SUBSTRING(supply.tagname FROM '^ch[0-9]+') = SUBSTRING(return.tagname FROM '^ch[0-9]+')
    AND supply.datetimegenerated = return.datetimegenerated
    AND supply.sites = return.sites
WHERE supply.tagname ILIKE '%supply%temp%'
    AND return.tagname ILIKE '%return%temp%'
    AND supply.datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY SUBSTRING(supply.tagname FROM '^ch[0-9]+')
ORDER BY avg_delta_t DESC
LIMIT 1;"""
)

# Question 11
dataAgent.train(
    question="Show me the chiller water flow rate trends over the past 24 hours", 
    sql="""SELECT 
    datetimegenerated,
    tagname,
    value as flow_rate
FROM public.power
WHERE tagname ILIKE '%ch%flow%'
    AND datetimegenerated >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY tagname, datetimegenerated;"""
)

# Question 12
dataAgent.train(
    question="Has the chiller supply temperature been within the 6-8°C setpoint range?", 
    sql="""SELECT 
    tagname,
    datetimegenerated,
    value as supply_temp,
    CASE 
        WHEN value BETWEEN 6 AND 8 THEN 'Within Range'
        WHEN value < 6 THEN 'Below Range'
        ELSE 'Above Range'
    END as status,
    COUNT(*) OVER (PARTITION BY tagname) as total_readings,
    SUM(CASE WHEN value BETWEEN 6 AND 8 THEN 1 ELSE 0 END) OVER (PARTITION BY tagname) as in_range_count
FROM public.power
WHERE tagname ILIKE '%ch%supply%temp%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY tagname, datetimegenerated DESC;"""
)


# %%
# Electrical Quality

# Question 13
dataAgent.train(
    question="Is there any phase imbalance in pminc1?", 
    sql="""SELECT 
    datetimegenerated,
    MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) as phase_a_current,
    MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) as phase_b_current,
    MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END) as phase_c_current,
    (MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) + 
     MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) + 
     MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END)) / 3 as avg_current,
    GREATEST(
        ABS(MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) - 
            (MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) + 
             MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) + 
             MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END)) / 3),
        ABS(MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) - 
            (MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) + 
             MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) + 
             MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END)) / 3),
        ABS(MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END) - 
            (MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) + 
             MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) + 
             MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END)) / 3)
    ) / NULLIF((MAX(CASE WHEN tagname ILIKE '%pminc1%phase%a%current%' THEN value END) + 
                MAX(CASE WHEN tagname ILIKE '%pminc1%phase%b%current%' THEN value END) + 
                MAX(CASE WHEN tagname ILIKE '%pminc1%phase%c%current%' THEN value END)) / 3, 0) * 100 as imbalance_percentage
FROM public.power
WHERE tagname ILIKE '%pminc1%'
    AND tagname ILIKE '%current%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY datetimegenerated
ORDER BY datetimegenerated DESC;"""
)

# Question 14
dataAgent.train(
    question="Show me the power factor trends for all power meters", 
    sql="""SELECT 
    tagname,
    DATE_TRUNC('hour', datetimegenerated) as hour_timestamp,
    AVG(value) as avg_power_factor,
    MIN(value) as min_power_factor,
    MAX(value) as max_power_factor
FROM public.power
WHERE (tagname ILIKE '%power%factor%' OR tagname ILIKE '%pf%')
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY tagname, DATE_TRUNC('hour', datetimegenerated)
ORDER BY tagname, hour_timestamp;"""
)

# Question 15
dataAgent.train(
    question="Are there any voltage stability issues at site-1?", 
    sql="""SELECT 
    tagname,
    datetimegenerated,
    value as voltage,
    AVG(value) OVER (PARTITION BY tagname ORDER BY datetimegenerated ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as moving_avg,
    STDDEV(value) OVER (PARTITION BY tagname ORDER BY datetimegenerated ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as moving_stddev,
    CASE 
        WHEN value < 207 OR value > 253 THEN 'Out of Range (207-253V)'
        WHEN ABS(value - LAG(value) OVER (PARTITION BY tagname ORDER BY datetimegenerated)) > 10 THEN 'Rapid Change'
        ELSE 'Stable'
    END as stability_status
FROM public.power
WHERE sites = 'site-1'
    AND tagname ILIKE '%voltage%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY tagname, datetimegenerated DESC;"""
)

# Question 16
dataAgent.train(
    question="What is the current load on each phase of pminc2?", 
    sql="""SELECT 
    tagname,
    value as current_amps,
    datetimegenerated
FROM public.power
WHERE tagname LIKE 'pminc2%'
    AND tagname ILIKE '%current%'
    AND datetimegenerated >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
ORDER BY datetimegenerated DESC
LIMIT 3;"""
)


# %%
# Anomaly Detection & Diagnostics

# Question 17
dataAgent.train(
    question="Why did power consumption spike at 3am yesterday?", 
    sql="""WITH hourly_avg AS (
    SELECT 
        DATE_TRUNC('hour', datetimegenerated) as hour_timestamp,
        AVG(value) as avg_power
    FROM public.power
    WHERE (tagname ILIKE '%power%' OR tagname ILIKE '%kw%')
        AND tagname NOT ILIKE '%kwh%'
        AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY DATE_TRUNC('hour', datetimegenerated)
),
spike_analysis AS (
    SELECT 
        hour_timestamp,
        avg_power,
        AVG(avg_power) OVER () as overall_avg,
        STDDEV(avg_power) OVER () as overall_stddev
    FROM hourly_avg
)
SELECT 
    p.tagname,
    p.datetimegenerated,
    p.value,
    sa.avg_power as hour_avg,
    sa.overall_avg,
    (p.value - sa.overall_avg) / NULLIF(sa.overall_stddev, 0) as z_score
FROM public.power p
JOIN spike_analysis sa ON DATE_TRUNC('hour', p.datetimegenerated) = sa.hour_timestamp
WHERE p.datetimegenerated >= (CURRENT_DATE - INTERVAL '1 day') + INTERVAL '3 hours'
    AND p.datetimegenerated < (CURRENT_DATE - INTERVAL '1 day') + INTERVAL '4 hours'
    AND (p.tagname ILIKE '%power%' OR p.tagname ILIKE '%kw%')
    AND p.tagname NOT ILIKE '%kwh%'
ORDER BY p.value DESC
LIMIT 20;"""
)

# Question 18
dataAgent.train(
    question="Are there any unusual patterns in the chiller flow rates?", 
    sql="""WITH flow_stats AS (
    SELECT 
        tagname,
        AVG(value) as avg_flow,
        STDDEV(value) as stddev_flow,
        MIN(value) as min_flow,
        MAX(value) as max_flow
    FROM public.power
    WHERE tagname ILIKE '%ch%flow%'
        AND datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY tagname
)
SELECT 
    p.tagname,
    p.datetimegenerated,
    p.value as flow_rate,
    fs.avg_flow,
    fs.stddev_flow,
    ABS(p.value - fs.avg_flow) / NULLIF(fs.stddev_flow, 0) as z_score,
    CASE 
        WHEN ABS(p.value - fs.avg_flow) > 2 * fs.stddev_flow THEN 'Anomaly'
        WHEN p.value = 0 THEN 'Zero Flow'
        ELSE 'Normal'
    END as status
FROM public.power p
JOIN flow_stats fs ON p.tagname = fs.tagname
WHERE p.tagname ILIKE '%ch%flow%'
    AND p.datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
    AND (ABS(p.value - fs.avg_flow) > 2 * fs.stddev_flow OR p.value = 0)
ORDER BY z_score DESC NULLS LAST;"""
)

# Question 19
dataAgent.train(
    question="Which equipment had the most downtime last week?", 
    sql="""WITH equipment_status AS (
    SELECT 
        SUBSTRING(tagname FROM '^[a-z0-9]+') as equipment_id,
        datetimegenerated,
        value,
        CASE 
            WHEN value = 0 OR value IS NULL THEN 1
            ELSE 0
        END as is_down,
        LEAD(datetimegenerated) OVER (PARTITION BY tagname ORDER BY datetimegenerated) as next_timestamp
    FROM public.power
    WHERE (tagname ILIKE '%status%' OR tagname ILIKE '%running%' OR tagname ILIKE '%power%')
        AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
)
SELECT 
    equipment_id,
    SUM(CASE WHEN is_down = 1 THEN 
        EXTRACT(EPOCH FROM (COALESCE(next_timestamp, CURRENT_TIMESTAMP) - datetimegenerated)) / 3600 
        ELSE 0 END) as downtime_hours,
    COUNT(CASE WHEN is_down = 1 THEN 1 END) as downtime_events,
    (SUM(CASE WHEN is_down = 1 THEN 
        EXTRACT(EPOCH FROM (COALESCE(next_timestamp, CURRENT_TIMESTAMP) - datetimegenerated)) / 3600 
        ELSE 0 END) / 168) * 100 as downtime_percentage
FROM equipment_status
GROUP BY equipment_id
ORDER BY downtime_hours DESC
LIMIT 10;"""
)

# Question 20
dataAgent.train(
    question="Did any meter readings fall outside normal ranges?", 
    sql="""WITH parameter_ranges AS (
    SELECT 
        tagname,
        AVG(value) as avg_value,
        STDDEV(value) as stddev_value,
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY value) as lower_bound,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value) as upper_bound
    FROM public.power
    WHERE datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY tagname
)
SELECT 
    p.tagname,
    p.datetimegenerated,
    p.value,
    pr.avg_value,
    pr.lower_bound,
    pr.upper_bound,
    CASE 
        WHEN p.value < pr.lower_bound THEN 'Below Normal'
        WHEN p.value > pr.upper_bound THEN 'Above Normal'
        ELSE 'Normal'
    END as status
FROM public.power p
JOIN parameter_ranges pr ON p.tagname = pr.tagname
WHERE p.datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
    AND (p.value < pr.lower_bound OR p.value > pr.upper_bound)
ORDER BY p.datetimegenerated DESC;"""
)


# %%
# Efficiency & Optimization

# Question 21
dataAgent.train(
    question="What is the energy efficiency of our chiller system?", 
    sql="""WITH chiller_power AS (
    SELECT 
        datetimegenerated,
        SUM(CASE WHEN tagname ILIKE '%ch%power%' THEN value ELSE 0 END) as total_chiller_power
    FROM public.power
    WHERE tagname ILIKE '%ch%'
        AND (tagname ILIKE '%power%' OR tagname ILIKE '%kw%')
        AND tagname NOT ILIKE '%kwh%'
        AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY datetimegenerated
),
cooling_capacity AS (
    SELECT 
        supply.datetimegenerated,
        AVG((return.value - supply.value) * flow.value * 4.186) as cooling_output_kw
    FROM public.power supply
    JOIN public.power return ON 
        SUBSTRING(supply.tagname FROM '^ch[0-9]+') = SUBSTRING(return.tagname FROM '^ch[0-9]+')
        AND supply.datetimegenerated = return.datetimegenerated
    JOIN public.power flow ON 
        SUBSTRING(supply.tagname FROM '^ch[0-9]+') = SUBSTRING(flow.tagname FROM '^ch[0-9]+')
        AND supply.datetimegenerated = flow.datetimegenerated
    WHERE supply.tagname ILIKE '%supply%temp%'
        AND return.tagname ILIKE '%return%temp%'
        AND flow.tagname ILIKE '%flow%'
        AND supply.datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY supply.datetimegenerated
)
SELECT 
    AVG(cc.cooling_output_kw / NULLIF(cp.total_chiller_power, 0)) as avg_cop,
    AVG(cc.cooling_output_kw) as avg_cooling_output_kw,
    AVG(cp.total_chiller_power) as avg_power_input_kw
FROM chiller_power cp
JOIN cooling_capacity cc ON cp.datetimegenerated = cc.datetimegenerated
WHERE cp.total_chiller_power > 0;"""
)

# Question 22
dataAgent.train(
    question="How much energy could we save by improving power factor to 0.95?", 
    sql="""WITH current_pf AS (
    SELECT 
        AVG(pf.value) as avg_power_factor,
        AVG(power.value) as avg_apparent_power
    FROM public.power pf
    JOIN public.power power ON 
        pf.datetimegenerated = power.datetimegenerated
        AND pf.sites = power.sites
    WHERE pf.tagname ILIKE '%power%factor%'
        AND power.tagname ILIKE '%power%'
        AND power.tagname NOT ILIKE '%factor%'
        AND pf.datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    avg_power_factor as current_power_factor,
    0.95 as target_power_factor,
    avg_apparent_power as current_apparent_power_kva,
    avg_apparent_power * avg_power_factor as current_real_power_kw,
    avg_apparent_power * 0.95 as improved_real_power_kw,
    (avg_apparent_power * 0.95 - avg_apparent_power * avg_power_factor) as potential_savings_kw,
    (avg_apparent_power * 0.95 - avg_apparent_power * avg_power_factor) * 730 as monthly_savings_kwh
FROM current_pf;"""
)

# Question 23
dataAgent.train(
    question="What are the operating hours for each chiller?", 
    sql="""WITH chiller_status AS (
    SELECT 
        SUBSTRING(tagname FROM '^ch[0-9]+') as chiller_id,
        datetimegenerated,
        value,
        CASE WHEN value > 0 THEN 1 ELSE 0 END as is_running,
        LEAD(datetimegenerated) OVER (PARTITION BY tagname ORDER BY datetimegenerated) as next_timestamp
    FROM public.power
    WHERE tagname ILIKE 'ch%'
        AND (tagname ILIKE '%power%' OR tagname ILIKE '%status%' OR tagname ILIKE '%running%')
        AND datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    chiller_id,
    SUM(CASE WHEN is_running = 1 THEN 
        EXTRACT(EPOCH FROM (COALESCE(next_timestamp, CURRENT_TIMESTAMP) - datetimegenerated)) / 3600 
        ELSE 0 END) as operating_hours,
    COUNT(CASE WHEN is_running = 1 THEN 1 END) as run_events,
    (SUM(CASE WHEN is_running = 1 THEN 
        EXTRACT(EPOCH FROM (COALESCE(next_timestamp, CURRENT_TIMESTAMP) - datetimegenerated)) / 3600 
        ELSE 0 END) / 720) * 100 as utilization_percentage
FROM chiller_status
GROUP BY chiller_id
ORDER BY operating_hours DESC;"""
)

# Question 24
dataAgent.train(
    question="Which time periods have the lowest power costs based on consumption patterns?", 
    sql="""SELECT 
    EXTRACT(HOUR FROM datetimegenerated) as hour_of_day,
    EXTRACT(DOW FROM datetimegenerated) as day_of_week,
    AVG(value) as avg_power_kw,
    SUM(value) as total_power_kw,
    COUNT(*) as reading_count,
    CASE 
        WHEN EXTRACT(HOUR FROM datetimegenerated) BETWEEN 22 AND 23 OR EXTRACT(HOUR FROM datetimegenerated) BETWEEN 0 AND 6 THEN 'Off-Peak'
        WHEN EXTRACT(HOUR FROM datetimegenerated) BETWEEN 7 AND 9 OR EXTRACT(HOUR FROM datetimegenerated) BETWEEN 17 AND 21 THEN 'Peak'
        ELSE 'Mid-Peak'
    END as period_type
FROM public.power
WHERE (tagname ILIKE '%power%' OR tagname ILIKE '%kw%')
    AND tagname NOT ILIKE '%kwh%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY EXTRACT(HOUR FROM datetimegenerated), EXTRACT(DOW FROM datetimegenerated)
ORDER BY avg_power_kw ASC
LIMIT 10;"""
)


# %%

# Comparative Analysis

# Question 25
dataAgent.train(
    question="Compare the energy efficiency across all sites", 
    sql="""SELECT 
    sites,
    SUM(CASE WHEN tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%' THEN value ELSE 0 END) as total_energy_kwh,
    AVG(CASE WHEN tagname ILIKE '%power%' AND tagname NOT ILIKE '%kwh%' THEN value END) as avg_power_kw,
    MAX(CASE WHEN tagname ILIKE '%power%' AND tagname NOT ILIKE '%kwh%' THEN value END) as peak_power_kw,
    SUM(CASE WHEN tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%' THEN value ELSE 0 END) / 
        NULLIF(MAX(CASE WHEN tagname ILIKE '%power%' AND tagname NOT ILIKE '%kwh%' THEN value END), 0) as load_factor,
    AVG(CASE WHEN tagname ILIKE '%power%factor%' THEN value END) as avg_power_factor
FROM public.power
WHERE datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY sites
ORDER BY total_energy_kwh DESC;"""
)

# Question 26
dataAgent.train(
    question="How does current week's consumption compare to the same week last year?", 
    sql="""WITH current_week AS (
    SELECT 
        sites,
        SUM(value) as energy_kwh
    FROM public.power
    WHERE (tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%')
        AND datetimegenerated >= DATE_TRUNC('week', CURRENT_DATE)
    GROUP BY sites
),
last_year_week AS (
    SELECT 
        sites,
        SUM(value) as energy_kwh
    FROM public.power
    WHERE (tagname ILIKE '%energy%' OR tagname ILIKE '%kwh%')
        AND datetimegenerated >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 year')
        AND datetimegenerated < DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 year') + INTERVAL '7 days'
    GROUP BY sites
)
SELECT 
    COALESCE(cw.sites, lyw.sites) as sites,
    cw.energy_kwh as current_week_kwh,
    lyw.energy_kwh as last_year_week_kwh,
    cw.energy_kwh - lyw.energy_kwh as difference_kwh,
    ((cw.energy_kwh - lyw.energy_kwh) / NULLIF(lyw.energy_kwh, 0)) * 100 as percentage_change
FROM current_week cw
FULL OUTER JOIN last_year_week lyw ON cw.sites = lyw.sites
ORDER BY sites;"""
)

# Question 27
dataAgent.train(
    question="Which site has the most stable voltage supply?", 
    sql="""SELECT 
    sites,
    AVG(value) as avg_voltage,
    STDDEV(value) as voltage_stddev,
    MIN(value) as min_voltage,
    MAX(value) as max_voltage,
    (MAX(value) - MIN(value)) as voltage_range,
    STDDEV(value) / NULLIF(AVG(value), 0) * 100 as coefficient_of_variation
FROM public.power
WHERE tagname ILIKE '%voltage%'
    AND datetimegenerated >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY sites
ORDER BY voltage_stddev ASC
LIMIT 1;"""
)

# Question 28
dataAgent.train(
    question="What is the performance difference between ch2 and ch3 chillers?", 
    sql="""WITH chiller_metrics AS (
    SELECT 
        SUBSTRING(tagname FROM '^ch[0-9]+') as chiller_id,
        AVG(CASE WHEN tagname ILIKE '%supply%temp%' THEN value END) as avg_supply_temp,
        AVG(CASE WHEN tagname ILIKE '%return%temp%' THEN value END) as avg_return_temp,
        AVG(CASE WHEN tagname ILIKE '%flow%' THEN value END) as avg_flow_rate,
        AVG(CASE WHEN tagname ILIKE '%power%' AND tagname NOT ILIKE '%factor%' THEN value END) as avg_power_kw
    FROM public.power
    WHERE (tagname LIKE 'ch2%' OR tagname LIKE 'ch3%')
        AND datetimegenerated >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY SUBSTRING(tagname FROM '^ch[0-9]+')
    )
    SELECT 
        chiller_id,
        avg_supply_temp,
        avg_return_temp,
        (avg_return_temp - avg_supply_temp) as delta_t,
        avg_flow_rate,
        avg_power_kw,
        ((avg_return_temp - avg_supply_temp) * avg_flow_rate * 4.186) / NULLIF(avg_power_kw, 0) as estimated_cop
    FROM chiller_metrics
    WHERE chiller_id IN ('ch2', 'ch3')
    ORDER BY chiller_id;"""
)

# %%
# Read markdown file into string

context_v2_power_md = r'src\agents\sub_agents\vanna_agent\context_v2_power.md'
with open(context_v2_power_md, 'r', encoding='utf-8') as f:
    md_content = f.read()

print(md_content)

# %%
dataAgent.add_documentation(md_content)


