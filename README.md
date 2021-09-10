
TEMPORARY REPOSITORY

The purpose of this code is to take the configuration files in https://github.com/spraakbanken/korp-frontend-sb
and create new configuration files for the Korp frontend (https://github.com/spraakbanken/korp-frontend), while 
extracting the neccessary information for the new configuration backend.

Since the original files are Javascript, that will be evaluated with nodejs to extract information, the files must be
preprocessed to remove/change dependencies, such as a call to `new CorpusListing(corpora)` (of no interest to the
actual configuration).

main.py does this:
1. Copy the files from ../korp-frontend-sb (depends in the correct version being checkouted) into ./source/
2. preprocess.py:preprocess updates the Javascript config using string replacement (so that files are executable).
3. node_eval/index.js run the files and does JSON.stringify on the `settings`-variable and writes to disk ./node_eval/result/<mode>.json
4. ...
5. PROFIT!!!
