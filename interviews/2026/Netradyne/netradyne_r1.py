You are given a 0-indexed binary string array bank representing the floor plan of the bank, which is an m x n 2D matrix. bank[i] represents the ith row, consisting of '0's and '1's. '0' means the cell is empty, while'1' means the cell has a security device.
There is one laser beam between any two security devices if both conditions are met:
The two devices are located on two different rows: r1 and r2, where r1 < r2.
For each row i where r1 < i < r2, there are no security devices in the ith row.
Laser beams are independent, i.e., one beam does not interfere nor join with another.
Return the total number of laser beams in the bank.
 
Input: bank = ["011001",
			"000000",
			"010100",
			"001000"]
Output: 8


"011001",
"000000",
"000000",
"010100",
"001000", 



3
0
2
1


(3*2) + (2*1) + (1*0)

# m: number of rows
# n: number of cell in each row

_input = ["011001","000000", "010100", "001000"]


def _function_name(_bank): 
	bank_ones = []
	
	for i in _bank: 
		_counter = 0 
			for _cell in i: 
				if int(_cell) == 1: 
					_count += 1

			if _counter > 0:
				bank_ones.append(_counter)

	## _counter is updated fully
	## bank_ones = [3, 2, 1] 
	_return = 0

	for i in range(0, len(bank_ones-1)): 
		_return += bank_ones[i]*bank_ones[i+1]
	return _return 



def _function_name(_bank): 
	bank_ones = []
	_prev = 0
	_return = 0
	
	for i in _bank: 
		_counter = 0 
			for _cell in i: 
				if int(_cell) == 1: 
					_count += 1

			if _counter > 0:
				_return += _prev*_counter
				_prev = _counter

	return _return 



"""
SQL Query: 

employees: emp_id, emp_name, salary, doj


with _max_sal as (
	SELECT max(salary) as max_salary FROM employees 
)

SELECT emp_name
FROM employees 
INNER JOIN _max_sal ON salary = max_salary
ORDER BY doj DESC 
LIMIT 1



with _ranking as (
	SELECT emp_id, emp_name, salary, doj, 
		rank() OVER (ORDER BY salary DESC) as _rnk 
)

SELECT emp_name FROM _ranking WHERE _rnk = 3

"""

"""
10000-1
10000-1
10000-1
9000-2
8000-3
7000-4
7000-4
7000-4



Scene: 12000 req/sec
OLTP: Postgres


1. Query is slow: 
 - Query based on primary keys 
 - If there are joins, join based on PK_FK 
 - Get on the columns needed, don't use SELECT * directly
 - PK is already indexed
 - FK is properly constrained

Data in DB - Process in a MS-1 - Now I have processed data per request with MS-1 -> MS-2
SQS with DLQ
SNS - configure the topic - SQS

Query - Process - Queue
Autoscaling
Caching
Async processing
"""

	