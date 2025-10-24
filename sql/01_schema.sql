-- Create the 'countries' lookup table
CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(2) PRIMARY KEY,
    country_name VARCHAR(50) NOT NULL,
    zone_key VARCHAR(16) NOT NULL
);

-- Create the 'energy_production' table 
CREATE TABLE IF NOT EXISTS energy_production (
    production_id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL,
    time_stamp TIMESTAMP NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    production_mw DOUBLE PRECISION NOT NULL,
    UNIQUE (country_code, time_stamp, source_type)
);

-- Create the 'energy_consumption' table 
CREATE TABLE IF NOT EXISTS energy_consumption (
    consumption_id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL REFERENCES countries(country_code),
    time_stamp TIMESTAMP NOT NULL,
    consumption_mw DOUBLE PRECISION NOT NULL,
    UNIQUE (country_code, time_stamp)
);

-- Create the 'cross_border_flow' table 
CREATE TABLE IF NOT EXISTS cross_border_flow (
    flow_id SERIAL PRIMARY KEY,
    from_country_code VARCHAR(2) NOT NULL REFERENCES countries(country_code),
    to_country_code   VARCHAR(2) NOT NULL REFERENCES countries(country_code),
    time_stamp        TIMESTAMP NOT NULL,
    flow_mw           DOUBLE PRECISION NOT NULL,
    UNIQUE (from_country_code, to_country_code, time_stamp)
);

-- Insert countries
INSERT INTO countries (country_code, country_name, zone_key) VALUES
        ('FR', 'France', '10YFR-RTE------C'),
        ('DE', 'Germany', '10Y1001A1001A83F'),
        ('BE', 'Belgium', '10YBE----------2'),
        ('CH', 'Switzerland', '10YCH-SWISSGRIDZ'),
        ('ES', 'Spain', '10YES-REE------0'),
        ('NL', 'Netherlands', '10YNL----------L'),
        ('AT', 'Austria', '10YAT-APG------L'),
        ('CZ', 'Czech Republic', '10YCZ-CEPS-----N'),
        ('PL', 'Poland', '10YPL-AREA-----S')
ON CONFLICT (country_code) DO NOTHING;
