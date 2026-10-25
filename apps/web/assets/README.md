# apps/web/assets

Bundled CSS, JavaScript and fonts. Nothing loads from a CDN; everything works offline. Owner: Area 4 (Hardik).

| File | Purpose |
|---|---|
| `design-tokens.css` | The one tokens file: colours (light and dark), status colours with their symbol and word, spacing, type scale, radii, layout, focus, shadow, motion |
| `fonts.css` | `@font-face` rules for the bundled fonts |
| `fonts/` | Noto Sans (Latin), Noto Sans Devanagari, Noto Sans Kannada, regular and bold, as woff2, with the SIL Open Font License text |

## Use the tokens

Load `fonts.css`, then `design-tokens.css`, then your screen's own CSS file. Read values only through `var(--name)`:

```css
.deal-row {
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  font: var(--font-weight-regular) var(--font-size-base) / var(--line-height-normal) var(--font-body);
}
```

Rules:
1. No raw colours (hex, rgb, hsl, named), font sizes, font families or radii in screen CSS or HTML. Add a token here instead, in the same pull request, with the dark value as well.
2. Every status shows a symbol and a word, never colour alone: put the word in the markup and the symbol with `::before { content: var(--status-clear-symbol); }`. Statuses: clear, ambiguous, missing, conflict.
3. Themes: light by default; dark follows the system. Force one with `<html data-theme="light">` or `<html data-theme="dark">`.
4. Text in Hindi or Kannada uses `line-height: var(--line-height-indic)`.
5. Sizes are in rem, so the page works at 200% zoom.
6. One CSS file per screen, in the screen's own folder.

Check: `python scripts/check_design_tokens.py` (also runs in pre-commit and CI). Tests: `apps/web/tests/` check the tokens, contrast (WCAG AA) and the fonts.

## Fonts

Source: Fontsource packages `@fontsource/noto-sans`, `@fontsource/noto-sans-devanagari`, `@fontsource/noto-sans-kannada` v5.3.0 (SIL OFL 1.1). Latin, Devanagari and Kannada subsets only. The rupee sign is served by the Devanagari and Kannada files. Status symbols come from the system symbol font.
