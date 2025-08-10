---
description: Commit and push changes to the repository
allowed-tools: [git]
---

# Commit and Push Changes
This document provides instructions for committing and pushing changes to the EchoFlow repository.

## Commit Changes
1. **Stage Changes**: Use `git add` to stage the files you want to commit.
   ```bash
   git add <file1> <file2> ...
   ``` 

2. **Commit Changes**: Use `git commit` with a clear and concise commit message.
   ```bash
   git commit -m "Brief description of changes made"
   ```

3. **Check Commit**: Verify your commit with `git log` to ensure it has been recorded correctly.
   ```bash
   git log --oneline
   ```

## Push Changes
1. **Push to Remote**: Use `git push` to push your changes to the remote repository.
   ```bash
   git push origin <branch-name>
   ```
2. **Verify Push**: Check the remote repository (e.g., on GitHub) to confirm that your changes have been successfully pushed.

