CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrower_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    annual_income DOUBLE PRECISION NOT NULL,
    credit_score INTEGER NOT NULL,
    monthly_debts DOUBLE PRECISION NOT NULL,
    assets DOUBLE PRECISION NOT NULL,
    loan_amount DOUBLE PRECISION NOT NULL,
    down_payment DOUBLE PRECISION NOT NULL,
    property_value DOUBLE PRECISION NOT NULL,
    credit_used DOUBLE PRECISION NOT NULL DEFAULT 0,
    credit_limit DOUBLE PRECISION NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    borrower_profile_id INTEGER NOT NULL REFERENCES borrower_profiles(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    raw_text TEXT NOT NULL,
    extracted_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_metrics (
    id SERIAL PRIMARY KEY,
    borrower_profile_id INTEGER NOT NULL REFERENCES borrower_profiles(id) ON DELETE CASCADE,
    dti DOUBLE PRECISION NOT NULL,
    ltv DOUBLE PRECISION NOT NULL,
    credit_utilization DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_band VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_decisions (
    id SERIAL PRIMARY KEY,
    borrower_profile_id INTEGER NOT NULL REFERENCES borrower_profiles(id) ON DELETE CASCADE,
    financial_metrics_id INTEGER NOT NULL REFERENCES financial_metrics(id) ON DELETE CASCADE,
    decision VARCHAR(50) NOT NULL,
    risk_category VARCHAR(50) NOT NULL,
    approval_probability DOUBLE PRECISION NOT NULL,
    explanation TEXT NOT NULL,
    reasoning_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_scenarios (
    id SERIAL PRIMARY KEY,
    borrower_profile_id INTEGER NOT NULL REFERENCES borrower_profiles(id) ON DELETE CASCADE,
    scenario_name VARCHAR(120) NOT NULL,
    input_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
