import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client=Groq()

JUDGE_MODEL =  "llama-3.3-70b-versatile"
JUDGE_PROMPT = """
                You are an expert SQL evaluator.
                Your job is to score a generated SQL query against an expexted SQL query
                
                Schema: {schema}
                Question: {question}
                Expected SQL: {expected_sql}
                Generated SQL: {generated_sql}
                
                Score the generated SQL on these 4 dimensions. Each score is 1-5:
                
                1. CORRECTNESS (1-5): Does the generated SQL produce the correct result ?
                   5 = Perfectly correct, identical logic to expected
                   4 = Correct result but minor differences (alias names, formatting)
                   3 = Mostly correct but missing one clause or condition
                   2 = Partially correct, gets some of it right
                   1 = Completely wrong or would produce wrong results
                   
                2. FAITHFULNESS (1-5): Does it only use tables/columns mentioned in the schema ?
                   5 = Only uses schema elements, no hallucinated columns/tables
                   3 = Mostly faithful, minor deviation
                   1 = References tables or columns not in the schema
                   
                3. EFFICIENCY (1-5): Is the query well-written and efficient ?
                   5 = Optimal approach, clean and readable
                   4 = Good but could be slightly improved
                   3 = Works but has unnecessary complexity
                   2 = Overly complex for the task
                   1 = Very inefficient or unreadable
                   
                4. HALLUCINATION (1-5): Inverse hallucination score - higher means less hallucination
                   5 = No made-up columns, functions, or logic
                   3 = Minor hallucination (wrong function name, invented alias)
                   1 = Major hallucination (invented tables, completely fabricated logic)
                   
                Respond ONLY with a JSON object in this exact format, nothing else:
                {{
                    "correctness": <1-5>,
                    "faithfulness": <1-5>,
                    "efficiency" : <1-5>,
                    "hallucination": <1-5>,
                    "reasoning" : "<one sentence explaining the score>"
                }}
                   """
                   
def evaluate(test_case: dict, generated_sql: str)->dict:
   """
   Use the judge LLM to score a generated SQL query.
   Returns a dict with all 4 scores + total + reasoning
   """
   prompt = JUDGE_PROMPT.format(
      schema = test_case["schema"],
      question = test_case["question"],
      expected_sql = test_case["expected_sql"],
      generated_sql = generated_sql
   )
   
   try:
      response = client.chat.completions.create(
         model = JUDGE_MODEL,
         messages = [{"role": "user","content": prompt}],
         temperature = 0,
         max_tokens = 300 
      )
      raw = response.choices[0].message.content.strip()
      raw = re.sub(r"```json|```", "", raw).strip()
      scores = json.loads(raw)
      
      required = ["correctness","faithfulness","efficiency","hallucination","reasoning"]
      for key in required:
         if key not in scores:
            raise ValueError(f"Missing key: {key}")
         
      for key in ["correctness","faithfulness","efficiency","hallucination"]:
         scores[key]=max(1,min(5, int(scores[key])))
      
      scores["total"]=round(
         scores["correctness"]*0.4 +
         scores["faithfulness"]*0.2 +
         scores["efficiency"]*0.2 +
         scores["hallucination"]*0.2,
         2
      )
      return scores
   
   except Exception as e:
      print(f"Judge error: {e} - using default scores")
      return{
         "correctness":1,
         "faithfulness":1,
         "efficiency":1,
         "hallucination":1,
         "total":1.0,
         "reasoning":f"Judge failed: {str(e)}"
      }
      
if __name__ == "__main__":
   test_case = {
      "schema": "Table: users(id,name,email,age,city)",
      "question": "Get all users from Mumbai.",
      "expected_sql": "SELECT * FROM users WHERE city = 'Mumbai';"
   }
   
   generated = "SELECT * FROM users WHERE city = 'Mumbai';"
   scores = evaluate(test_case,generated)
   print("\nPerfect answer scores:")
   print(scores)
   
   generated_bad = "SELECT name FROM customers WHERE location = 'Mumbai';"
   scores_bad = evaluate(test_case,generated_bad)
   print("\nBad answer scores:")
   print(scores_bad)
   