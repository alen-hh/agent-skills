---
name: html-prototype
description: >-
  Builds a minimal static HTML prototype of a product screen for product-manager
  review. Use whenever someone asks for a prototype, wireframe, mockup, HTML
  mock, 原型, or 线框图, or describes a product screen they want to see quickly
  — settings, lists, dashboards, forms, dialogs, empty states — even if they
  never say HTML. The page is one self-contained file, content max-width 1440px
  and vertically centered, black white and gray only plus success, info,
  warning, and danger status colors, and standard actions are icons rather than
  words. Skip this for production apps, component libraries, Bootstrap styling,
  and branded marketing sites.
---

# HTML Prototype

Build a static product-screen prototype a product manager can open and review. The page should be understandable in one glance and contain nothing that is only there to look finished.

Copy [assets/page.html](assets/page.html) as the document. Keep its shell, tokens, and the rule that disables animation. Put screen-specific CSS in the same `<style>` block. Icons come from Lucide. Read [references/icons.md](references/icons.md) and copy those SVGs. Do not draw a new icon when Lucide already has one.

## Output

Write one `.html` file per screen. No build step, no framework, no Tailwind, no Bootstrap, no icon font, no remote CSS, font, image, or script. The file must open from `file://`.

Name it after the screen (`order-list.html`) in the directory the user is working in, unless they gave a path. UI copy uses the language of the user's request. Use realistic content from the brief. If the brief is thin, pick one concrete product and say what you assumed. Do not use lorem ipsum.

A second screen is another HTML file with the same shell. Link screens with a plain `<a href>`. Add a `<script>` only when the user asked to see two states of the same screen, and then only to toggle the `hidden` attribute. Do not add a router.

## Layout

The content column is at most 1440px wide and sits in the vertical center of the viewport.

The template does this with `grid-template-rows: 1fr auto 1fr` and `.page` on the middle row. A short screen (a form, a dialog, an empty state) rests in the middle. A tall screen starts at the top and scrolls, because the `1fr` rows shrink to nothing once the column is taller than the viewport. Keep that grid. Centering with `align-items: center` or `place-items: center` clips the top of a long page.

Do not add a device frame, browser chrome, or a gray artboard around the page. Sidebars, toolbars, and tables live inside the 1440px column.

## Color

The page is black, white, and gray. These tokens are already in the template:

| Token | Hex | Use |
| --- | --- | --- |
| `--text` | `#18181b` | Primary text, primary button fill, icons |
| `--muted` | `#71717a` | Secondary text |
| `--faint` | `#a1a1aa` | Disabled, placeholder |
| `--line` | `#e4e4e7` | Borders, dividers |
| `--wash` | `#f4f4f5` | Hover fill, table header, inset area |
| `--success` | `#15803d` | Completed, paid, active, passed |
| `--info` | `#1d4ed8` | In progress, processing, neutral notice |
| `--warning` | `#a16207` | Pending, expiring, needs attention |
| `--danger` | `#b91c1c` | Failed, cancelled, overdue, destructive |

Status color is for the status icon only. Do not paint cards, headers, charts, or links with it. Do not invent another hue. No gradients, no shadows, no colored backgrounds except `--wash`.

A primary action is a black `--btn`. A destructive confirmation, and only that confirmation, may use a `--btn` filled with `--danger`. Every other action is an icon button.

## Icons before text

Standard actions are a Lucide icon with no visible word. Put the name in `aria-label` and `title` so a reviewer can hover or use a screen reader to read it. Use these Lucide names: `search`, `plus`, `x`, `pencil`, `trash`, `funnel`, `ellipsis`, `chevron-left`, `download`, `upload`, `eye`, `copy`, `refresh-cw`, `settings`, `user`, `bell`.

Keep a short visible label when the control is not one of those: section names in navigation, field labels, the page title, data values, and the one primary commitment on the screen (Save, Create, Pay). That commitment may be a word, or a word plus an icon. It is the exception that tells a reviewer what the screen is for.

Status is a colored icon, not a pill of text. Add a word beside it only when two statuses would otherwise share the same icon. Map status like this:

- success: `check`
- info: `info`
- warning: `clock` or `triangle-alert`
- danger: `circle-x`

Empty states use one icon and a single short sentence. Do not add an illustration.

## What to leave out

The prototype shows the screen. It does not demonstrate polish.

- No transitions, animations, transforms, skeletons, or hover motion. The template already sets `animation` and `transition` to `none`. Leave that rule in place. Hover may change a background to `--wash` instantly.
- No dropdowns, toasts, drawers, carousels, or tooltips beyond the native `title` attribute, unless the user asked to review that component. If they did, show it open and static, or as a second file.
- No chart library. If a chart is required, draw one gray SVG series. Use a status color only to mark the point the screen is about.
- No emoji, stock photos, or generated illustrations. An avatar is the user icon or initials in a gray circle.

## Before handing it over

- [ ] Opened from the template, still max-width 1440px, still vertically centered without clipping a tall page
- [ ] Only the tokens above; status color appears only on status icons (and a destructive confirm button, if there is one)
- [ ] Standard actions are Lucide icons, copied from the catalog, with `aria-label` and `title`
- [ ] No animation, no remote assets, no framework
- [ ] Copy matches the user's language and the brief's real content
