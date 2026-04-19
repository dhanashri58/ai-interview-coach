% Facts: question(ID, Topic, Difficulty, QuestionText)
question(1, python, beginner, 'What is a list in Python?').
question(2, python, beginner, 'Difference between tuple and list?').
question(4, python, intermediate, 'Explain decorators with example.').
question(6, python, advanced, 'Explain generators and yield keyword.').
question(7, sql, beginner, 'What is SQL and its command types?').
question(9, sql, intermediate, 'Explain different types of JOINs.').
question(10, dsa, beginner, 'What is an array? Explain time complexity.').
question(11, dsa, intermediate, 'Explain binary search algorithm.').
question(201, java, beginner, 'What is JVM and how does it provide platform independence?').
question(202, java, beginner, 'What are the core principles of OOP in Java?').

% Facts: keyword(QuestionID, Keyword)
keyword(1, mutable). keyword(1, ordered). keyword(1, sequence). keyword(1, collection).
keyword(2, immutable). keyword(2, faster). keyword(2, mutable).
keyword(4, wrapper). keyword(4, function). keyword(4, modify).
keyword(6, yield). keyword(6, iterator). keyword(6, lazy).
keyword(7, ddl). keyword(7, dml). keyword(7, query).
keyword(201, bytecode). keyword(201, platfrom). keyword(201, virtual).
keyword(202, inheritance). keyword(202, polymorphism). keyword(202, encapsulation).

% Facts: concept(QuestionID, Concept)
concept(1, indexing). concept(1, slicing). concept(1, mutable).
concept(2, immutability). concept(2, performace).
concept(201, architecture).

% Rules:
% A question is "easy" if it's beginner AND has <= 3 concepts
easy_question(ID) :- question(ID, _, beginner, _), 
                     findall(C, concept(ID, C), Cs), length(Cs, N), N =< 3.

% A question matches a role
matches_role(ID, 'Software Engineer') :- question(ID, python, _, _).
matches_role(ID, 'Software Engineer') :- question(ID, dsa, _, _).
matches_role(ID, 'Software Engineer') :- question(ID, java, _, _).
matches_role(ID, 'Data Scientist') :- question(ID, sql, _, _).
matches_role(ID, 'Data Scientist') :- question(ID, python, _, _).
matches_role(ID, 'Backend Developer') :- question(ID, java, _, _).
matches_role(ID, 'Backend Developer') :- question(ID, sql, _, _).

% Answer quality rules
good_answer(QID, Answer) :- 
    keyword(QID, KW), 
    sub_atom(Answer, _, _, _, KW).

% Recommend next topic based on weak score
recommend_topic(python, sql) :- true.
recommend_topic(sql, dsa) :- true.
recommend_topic(dsa, java) :- true.
recommend_topic(java, python) :- true.
