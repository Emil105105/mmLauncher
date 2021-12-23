#!/usr/bin/env python3

# ^^ Linux-executable init

# ### LEGAL ###

# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org/>

import json
import sys
import subprocess
import base64
import os
from ast import literal_eval

try:
    from Crypto.Hash import SHA3_256
    from Crypto.Random import random
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
    from Crypto.Hash import SHA3_256
    from Crypto.Random import random


def create_signature(message, private_key):
    signature = pow(message, private_key[0], private_key[1])
    return signature


def get_files(subdir):
    r = {}
    path = os.path.join(os.getcwd(), subdir)
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        if os.path.isfile(f):
            with open(f, 'rb') as x:
                r[filename] = base64.urlsafe_b64encode(x.read()).decode()
    return r


def create_package(rsa, info, subdir, output):
    files = get_files(subdir)
    signed_hashes = {}
    for i in files:
        h = SHA3_256.new()
        h.update(files[i].encode())
        n = int(h.hexdigest(), 16)
        signed_hashes[i] = hex(create_signature(n, [rsa[1], rsa[2]]))
    r = {'name': info['name'],
         'author': info['author'],
         'description': info['description'],
         'public_keys': [rsa[0], rsa[2]],
         'files': files,
         'signature': signed_hashes}
    with open(output + '.mmp', 'w') as f:
        json.dump(r, f, indent=4)


def main():
    info = {'name': input('Name of package: '),
            'author': input('Author: '),
            'description': input('Description: ')}
    with open('rsa.list', 'r') as f:
        rsa = literal_eval(f.read())
    subdir = input('Subdir: ')
    output = input('Output file [without extension]: ')
    create_package(rsa, info, subdir, output)


if __name__ == '__main__':
    main()
