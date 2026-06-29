import time
import uuid
from groq import Groq
from dotenv import load_dotenv
from test_cases import TEST_CASES
from evaluator import evaluate
from database import init_db, save_run, save_result, complete_run

load_dotenv()

client = Groq()

MODELS = [
    "qwen/qwen3-32b",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
]

SQL_PROMPT = """You are an expert SQL developer. Generate a SQL query for the following:
Schema: {schema}
Question: {question}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks
- Use only the tables and columns mentioned in the schema
- Write clean, efficient SQL
"""

def get_sql(model: str, test_case: dict) -> tuple[str, int]:
    """
    Ask a model to generate SQL for a test case.
    Returns (generated_sql, latency_ms)
    """
    prompt = SQL_PROMPT.format(
        schema = test_case["schema"],
        question = test_case["question"]
    )
    
    start = time.time()
    response = client.chat.completions.create(
        model = model,
        messages = [{"role": "user", "content": prompt}],
        temperature = 0,
        max_tokens = 300
    )
    latency_ms = int((time.time() - start)*1000)
    sql =  response.choices[0].message.content.strip()
    if "<think>" in sql :
        if "</think>" in sql :
            sql = sql.split("</think>")[-1].strip()
        else:
            lines = [l.strip() for l in sql.split("\n") if l.strip()]
            sql = lines[-1] if lines else sql
    if "```" in sql:
        lines = sql.split("\n")
        sql = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()
    return sql, latency_ms

def run_model(model: str):
    run_id = str(uuid.uuid4())[:8]
    total = len(TEST_CASES)
    
    print(f"Evaluating: {model}")
    print(f" Run ID: {run_id} | Test cases: {total}")
    
    save_run(run_id,model,total)
    
    passed = 0
    total_score=0
    
    for i, test_case in enumerate(TEST_CASES,1):
        print(f"\n[{i}/{total}] {test_case['id']} ({test_case['difficulty']})")
        print(f" Q: {test_case['question']}")
        
        try:
            generated_sql, latency_ms = get_sql(model, test_case)
            print(f" Generated: {generated_sql[:80]}{'...' if len(generated_sql)>80 else ''}")
            print(f" Latency: {latency_ms}ms")
            
            scores = evaluate(test_case, generated_sql)
            print(f" Scores-> Correctness: {scores['correctness']} |"
                  f"Faithfulness: {scores['faithfulness']} |"
                  f"Efficieny: {scores['efficiency']} |"
                  f"Hallucination: {scores['hallucination']} |"
                  f"Total: {scores['total']}")
            print(f" Reasoning: {scores['reasoning']}")
            
            save_result(run_id, model, test_case, generated_sql, scores, latency_ms)
            total_score += scores["total"]
            passed +=1
            
        except Exception as e:
            print(f" Error: {e}")
        
        time.sleep(0.5)
        
    avg_score = round(total_score/passed,2) if passed > 0 else 0
    complete_run(run_id, passed)
    
    print(f"{model} complete")
    print(f" Cases: {passed}/{total} | Average Score: {avg_score}/5.0")
    
    return avg_score

def run_all():
    init_db()
    print("\nLLM Evaluation Framework - SQL Generation Benchmark")
    print(f" Models: {', '.join(MODELS)}")
    print(f" Test cases: {len(TEST_CASES)}")
    
    results = {}
    for model in MODELS :
        avg = run_model(model)
        results[model] = avg
        
    print("\nFINAL RESULTS")
    for model, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(score * 4) + "░" * (20 - int(score * 4))
        print(f"{model.split('/')[-1]:<35} {bar} {score}/5.0")
        
if __name__ == "__main__":
    run_all()
        