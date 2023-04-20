#! /bin/bash

cp environment.yml environment.yml~
conda env export --from-history | sed '$ d' > environment.yml
