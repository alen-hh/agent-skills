# Icons

Prefer [Lucide](https://lucide.dev). The names in the table are Lucide names, and the SVG paths are copied from Lucide. Stroke, size, and color come from `.icon` in the page template, which matches Lucide: 24 viewBox, stroke width 2, round caps and joins. Do not add fill or stroke attributes.

Paste the SVG into the control. Put the accessible name on the control, not the SVG. The SVG stays `aria-hidden="true"`.

```html
<button class="icon-btn" type="button" aria-label="Delete" title="Delete">
  <!-- paste the trash svg -->
</button>
```

Status wraps the same SVG in a span:

```html
<span class="status-success" title="Paid">
  <!-- check svg, still aria-hidden -->
</span>
```

Do not load `lucide.js`, an icon font, or a CDN. Inline the SVG so the file still opens from `file://`.

If the screen needs an icon that is not listed, copy that icon from Lucide into the same wrapper: `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">...</svg>`. Keep the Lucide name. Draw a new glyph only when Lucide has nothing that fits.

| Lucide name | Use for | SVG |
| --- | --- | --- |
| search | Search | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m21 21-4.34-4.34" /> <circle cx="11" cy="11" r="8" /></svg>` |
| plus | Add, create | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14" /> <path d="M12 5v14" /></svg>` |
| x | Close, dismiss | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18" /> <path d="m6 6 12 12" /></svg>` |
| pencil | Edit | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z" /> <path d="m15 5 4 4" /></svg>` |
| trash | Delete | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 11v6" /> <path d="M14 11v6" /> <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" /> <path d="M3 6h18" /> <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></svg>` |
| funnel | Filter | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z" /></svg>` |
| ellipsis | More actions | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="1" /> <circle cx="19" cy="12" r="1" /> <circle cx="5" cy="12" r="1" /></svg>` |
| check | Success, paid, done, confirm | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5" /></svg>` |
| info | Info, in progress | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" /> <path d="M12 16v-4" /> <path d="M12 8h.01" /></svg>` |
| triangle-alert | Warning | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" /> <path d="M12 9v4" /> <path d="M12 17h.01" /></svg>` |
| circle-x | Danger, failed, cancelled | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" /> <path d="m15 9-6 6" /> <path d="m9 9 6 6" /></svg>` |
| clock | Pending, time | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" /> <path d="M12 6v6l4 2" /></svg>` |
| chevron-left | Back | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6" /></svg>` |
| chevron-right | Next, drill-in | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg>` |
| chevron-down | Expand | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>` |
| user | Account, avatar | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /> <circle cx="12" cy="7" r="4" /></svg>` |
| settings | Settings | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915" /> <circle cx="12" cy="12" r="3" /></svg>` |
| bell | Notifications | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M10.268 21a2 2 0 0 0 3.464 0" /> <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" /></svg>` |
| eye | View | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" /> <circle cx="12" cy="12" r="3" /></svg>` |
| download | Download | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15V3" /> <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /> <path d="m7 10 5 5 5-5" /></svg>` |
| upload | Upload | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12" /> <path d="m17 8-5-5-5 5" /> <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /></svg>` |
| copy | Copy | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2" /> <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" /></svg>` |
| refresh-cw | Refresh, refund | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /> <path d="M21 3v5h-5" /> <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /> <path d="M8 16H3v5" /></svg>` |
| calendar | Date | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 2v3" /> <path d="M16 2v3" /> <rect x="3" y="3" width="18" height="18" rx="2" /> <path d="M3 9h18" /></svg>` |
| credit-card | Billing, payment | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><rect width="20" height="14" x="2" y="5" rx="2" /> <line x1="2" x2="22" y1="10" y2="10" /> <path d="M6 14h2" /></svg>` |
| menu | Open navigation | `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16" /> <path d="M4 12h16" /> <path d="M4 19h16" /></svg>` |

These paths are from Lucide, ISC License. Copyright (c) Lucide Contributors. Portions from Feather (MIT), copyright (c) Cole Bemis.
