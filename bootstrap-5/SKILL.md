---
name: bootstrap-5
description: Guide for using Bootstrap 5 framework for frontend development. Use when building UI components, layouts, or when the user mentions Bootstrap, b5, or responsive design. Applicable to any tech stack (HTML, Vue, React, etc.).
---

# Bootstrap 5 Development Guide

## Quick Start

When developing with Bootstrap 5, follow these core principles regardless of the underlying tech stack:

1. **Utility-First Approach**: Use Bootstrap's extensive utility classes for spacing (`m-*`, `p-*`), typography (`fs-*`, `fw-*`), flexbox (`d-flex`, `justify-content-*`), and colors (`text-*`, `bg-*`) before writing custom CSS.
2. **Mobile-First Grid**: Utilize the 12-column grid system (`container`, `row`, `col-*`). Design for mobile first, then scale up using breakpoint infixes (`sm`, `md`, `lg`, `xl`, `xxl`).
3. **No jQuery**: Bootstrap 5 dropped jQuery. Rely on vanilla JavaScript or your framework's state management for component behavior.
4. **CSS Variables**: Leverage Bootstrap's CSS variables (e.g., `var(--bs-primary)`) for easier theming and customization.

## Framework-Agnostic Usage

Bootstrap 5's core is its CSS. The HTML structure and class names remain consistent across frameworks.

### Structure & Classes
Always use the correct semantic HTML structure and class names as defined in the Bootstrap documentation.
*Note: In React, remember to use `className` instead of `class`.*

### Component Behavior (JavaScript)
- **Plain HTML/JS**: Use `data-bs-*` attributes (e.g., `data-bs-toggle="modal"`, `data-bs-target="#myModal"`) to initialize components without writing JS.
- **Vue/React/Angular**: While you *can* use the native Bootstrap JS via refs/DOM manipulation, it is often better to manage state (like modal open/closed) via the framework's reactivity system and conditionally apply classes (like `.show`, `.d-block`), or use framework-specific wrapper libraries (like `react-bootstrap` or `bootstrap-vue-next`) if they are installed in the project.

## Review Checklist

- [ ] Are utility classes used instead of custom CSS where possible?
- [ ] Is the grid system used correctly for responsive layouts?
- [ ] Are accessibility attributes (ARIA) preserved from the Bootstrap examples?
- [ ] Are `data-bs-*` attributes used correctly (if relying on Bootstrap's native JS)?
- [ ] Are CSS variables used for custom styling instead of hardcoded values?

## Additional Resources

- For concrete component and layout examples, see [examples.md](examples.md)
- For official documentation links, see [reference.md](reference.md)
