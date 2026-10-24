Shared UI pieces. Owner: Area 4 only.

`components.css` holds the shared styles (page frame, header and navigation, buttons, fields, tabs, cards, tables, status pills with symbol and word, evidence meter, placeholder banner). Tokens only: `python scripts/check_design_tokens.py` fails on raw colours, sizes or radii.

Markup pattern for a status (always a symbol and a word):

```html
<span class="status status--ambiguous"><span class="status__symbol" aria-hidden="true"></span>Ambiguous</span>
```
