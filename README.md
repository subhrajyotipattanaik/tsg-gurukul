# TSG Gurukul website

This archive includes the editable page generator, school content and data, and the complete static site in `dist/`.

## Preview locally

From the extracted `tsg-gurukul` directory, start a local server with Python 3.

```sh
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000/ in your browser. Serve `dist/` as the web root so page and asset paths work.

## Edit and rebuild

- `school_copy.py` contains the page and blog copy.
- `school-data.json` contains published fees, gallery entries, and other structured content.
- `build.py` generates the HTML pages and search index.
- `dist/assets/site.css` and `dist/assets/site.js` contain the styling, animation, and interactions.

Run `python3 build.py` from the project directory after changing the page source. The prebuilt `dist/` folder can also be deployed directly to a static web host. Videos, some official documents, and form submissions use the school’s original website.
