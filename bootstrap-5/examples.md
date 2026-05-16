# Bootstrap 5 Examples

These examples demonstrate the core HTML structure and class names required for Bootstrap 5 components. Adapt the syntax (e.g., `class` vs `className`) and state management according to your specific tech stack.

## 1. Responsive Grid Layout

A common layout using containers, rows, and responsive columns.

```html
<div class="container">
  <div class="row g-3"> <!-- g-3 adds gutters -->
    <div class="col-12 col-md-6 col-lg-4">
      <div class="p-3 border bg-light">Column 1</div>
    </div>
    <div class="col-12 col-md-6 col-lg-4">
      <div class="p-3 border bg-light">Column 2</div>
    </div>
    <div class="col-12 col-md-12 col-lg-4">
      <div class="p-3 border bg-light">Column 3</div>
    </div>
  </div>
</div>
```

## 2. Flexbox Utilities

Using utility classes for alignment and spacing.

```html
<div class="d-flex justify-content-between align-items-center p-3 mb-2 bg-primary text-white rounded">
  <h2 class="m-0 fs-4">Dashboard</h2>
  <button class="btn btn-light btn-sm">Settings</button>
</div>
```

## 3. Interactive Component: Modal (Plain HTML)

This example uses Bootstrap's native `data-bs-*` attributes to handle the modal state without custom JavaScript.

```html
<!-- Button trigger modal -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#exampleModal">
  Launch demo modal
</button>

<!-- Modal -->
<div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Modal title</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        ...
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary">Save changes</button>
      </div>
    </div>
  </div>
</div>
```

### Framework Adaptation Note (e.g., React/Vue)
In a reactive framework, you might not use `data-bs-toggle`. Instead, you would bind a click event to the button to update a state variable (e.g., `isOpen`), and conditionally render the modal or apply the `.show` class and `display: block` style based on that state.

## 4. Card Component

A standard card layout.

```html
<div class="card" style="width: 18rem;">
  <img src="..." class="card-img-top" alt="...">
  <div class="card-body">
    <h5 class="card-title">Card title</h5>
    <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
    <a href="#" class="btn btn-primary">Go somewhere</a>
  </div>
</div>
```
