TEST_CASES = [
    # EASY
    {
        "id":"sql_001",
        "difficulty":"easy",
        "schema":"Table: users(id,name,email,age,city)",
        "question":"Get all users from Mumbai.",
        "expected_sql":"SELECT * FROM users WHERE city='Mumbai';",
        "expected_concepts":["SELECT","WHERE"]
    },
    {
        "id":"sql_002",
        "difficulty":"easy",
        "schema":"Table: products(id,name,price,category,stock)",
        "question":"Get the names and prices of all products under 500 rupees.",
        "expected_sql":"SELECT name,price FROM products WHERE price < 500;",
        "expected_concepts":["SELECT specific columns","WHERE"]
    },
    {
        "id":"sql_003",
        "difficulty":"easy",
        "schema":"Table: orders(id,customer_id,amount,status,created_at)",
        "question":"Count the total number of orders.",
        "expected_sql":"SELECT COUNT(*) FROM orders;",
        "expected_concept":["COUNT","aggregate"],
    },
    {
        "id":"sql_004",
        "difficulty":"easy",
        "schema":"Table: employees(id,name,department,salary,hire_date)",
        "question":"Get all employees sorted by salary from highest to lowest.",
        "expected_sql":"SELECT * FROM employees ORDER BY salary DESC;",
        "expected_concept":["ORDER BY","DESC"]
    },
    {
        "id":"sql_005",
        "difficulty":"easy",
        "schema":"Table: students(id,name,grade,score,subject)",
        "question":"Get the top 5 students by score.",
        "expected_sql":"SELECT * FROM students ORDER BY marks DESC LIMIT 5;",
        "expected_concepts":["ORDER BY","LIMIT"]
    },
    # MEDIUM
    {
        "id":"sql_006",
        "difficulty":"medium",
        "schema":"Table: orders(id,customer_id,amount,status,created_at)",
        "question":"Get the total revenue per status (pending,completed,cancelled).",
        "expected_sql":"SELECT status, SUM(amount) as total_revenue FROM orders GROUP BY status;",
        "expected_concept":["GROUP BY","SUM","alias"]
    },
    {
        "id":"sql_007",
        "difficulty": "medium",
        "schema": "Table: employees (id, name, department, salary, hire_date)",
        "question": "Get the average salary per department, only for departments where average salary exceeds 50000.",
        "expected_sql": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department HAVING AVG(salary) > 50000;",
        "expected_concepts": ["GROUP BY", "HAVING", "AVG"]
    },
    {
        "id": "sql_008",
        "difficulty": "medium",
        "schema": "Tables: orders (id, customer_id, amount), customers (id, name, email, city)",
        "question": "Get the name and total spending of each customer.",
        "expected_sql": "SELECT c.name, SUM(o.amount) as total_spent FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.name;",
        "expected_concepts": ["JOIN", "GROUP BY", "SUM"]
    },
    {
        "id": "sql_009",
        "difficulty": "medium",
        "schema": "Table: products (id, name, price, category, stock)",
        "question": "Get the most expensive product in each category.",
        "expected_sql": "SELECT category, name, MAX(price) as max_price FROM products GROUP BY category;",
        "expected_concepts": ["GROUP BY", "MAX"]
    },
    {
        "id": "sql_010",
        "difficulty": "medium",
        "schema": "Table: employees (id, name, department, salary, manager_id)",
        "question": "Get all employees who earn more than the average salary.",
        "expected_sql": "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);",
        "expected_concepts": ["subquery", "AVG", "WHERE"]
    },
    {
        "id": "sql_011",
        "difficulty": "medium",
        "schema": "Table: orders (id, customer_id, amount, created_at)",
        "question": "Get total revenue for each month in 2024.",
        "expected_sql": "SELECT MONTH(created_at) as month, SUM(amount) as revenue FROM orders WHERE YEAR(created_at) = 2024 GROUP BY MONTH(created_at);",
        "expected_concepts": ["date functions", "GROUP BY", "SUM"]
    },
    {
        "id": "sql_012",
        "difficulty": "medium",
        "schema": "Tables: students (id, name), scores (id, student_id, subject, score)",
        "question": "Get students who scored above 90 in at least one subject.",
        "expected_sql": "SELECT DISTINCT s.name FROM students s JOIN scores sc ON s.id = sc.student_id WHERE sc.score > 90;",
        "expected_concepts": ["JOIN", "DISTINCT", "WHERE"]
    },
    # HARD
    {
        "id": "sql_013",
        "difficulty": "hard",
        "schema": "Tables: orders (id, customer_id, amount, created_at), customers (id, name, city)",
        "question": "Get the top 3 customers by total spending in the last 30 days.",
        "expected_sql": "SELECT c.name, SUM(o.amount) as total FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY c.id, c.name ORDER BY total DESC LIMIT 3;",
        "expected_concepts": ["JOIN", "date filter", "GROUP BY", "ORDER BY", "LIMIT"]
    },
    {
        "id": "sql_014",
        "difficulty": "hard",
        "schema": "Table: employees (id, name, department, salary, manager_id)",
        "question": "Get each employee's name, salary, and how their salary compares to their department average.",
        "expected_sql": "SELECT name, salary, department, AVG(salary) OVER (PARTITION BY department) as dept_avg, salary - AVG(salary) OVER (PARTITION BY department) as diff_from_avg FROM employees;",
        "expected_concepts": ["window function", "PARTITION BY", "AVG OVER"]
    },
    {
        "id": "sql_015",
        "difficulty": "hard",
        "schema": "Tables: products (id, name, category), order_items (id, order_id, product_id, quantity, price)",
        "question": "Get the second best-selling product by total quantity sold.",
        "expected_sql": "SELECT p.name, SUM(oi.quantity) as total_sold FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id, p.name ORDER BY total_sold DESC LIMIT 1 OFFSET 1;",
        "expected_concepts": ["JOIN", "GROUP BY", "OFFSET", "ORDER BY"]
    },
    {
        "id": "sql_016",
        "difficulty": "hard",
        "schema": "Table: orders (id, customer_id, amount, created_at)",
        "question": "Get customers who placed orders in January 2024 but not in February 2024.",
        "expected_sql": "SELECT DISTINCT customer_id FROM orders WHERE MONTH(created_at) = 1 AND YEAR(created_at) = 2024 AND customer_id NOT IN (SELECT customer_id FROM orders WHERE MONTH(created_at) = 2 AND YEAR(created_at) = 2024);",
        "expected_concepts": ["NOT IN", "subquery", "date filter", "DISTINCT"]
    },
    {
        "id": "sql_017",
        "difficulty": "hard",
        "schema": "Tables: employees (id, name, manager_id)",
        "question": "Get all employees and their manager's name. Include employees with no manager.",
        "expected_sql": "SELECT e.name as employee, m.name as manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id;",
        "expected_concepts": ["self JOIN", "LEFT JOIN", "NULL handling"]
    },
    {
        "id": "sql_018",
        "difficulty": "hard",
        "schema": "Table: transactions (id, user_id, amount, type, created_at) where type is 'credit' or 'debit'",
        "question": "Get the running balance for each user ordered by date.",
        "expected_sql": "SELECT user_id, created_at, amount, type, SUM(CASE WHEN type='credit' THEN amount ELSE -amount END) OVER (PARTITION BY user_id ORDER BY created_at) as running_balance FROM transactions;",
        "expected_concepts": ["window function", "CASE WHEN", "running total", "PARTITION BY"]
    },
    {
        "id": "sql_019",
        "difficulty": "hard",
        "schema": "Tables: courses (id, name), enrollments (id, student_id, course_id), students (id, name)",
        "question": "Get students enrolled in ALL available courses.",
        "expected_sql": "SELECT s.name FROM students s WHERE NOT EXISTS (SELECT c.id FROM courses c WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.id AND e.course_id = c.id));",
        "expected_concepts": ["NOT EXISTS", "correlated subquery", "relational division"]
    },
    {
        "id": "sql_020",
        "difficulty": "hard",
        "schema": "Table: sales (id, product_id, amount, sale_date)",
        "question": "For each product, get the month with highest sales and the month with lowest sales.",
        "expected_sql": "WITH monthly AS (SELECT product_id, MONTH(sale_date) as month, SUM(amount) as total FROM sales GROUP BY product_id, MONTH(sale_date)) SELECT product_id, MAX(CASE WHEN total = max_total THEN month END) as best_month, MAX(CASE WHEN total = min_total THEN month END) as worst_month FROM (SELECT m.*, MAX(total) OVER (PARTITION BY product_id) as max_total, MIN(total) OVER (PARTITION BY product_id) as min_total FROM monthly m) t GROUP BY product_id;",
        "expected_concepts": ["CTE", "window function", "CASE WHEN", "MIN MAX"]
    },
]

if __name__ == "__main__":
    easy = [t for t in TEST_CASES if t["difficulty"]=="easy"]
    medium = [t for t in TEST_CASES if t["difficulty"]=="medium"]
    hard = [t for t in TEST_CASES if t["difficulty"]=="hard"]
    print(f"Total: {len(TEST_CASES)} test cases")
    print(f"Easy: {len(easy)} | Medium: {len(medium)} | Hard: {len(hard)}")
    