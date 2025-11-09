# Building Energy Management System Datasource

This data source contains time-series sensor and meter readings from Building Energy Management Systems across multiple facility sites. Each row represents a single tag reading at a specific timestamp, capturing various electrical, chiller, and HVAC operational metrics. This is the core table for energy consumption analytics, equipment performance monitoring, and operational efficiency analysis.

---

## 1. Schema Overview

- **Database**: PostgreSQL
- **Database Name**: power
- **Table Name**: power
- **Data Model**: Time-series tag-value pairs with site context

- **Columns**:
  - `site` (String): Site identifier/name. Low cardinality. Examples: "site-1", "site-2"
  - `dateTimeGenerated` (Timestamp): UTC timestamp when the tag value was recorded. Used for temporal filtering and trend analysis.
  - `tagName` (String): Tag identifier following a hierarchical naming convention. High cardinality. Identifies the specific sensor/meter and measurement type.
  - `value` (String/Numeric): The measured value. Data type varies based on tag type. Can be numeric (Float64) or string for status indicators.
  - `dataType` (String): Data type indicator of the value field (e.g., "Double", "String", "Integer").
  - `address` (String): Internal system address/path for the tag. Informative only, not typically used for analysis.

---

## 2. Key Columns

### `site`
- **Type**: `String`
- **Format**: Kebab-case site identifier
- **Example Values**:
  - `"site-1"`
  - `"site-2"`
- **Cardinality**: Low (~3-10 sites)
- **Notes**: Primary dimension for cross-site comparisons and site-specific filtering.

### `dateTimeGenerated`
- **Type**: `Timestamp (DateTime with timezone)`
- **Format**: `YYYY-MM-DD HH:MM:SS+00:00` (UTC)
- **Example Values**:
  - `"2025-07-01 23:00:54+00:00"`
  - `"2025-07-02 08:15:30+00:00"`
- **Notes**: Used for time-based filtering, trend analysis, and time-series aggregations. Always in UTC timezone.

### `tagName`
- **Type**: `String`
- **Format**: Hierarchical naming with hyphen separators
- **Pattern**: `{equipment_id}-{metric_type}[_{phase}]`
- **Cardinality**: High (hundreds to thousands)
- **Examples**:
  - `"pminc1-energy"` - Power meter 1 energy consumption
  - `"pminc1-amp_r"` - Power meter 1 current (R phase)
  - `"ch2-chw_s_temp"` - Chiller 2 supply water temperature
  - `"embs-flow"` - Energy meter basement chiller water flow
- **Notes**: Primary dimension for metric type selection. See Section 3 for detailed tag taxonomy.

### `value`
- **Type**: `String` (stored as string, interpreted based on dataType)
- **Range**: Varies widely by tag type
- **Distribution**: Tag-dependent; energy values are monotonically increasing, instantaneous readings vary continuously
- **Usage**: Main fact value for all analysis. Must be cast to appropriate numeric type for calculations.

### `dataType`
- **Type**: `String`
- **Common Values**: `"Double"`, `"Integer"`, `"String"`, `"Boolean"`
- **Usage**: Indicates how to interpret and cast the `value` field for calculations.

### `address`
- **Type**: `String`
- **Format**: OPC UA or proprietary addressing scheme
- **Example**: `"0:Application Tags.PMINC1_E"`
- **Usage**: Metadata only; typically not used in analytical queries.

---

## 3. Tag Taxonomy and Naming Conventions

The `tagName` field follows a structured naming convention where:
- **`*`** = wildcard representing any equipment identifier (e.g., pminc1, pminc2, ch3)
- **`|`** = logical OR operator (e.g., `_r|y|b` means `_r` OR `_y` OR `_b`)

### Power Metering Tags (Electrical)

#### Energy Consumption
- **Pattern**: `*-energy`
- **Description**: Cumulative energy consumption
- **Unit**: kWh (kilowatt-hours)
- **Type**: Monotonically increasing counter
- **Examples**: `pminc1-energy`, `pminc2-energy`
- **Analysis Use**: Calculate energy consumption over periods using delta calculations

#### Power Demand
- **Pattern**: `*-pwr`
- **Description**: Real-time power consumption
- **Unit**: kW (kilowatts)
- **Type**: Instantaneous measurement
- **Examples**: `pminc1-pwr`, `pminc2-pwr`
- **Analysis Use**: Monitor current load, identify peak usage periods

#### Maximum Demand
- **Pattern**: `*-md`
- **Description**: Maximum demand recorded
- **Unit**: kW (kilowatts)
- **Type**: Peak value tracking
- **Examples**: `pminc1-md`, `pminc2-md`
- **Analysis Use**: Capacity planning, demand charge analysis

#### Current (Three-Phase)
- **Pattern**: `*-amp_r|y|b`
- **Description**: Electrical current per phase
- **Unit**: Amperes (A)
- **Phases**:
  - `_r` = Red/Phase A
  - `_y` = Yellow/Phase B
  - `_b` = Blue/Phase C
- **Type**: Instantaneous measurement
- **Examples**: `pminc1-amp_r`, `pminc1-amp_y`, `pminc1-amp_b`
- **Analysis Use**: Load balancing analysis, circuit health monitoring

#### Voltage (Three-Phase)
- **Pattern**: `*-volt_r|y|b`
- **Description**: Electrical voltage per phase
- **Unit**: Volts (V)
- **Phases**:
  - `_r` = Red/Phase A
  - `_y` = Yellow/Phase B
  - `_b` = Blue/Phase C
- **Type**: Instantaneous measurement
- **Examples**: `pminc1-volt_r`, `pminc1-volt_y`, `pminc1-volt_b`
- **Analysis Use**: Power quality monitoring, voltage stability analysis

#### Power Factor
- **Pattern**: `*-pf`
- **Description**: Power factor (ratio of real to apparent power)
- **Unit**: Unitless (typically -1.0 to 1.0)
- **Type**: Instantaneous measurement
- **Examples**: `pminc1-pf`, `pminc2-pf`
- **Analysis Use**: Electrical efficiency monitoring, power quality assessment

### Chiller/HVAC Water System Tags

#### Water Flow Rate
- **Pattern**: `*-flow`
- **Description**: Chilled water or condenser water flow rate
- **Unit**: m³/h (cubic meters per hour)
- **Type**: Instantaneous measurement
- **Examples**: `embs-flow`, `eml1-flow`, `ch2-flow`
- **Analysis Use**: System capacity utilization, flow rate optimization

#### Supply Temperature
- **Pattern**: `*-s_temp`
- **Description**: Supply water temperature (leaving the chiller)
- **Unit**: °C (degrees Celsius)
- **Type**: Instantaneous measurement
- **Examples**: `embs-s_temp`, `ch2-chw_s_temp`
- **Analysis Use**: Chiller efficiency, temperature setpoint compliance

#### Return Temperature
- **Pattern**: `*-r_temp`
- **Description**: Return water temperature (entering the chiller)
- **Unit**: °C (degrees Celsius)
- **Type**: Instantaneous measurement
- **Examples**: `embs-r_temp`, `ch2-chw_r_temp`
- **Analysis Use**: Cooling load calculation (ΔT analysis), system efficiency

### Equipment Identifiers

Common equipment prefixes found in the data:
- **`pminc*`**: Power meter incoming (main electrical meters)
- **`ch*`**: Chiller units (e.g., ch2, ch3)
- **`em*`**: Energy/flow meters (embs, eml1, eml2, eml3, emml, emta, emtb)
- **`ct*`**: Cooling tower units (ct1a, ct1b, ct2a, ct2b, ct3a, ct3b, ct4a, ct4b)

---

## 4. Facts, Dimensions, and Metrics

### Facts (Measurements)
- `value` - The primary fact field containing all measurements
  - Energy consumption (kWh)
  - Power demand (kW)
  - Current (A)
  - Voltage (V)
  - Power factor
  - Flow rate (m³/h)
  - Temperature (°C)

### Dimensions
- `site` (categorical) - Facility location
- `dateTimeGenerated` (temporal) - Timestamp of reading
- `tagName` (categorical) - Metric identifier
- `dataType` (categorical) - Value data type

### Calculated Metrics

#### Energy Metrics
- **Energy Consumption (Period)**: `MAX(value) - MIN(value)` WHERE `tagName LIKE '%energy'` GROUP BY time period
- **Average Power Demand**: `AVG(value)` WHERE `tagName LIKE '%pwr'`
- **Peak Power**: `MAX(value)` WHERE `tagName LIKE '%pwr'`
- **Load Factor**: `AVG(power) / MAX(power)` - Efficiency of power usage

#### Chiller Efficiency Metrics
- **Temperature Differential (ΔT)**: `AVG(r_temp) - AVG(s_temp)` - Cooling effectiveness
- **Cooling Load**: `Flow × ΔT × Specific_Heat_Constant` - Actual cooling provided
- **Chiller Efficiency**: `Cooling_Load / Energy_Consumption` - kW/ton or COP

#### Electrical Quality Metrics
- **Phase Imbalance**: Standard deviation of current across phases
- **Voltage Deviation**: Distance from nominal voltage (e.g., 415V, 240V)
- **Power Quality Score**: Based on voltage stability and power factor

#### Cross-Tag Aggregations
- **Site Total Energy**: `SUM(energy consumption)` across all meters per site
- **Equipment Utilization**: Percentage of time equipment is running (power > threshold)
- **Multi-Equipment Efficiency**: Compare chillers, meters across sites

---

## 5. Data Patterns

- **Time Range**: Typically contains 12-24 months of rolling historical data
- **Sampling Frequency**:
  - Most tags: 1-5 minute intervals
  - Some tags: 15-minute or hourly intervals
  - Sampling rate varies by tag type and equipment
- **Timezone**: All timestamps in UTC (+00:00)
- **Seasonality**:
  - Daily patterns: Peak electrical load during business hours (8am-6pm local time)
  - Weekly patterns: Lower consumption on weekends
  - Annual patterns: Higher cooling loads in summer months, lower in winter
- **Data Completeness**:
  - Generally high completeness for critical meters (>95%)
  - Occasional gaps due to communication failures or maintenance
  - Missing data typically appears as absent records, not NULL values
- **Value Ranges** (typical):
  - Energy: 0 to 50,000,000+ kWh (cumulative)
  - Power: 0 to 2,000 kW
  - Current: 0 to 500 A per phase
  - Voltage: 200 to 450 V
  - Power Factor: -1.0 to 1.0 (typically 0.8 to 1.0)
  - Flow: 0 to 500 m³/h
  - Temperature: 5 to 40 °C (chilled water systems)
- **Data Quality Notes**:
  - Cumulative energy values reset occasionally during meter maintenance
  - Outliers may occur during equipment startup/shutdown
  - Some tags may report constant values when equipment is offline

---
<!--
## 6. Relationships and Join Potential

- **Self-Joins**: Join multiple tags from the same equipment/timestamp for comprehensive analysis
  - Example: Join supply and return temps for ΔT calculation
  - Example: Join all three phase currents for imbalance analysis

- **Time-Based Joins**:
  - Join readings within time windows for correlation analysis
  - WINDOW functions for moving averages and trends

- **External Table Joins** (potential):
  - Site metadata table (site name → location, timezone, building type, area)
  - Equipment registry (equipment ID → capacity, model, install date)
  - Weather data (timestamp + location → outdoor temp, humidity)
  - Occupancy data (timestamp + site → occupancy count)
  - Utility tariff table (timestamp → rate per kWh, demand charges)

- **Pivot Operations**:
  - Wide-format transformation where tagNames become columns
  - Useful for ML feature engineering and correlation matrices -->

---

## 7. Example Questions the LLM Should Be Able to Answer

### Energy Consumption Analysis
- "What was the total energy consumption for site-1 last month?"
- "Which site had the highest energy usage in July 2025?"
- "Show me the daily energy consumption trend for pminc1 over the past week"
- "Compare energy consumption between site-1 and site-2 for Q2 2025"

### Power Demand & Load Analysis
- "What was the peak power demand at site-1 yesterday?"
- "Show me the hourly power consumption pattern for the last 7 days"
- "When does site-2 typically experience peak electrical load?"
- "What is the load factor for pminc2 over the past month?"

### Chiller Performance
- "What is the average temperature differential (ΔT) for chiller ch2 this week?"
- "Which chiller is operating most efficiently based on supply/return temperatures?"
- "Show me the chiller water flow rate trends over the past 24 hours"
- "Has the chiller supply temperature been within the 6-8°C setpoint range?"

### Electrical Quality
- "Is there any phase imbalance in pminc1?"
- "Show me the power factor trends for all power meters"
- "Are there any voltage stability issues at site-1?"
- "What is the current load on each phase of pminc2?"

### Anomaly Detection & Diagnostics
- "Why did power consumption spike at 3am yesterday?"
- "Are there any unusual patterns in the chiller flow rates?"
- "Which equipment had the most downtime last week?"
- "Did any meter readings fall outside normal ranges?"

### Efficiency & Optimization
- "What is the energy efficiency of our chiller system?"
- "How much energy could we save by improving power factor to 0.95?"
- "What are the operating hours for each chiller?"
- "Which time periods have the lowest power costs based on consumption patterns?"

### Comparative Analysis
- "Compare the energy efficiency across all sites"
- "How does current week's consumption compare to the same week last year?"
- "Which site has the most stable voltage supply?"
- "What is the performance difference between ch2 and ch3 chillers?"

---

## 8. Query Tips for the LLM

### Time-Based Filtering
- **Always use explicit timestamp ranges** to avoid full table scans:
  ```sql
  WHERE dateTimeGenerated >= '2025-07-01' AND dateTimeGenerated < '2025-07-08'
  ```
- **Use interval functions** for relative time periods:
  ```sql
  WHERE dateTimeGenerated >= NOW() - INTERVAL '7 days'
  ```
- **Remember timezone**: All timestamps are UTC; convert to local time if needed

### Tag Filtering
- **Use LIKE or regex patterns** for tag matching:
  ```sql
  WHERE tagName LIKE 'pminc%-energy'  -- All energy meters
  WHERE tagName ~ '^pminc\d+-amp_(r|y|b)$'  -- All phase currents
  ```
- **Create tag groups** for complex queries:
  ```sql
  WHERE tagName IN ('pminc1-energy', 'pminc2-energy')
  ```

### Value Type Casting
- **Cast values appropriately** based on dataType:
  ```sql
  CAST(value AS DOUBLE PRECISION) WHERE dataType = 'Double'
  CAST(value AS INTEGER) WHERE dataType = 'Integer'
  ```

### Energy Consumption Calculation
- **For cumulative meters** (e.g., *-energy), use delta calculations:
  ```sql
  SELECT
    site,
    tagName,
    MAX(CAST(value AS DOUBLE PRECISION)) - MIN(CAST(value AS DOUBLE PRECISION)) as energy_consumed
  FROM table
  WHERE tagName LIKE '%energy'
    AND dateTimeGenerated BETWEEN start_time AND end_time
  GROUP BY site, tagName
  ```

### Temperature Differential (ΔT)
- **Join supply and return temperatures**:
  ```sql
  SELECT
    s.dateTimeGenerated,
    AVG(CAST(r.value AS DOUBLE PRECISION)) - AVG(CAST(s.value AS DOUBLE PRECISION)) as delta_t
  FROM table r
  JOIN table s ON
    r.site = s.site
    AND r.dateTimeGenerated = s.dateTimeGenerated
  WHERE r.tagName LIKE '%r_temp'
    AND s.tagName LIKE '%s_temp'
    AND r.tagName = REPLACE(s.tagName, 's_temp', 'r_temp')
  ```

### Aggregation Best Practices
- **Use time-bucket aggregations** for time-series data:
  ```sql
  SELECT
    DATE_TRUNC('hour', dateTimeGenerated) as hour,
    AVG(CAST(value AS DOUBLE PRECISION)) as avg_value
  GROUP BY hour
  ORDER BY hour
  ```

### Performance Optimization
- **Filter by site first** when analyzing single sites (if indexed)
- **Limit tag cardinality** using specific tag patterns rather than wildcards
- **Use materialized views** for frequently computed metrics (daily/hourly aggregates)
- **Consider partitioning** by dateTimeGenerated for large datasets

### Multi-Metric Analysis
- **Pivot tags to columns** for correlation analysis:
  ```sql
  SELECT
    dateTimeGenerated,
    MAX(CASE WHEN tagName = 'pminc1-pwr' THEN CAST(value AS DOUBLE PRECISION) END) as power,
    MAX(CASE WHEN tagName = 'pminc1-pf' THEN CAST(value AS DOUBLE PRECISION) END) as power_factor
  FROM table
  WHERE tagName IN ('pminc1-pwr', 'pminc1-pf')
  GROUP BY dateTimeGenerated
  ```

### Handling Data Gaps
- **Account for missing data** in time-series:
  ```sql
  -- Generate complete time series and left join to handle gaps
  SELECT time_bucket, COALESCE(avg_value, 0) as avg_value
  FROM time_series_generate(start, end, interval)
  LEFT JOIN aggregated_data USING (time_bucket)
  ```

---

## 9. Common Analysis Patterns

### Pattern 1: Period-over-Period Comparison
Compare current period to previous period (day, week, month):
```sql
WITH current_period AS (
  SELECT SUM(consumption) as current_value
  FROM ... WHERE dateTimeGenerated >= current_start
),
previous_period AS (
  SELECT SUM(consumption) as previous_value
  FROM ... WHERE dateTimeGenerated >= previous_start AND dateTimeGenerated < current_start
)
SELECT
  current_value,
  previous_value,
  (current_value - previous_value) / previous_value * 100 as percent_change
```

### Pattern 2: Peak Detection
Identify peak consumption times:
```sql
SELECT
  DATE_TRUNC('hour', dateTimeGenerated) as hour,
  MAX(CAST(value AS DOUBLE PRECISION)) as peak_value
WHERE tagName = 'pminc1-pwr'
GROUP BY hour
ORDER BY peak_value DESC
LIMIT 10
```

### Pattern 3: Equipment Efficiency
Calculate efficiency metrics:
```sql
-- Chiller efficiency: cooling output per power input
SELECT
  equipment_id,
  (flow * delta_t * 1.163) / power_consumption as efficiency_kwh_per_ton
FROM chiller_metrics
```

### Pattern 4: Anomaly Detection
Identify values outside normal ranges:
```sql
WITH stats AS (
  SELECT
    tagName,
    AVG(CAST(value AS DOUBLE PRECISION)) as mean,
    STDDEV(CAST(value AS DOUBLE PRECISION)) as stddev
  GROUP BY tagName
)
SELECT readings.*
FROM table readings
JOIN stats ON readings.tagName = stats.tagName
WHERE ABS(CAST(readings.value AS DOUBLE PRECISION) - stats.mean) > 3 * stats.stddev
```

---

## 10. Business Context

### Use Cases
1. **Energy Management**: Track and optimize facility energy consumption
2. **Cost Allocation**: Attribute energy costs to specific buildings/tenants
3. **Equipment Monitoring**: Track chiller, pump, and cooling tower performance
4. **Predictive Maintenance**: Identify equipment degradation through trend analysis
5. **Sustainability Reporting**: Calculate carbon footprint and ESG metrics
6. **Demand Response**: Optimize load during peak tariff periods
7. **Fault Detection**: Automated alerts for abnormal operating conditions

### Stakeholders
- **Facility Managers**: Daily operational monitoring
- **Energy Engineers**: Efficiency optimization and analysis
- **Finance**: Cost tracking and budget planning
- **Sustainability**: Carbon reporting and reduction initiatives
- **Maintenance**: Equipment health and preventive maintenance scheduling

### KPIs & Targets
- Energy consumption per square foot
- Chiller efficiency (kW/ton or COP)
- Power factor (target: >0.95)
- Equipment uptime percentage
- Peak demand reduction goals
- Energy cost per unit time
- Temperature setpoint compliance
- Phase balance (<10% deviation)

---

This datasource serves as the foundation for comprehensive building energy analytics, enabling data-driven decisions for operational efficiency, cost reduction, and sustainability goals across multi-site facility portfolios.
