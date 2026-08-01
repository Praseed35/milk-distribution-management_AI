select * from users;

select * from subscriptions;

select * from customers;

select * from milk_types

select * from employees;

select * from routes;

select * from delivery_exceptions;

select * from token_book_issues;

select * from token_identities;

update token_book_issues SET status = 'ACTIVE' WHERE customer_id = 2;