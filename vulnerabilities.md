# Fixed Vulnerabilities

## Company News

- Had XSS vulnerabilities
- Internal news was publicly accessible
- Internal news leaked secret keys

## Notes App

- Had access control vulnerabilities:
  - Allowed any user to view each others notes
  - Allowed any user to delete each other's notes
- Had information disclosure vulnerabilities:
  - Non-Admins could access the debug route
- Had an SQL injection vulnerability when searching notes
- Had XSS vulnerabilities
- Failed to enforce max content lengths

## Document Upload

- Failed to validate file types
- Max file sizes weren't enforced

## Admin Portal

- Had an SQL injection vulnerability when logging in
- Had XSS vulnerabilities
- Default admin credentials were hard coded

## 401(k) Portal

- Had a race condition
- Not stored in database

## General

- Flask secret key was hard coded
