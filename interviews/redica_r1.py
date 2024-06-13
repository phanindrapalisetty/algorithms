#%% 

"""
Design a function solution that, given a string S consisting of N letters 'a' and/or 'b' returns True 
when all occurrences of letter 'a' are before all occurrences of letter 'b' and returns False otherwise.

aaaaabbbbb => True
aaaaabbbbaaaa => False


bbbb => True 
aaaa => False 

aaabbbccc => False 

aaaaaddd => True

1. Check if there is any a in the string.. 
2. If there is a, then the before element to the a is a or b. 
"""

input_ = 'aabbccdd'

map_dict = {
    'b': 'a',
    'c': 'b',
    'd': 'c'
}

def get_answer(input_:str):
    n = len(input_)
    res_ = True 

    if 'a' in input_:
        for i in range(1, n):
            if input_[i] == 'a' and input_[i-1] == 'b':
                return False 
        return True
    else:
        return True 

print(get_answer(input_))


"""
We have a table Teams with one column Names with 5 rows -
Team_Name
India       1
Pakistan    2
England     3
Srilanka    4
Australia   5
"""

"""
WITH _CTE AS (
SELECT *, ROW_NUMBER() OVER() as row_
) 

SELECT a.team_name, b.team_name
FROM _cte a 
LEFT JOIN _cte b 
ON a.row_ < b.row_ 


SELECT a.team_name, b.team_name
FROM tableA a 
LEFT JOIN tableA b 
ON a.team_name <> b.team_name 
"""



"""
Round #2
"""

"""
Tell me about the recent project: Document Digitization 

1. Stage 1: Organising the files {claimId}/files -- Downloading
                                        /images
                                        /ocr-results
                                        /predictions
                                        /annotations
2. 
"""

"""
C1, C2, C3, C4 -- tableA
"""

# Rows Which have C4 = 30

""" 
-- _tempTable --

""" 

"""
WITH _CTE AS (
SELECT C1 as C1_CTE, C2 as C2_CTE WHERE C4 = 30
),

_tempTable AS 
(
SELECT a.*, 
CASE 
    WHEN b.C1_CTE IS NULL and C4 = 30 THEN 'Case30'
    WHEN b.C1_CTE IS NULL and C4 <> 30 THEN 'NotCase30'
ELSE 'getMax' END as tag_
FROM tableA a
LEFT JOIN _CTE b 
ON a.C1=b.C1_CTE and a.C2 = b.C2_CTE
)
"""

"""
SELECT *,
CASE WHEN tag_ = 'Case30' THEN 'Y'
WHEN tag_ = 'getMax' and row_ = 1 THEN 'Y' 
ELSE 'N' END AS tag_2
FROM (
SELECT *, ROW_NUMBER() OVER(PARTITION BY C1, c2 ORDER BY C4 DESC) as row_
FROM _tempTable
) temp_
WHERE tag_2 = 'Y'
"""


#Approach #2
"""
WITH _CTE AS (
SELECT C1 as C1_CTE, C2 as C2_CTE WHERE C4 = 30
),

_tempTable AS 
(
SELECT a.*, b.C1_CTE, ROW_NUMBER() OVER(PARTITION BY C1, c2 ORDER BY C4 DESC) as row_
FROM tableA a
LEFT JOIN _CTE b 
ON a.C1=b.C1_CTE and a.C2 = b.C2_CTE
"""


"""
SELECT * FROM _tempTable WHERE C1_CTE is NOT NULL AND C4 = 30 
UNION 
SELECT * FROM _tempTable WHERE C1_CTE is NULL AND row_ = 1
"""