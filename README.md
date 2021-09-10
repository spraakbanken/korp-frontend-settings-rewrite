
TEMPORARY REPOSITORY

The purpose of this code is to take the configuration files in https://github.com/spraakbanken/korp-frontend-sb
and create new configuration files for the Korp frontend (https://github.com/spraakbanken/korp-frontend), while 
extracting the neccessary information for the new configuration backend.

Since the original files are Javascript, that will be evaluated with nodejs to extract information, the files must be
preprocessed to remove/change dependencies, such as a call to `new CorpusListing(corpora)` (of no interest to the
actual configuration).

main.py:
1. Copy the files from ../korp-frontend-sb (depends in the correct version being checkouted) into ./source/
2. preprocess.py:preprocess updates the Javascript using string replacement
3. node_eval/index.js run the files and does JSON.stringify on the `settings`-variable and writes to disk ./node_eval/result/<mode>.json
4. frontend.py:create creates new Javascript files for the frontend and puts them in `./result/frontend`
5. backend.py:create creates JSON-files for
  - modes (lists the corpora in each mode)
  - attributes (lists every attribute used in corpora, will be assigned new internal names sometimes)
  - corpora (same format as in the frontend before, just that attributes are referred to by name)

