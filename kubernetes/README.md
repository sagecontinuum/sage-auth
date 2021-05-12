

# MySQL


connect to your MySQL and specify password for new user:

```bash
CREATE USER 'sage-auth'@'%' identified by '<NEW_USER_PASSWORD>';
GRANT ALL PRIVILEGES ON SAGEDB.* TO 'sage-auth'@'%';
exit
```