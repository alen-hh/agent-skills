---
name: html-prototype
description: >-
  Builds a one-pass static HTML prototype of a desktop product screen for
  product-manager review. Use whenever someone asks for a prototype, wireframe,
  mockup, HTML mock, 原型, or 线框图, or describes a product screen they want
  to see quickly — settings, lists, dashboards, forms, dialogs, empty states —
  even if they never say HTML. Desktop web only, with no responsive, mobile,
  or tablet layout. The page is one self-contained file, content width
  1440px and vertically centered, black white and gray only plus success, info,
  warning, and danger status colors, and standard actions are icons rather than
  words. Skip this for production apps, component libraries, Bootstrap styling,
  branded marketing sites, and responsive or mobile UI.
---

# HTML Prototype

Build one static desktop screen a product manager can open and review. The useful version is the first complete screen, not a polished one. Spend the time on the content of the screen. A second layout, a toolchain, or a browser session delays the review.

Copy [assets/page.html](assets/page.html) as the document. Keep its shell, tokens, and the rule that disables animation. Put screen-specific CSS in the same `<style>` block. Icons come from Lucide. Read [references/icons.md](references/icons.md) and copy those SVGs. Do not draw a new icon when Lucide already has one.

## Speed

A reviewer is waiting on the screen, so work in one pass:

- Copy the template, fill in the screen, run the check below, and hand the file over.
- Do not install packages, start a dev server, scaffold a project, or pull in a component library.
- If the brief is thin, pick one concrete product, state that assumption in the reply, and keep going. Ask only when you cannot tell which screen to build or where the file should go.
- Leave the template shell alone. Screen CSS is additive.

## Desktop only

Reviewers open this on a desktop browser. A phone or tablet layout is a different screen, and building it slows down the one they asked for.

Lay the screen out inside the template's 1440px column. Do not add `@media` or `@container` queries, a collapsing sidebar, a hamburger that exists only for a narrow window, stacked mobile tables, or a second file for a smaller viewport. Do not emulate a device or check a narrow window. The template's `min(100%, 1440px)` is only a cap on that desktop column. It is not a responsive system, and it is not a reason to design for more than one width.

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

## Check

The deliverable is a static file. Opening it in a browser, driving a browser, or screenshotting it does not catch more than reading the file, and it is the slow part. Skip Browser Use, the IDE browser, computer use, Playwright, Puppeteer, Chrome DevTools, Lighthouse, device emulation, and page screenshots. A general habit of verifying web apps in a browser does not apply here. This is not an application.

Glance through the file once: copy matches the brief and the user's language, standard actions are Lucide icons with `aria-label` and `title`, and status color is only on status icons (or a destructive confirm button). Then run the checker that ships with this skill, from this skill's directory or by absolute path:

```bash
python3 scripts/check_page.py path/to/screen.html
```

It confirms the file is still the desktop template: no remote assets, no `@media` or `@container`, and the 1440px column, vertical-centering grid, and disabled animation are still there. If it fails, fix the file and run it once more. Then stop. That glance plus the script is the whole test.
