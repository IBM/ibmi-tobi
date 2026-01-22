# Documentation

All the documentations for TOBi can be found in the root level `docs` directory. The documentation site is generated using [docsify](https://docsify.js.org/).



## Running Docs

<!-- tabs:start -->

#### **docsify-cli**

It is recommended to use `docsify-cli` to preview the documentation locally.

```bash
npm i docsify-cli -g
```

Once you have `docsify-cli` installed, run the following command to serve the documentation website.

```bash
docsify serve docs
```

#### **Manually Preview**

Run the following command to host the documentation website using Python's builtin HTTP Server

```bash
# For Python 2
cd docs && python -m SimpleHTTPServer 3000
```

```bash
# For Python 3
cd docs && python -m http.server 3000
```

<!-- tabs:end -->

Now the documentation is accessible on http://localhost:3000