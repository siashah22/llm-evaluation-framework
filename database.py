import sqlite3
import json
from datetime import datetime

DB_PATH = "eval_results.db"

def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
              CREATE TABLE IF NOT EXISTS runs(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  run_id TEXT NOT NULL,
                  model TEXT NOT NULL,
                  started_at TEXT NOT NULL,
                  completed_at TEXT,
                  total_cases INTEGER,
                  completed_cases INTEGER DEFAULT 0
                  )
            """)
    c.execute("""
              CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            model TEXT NOT NULL,
            test_case_id TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            question TEXT NOT NULL,
            generated_sql TEXT NOT NULL,
            expected_sql TEXT NOT NULL,
            faithfulness_score INTEGER,
            correctness_score INTEGER,
            efficiency_score INTEGER,
            hallucination_score INTEGER,
            total_score REAL,
            judge_reasoning TEXT,
            latency_ms INTEGER,
            created_at TEXT NOT NULL
                )
            """)
    conn.commit()
    conn.close()
    print("Database initialised.")
    
def save_run(run_id:str,model:str,total_cases:int):
    """Create a new evaluation run record."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
              INSERT INTO runs (run_id,model,started_at,total_cases)
              VALUES (?,?,?,?)
              """,(run_id,model,datetime.now().isoformat(),total_cases))
    conn.commit()
    conn.close()
    
def save_result(run_id:str,model:str,test_case:dict,generated_sql:str,scores:dict,latency_ms:int):
    """Save a single test case result."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
              INSERT INTO results (
                  run_id,model,test_case_id,difficulty,question,
                  generated_sql,expected_sql,
                  faithfulness_score,correctness_score,
                  efficiency_score,hallucination_score,total_score,
                  judge_reasoning,latency_ms,created_at)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (run_id,model,test_case["id"],test_case["difficulty"],
                   test_case["question"],generated_sql,test_case["expected_sql"],
                   scores["faithfulness"],scores["correctness"],
                   scores["efficiency"],scores["hallucination"],
                   scores["total"],scores["reasoning"],latency_ms,
                   datetime.now().isoformat()
                   ))
    conn.commit()
    conn.close()
    
def complete_run(run_id:str,completed_cases:int):
    """Marks a run as completed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
               "UPDATE runs SET completed_at = ? , completed_cases = ? WHERE run_id = ?",
               (datetime.now().isoformat(),completed_cases,run_id))
    conn.commit()
    conn.close()
    
def get_all_results()->list:
    """Fetch all results for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY created_at DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows    
    
def get_runs()->list:
    """Fetch all runs."""
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM runs ORDER BY started_at DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_model_summary()->list:
    """Aggregrate scores per model for comparison."""
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
              SELECT
            model,
            COUNT(*) as total_cases,
            ROUND(AVG(total_score), 2) as avg_total,
            ROUND(AVG(faithfulness_score), 2) as avg_faithfulness,
            ROUND(AVG(correctness_score), 2) as avg_correctness,
            ROUND(AVG(efficiency_score), 2) as avg_efficiency,
            ROUND(AVG(hallucination_score), 2) as avg_hallucination,
            ROUND(AVG(latency_ms), 0) as avg_latency_ms,
            SUM(CASE WHEN difficulty='easy' THEN 1 ELSE 0 END) as easy_count,
            ROUND(AVG(CASE WHEN difficulty='easy' THEN total_score END), 2) as easy_avg,
            ROUND(AVG(CASE WHEN difficulty='medium' THEN total_score END), 2) as medium_avg,
            ROUND(AVG(CASE WHEN difficulty='hard' THEN total_score END), 2) as hard_avg
        FROM results
        GROUP BY model
        ORDER BY avg_total DESC
          """)  
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print('Tables created. Ready to store results.')
         