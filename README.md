# Setup instructions 

- Initialize and activate a Python 3.9 virtualenv, e.g.:
```
python3.9 -m venv .venv
. .venv/bin/activate
```
- Install packages in `requirements.txt`
- Install CoreNLP:  
```
import stanza
stanza.install_corenlp()
```


