# Git Repo Management 


## Issues related to .gitignore
- Ensure target file or file type is located within the gitignore
- On the local repo remove the file from the repo cache
```
git rm --cached config.ini
```
- (OPTIONAL) Make sure there is still a template file available if needed that can remain the same on all machines.
```
cp config.ini config.ini.example
```
- (OPTIONAL) add and commit the config.ini.example
- Clear cache and commit changes
```
git rm -r --cached .
git add .
git commit -m "Updated .gitignore and removed files from tracking"
```
- Push changes to remote 
```
git push origin
```

## If .gitignore already has been implemented
- Make note of the config file or other dynamic files in the local repo and then delete and clone the repo.
- After cloning proceed to edit the config file. The ability to commit changes should not be possible at this point.