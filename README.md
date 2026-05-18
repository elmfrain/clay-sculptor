# Clay Sculptor

A lightweight **compile-time UI authoring** layer for [Clay](https://github.com/nicbarker/clay).

## Table of Contents
* [Description](#description)
* [Automated Requirements and Validation](#automated-requirements-and-validation)
* [Disclaimers](#disclaimers)
* [License](#license)

## Description

Clay Sculptor is a tooling suite designed to help developers using the [Clay UI layout library](https://github.com/nicbarker/clay) by Nic Barker to rapidly design and iterate user interfaces within their native applications.

Just like how modern web developers benefit from UI frameworks that enable fast, declarative, and responsive interface development, Clay Sculptor brings a similar workflow to native applications built with Clay. It allows developers to author UI layouts declaratively using XML-based `.ui` files and CSS-like `.style` files, and then preview and generate native UI C code powered by Clay.

The goal of Clay Sculptor is to **eliminate the repetitive boilerplate** commonly associated with building interfaces directly in Clay. While Clay itself is intuitive and enjoyable to use, large interfaces can eventually become cumbersome to maintain and iterate on. For instance, boilerplate-heavy UI code can slow down development, reduce readability, and ultimately get in the way of experimentation and creativity. Clay Sculptor solves this by automating the tedious parts of UI construction while preserving Clay’s immediate-mode philosophy.

Therefore, developers can:
* Rapidly prototype and iterate on interfaces
* Preview UI changes in real time
* Generate clean Clay-ready C code
* Reduce repetitive boilerplate
* Maintain full control over application logic and rendering behavior

Despite providing live iteration and hot-reloading capabilities during development, the **tooling remains completely non-intrusive** in production builds. Debug builds may include a lightweight runtime to support features such as hot reloading, but release/static builds contain no runtime dependency on Clay Sculptor itself. Only the generated C code is compiled into the final executable.

Clay Sculptor’s workflow is intentionally similar to modern web development:
* `.ui` files define UI structure declaratively, similar to HTML
* `.style` files define styling rules using a CSS-inspired syntax
* The tooling generates native C source files automatically
* Generated files integrate directly into the host application

The `.style` format is intentionally only a subset of CSS and is not intended to be a full CSS implementation.
The project is also designed to **integrate seamlessly with CMake-based build systems** by supporting automatic code generation, debug tooling integration, and hot-reload workflows.

Importantly, Clay Sculptor does not manage application behavior or business logic. Developers remain fully responsible for implementing interactions, callbacks, event handling, dynamic styling, and application state. The **tooling focuses solely on generating and organizing UI boilerplate** so that developers can continue using Clay exactly as intended with immediate-mode control over behavior and rendering.

In keeping with Clay’s lightweight philosophy, Clay Sculptor also aims to minimize dependencies. In most cases, developers only need a C compiler and CMake to integrate the tooling into their project.

## Automated Requirements and Validation

One of the goals of Clay Sculptor is to remain closely aligned with Clay itself, ensuring that developers can access the full range of functionality exposed by the underlying layout library.

To achieve this, Clay Sculptor treats Clay’s source code as the authoritative source of truth for capability discovery, validation, testing, and documentation. Rather than manually maintaining large compatibility tables or feature checklists, the project uses automated tooling to introspect Clay’s source code and derive a structured representation of the features available to UI authors.

This approach helps prevent compatibility gaps as Clay evolves over time while also improving the maintainability of Clay Sculptor itself. The resulting metadata is used to drive:

* CSS/XML subset validation
* feature compatibility reports
* automated test generation
* implementation checklists
* documentation generation
* CI validation pipelines

### Development Dependencies

The introspection and validation pipeline depends on:

* `python`
* `pycparser`

These dependencies are intended exclusively for Clay Sculptor maintainers and contributors. They are **not** required by applications using the toolkit itself because Clay Sculptor intentionally avoids introducing runtime dependencies.

### Parsing

Clay Sculptor uses `pycparser` to parse Clay’s source code into an [Abstract Syntax Tree (AST)](https://en.wikipedia.org/wiki/Abstract_syntax_tree), enabling the project to inspect Clay’s public API structure programmatically.

The parsing stage is intentionally structural rather than semantic. Its purpose is not to fully understand Clay’s internal implementation details, but rather to extract the public-facing types and declarations relevant to UI authoring.

### Code Introspection

During introspection, the pipeline scans the [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) for relevant public API constructs, including:

* structs
* enums
* configuration types
* public API declarations
* flags

Private or implementation-specific symbols (such as functions prefixed with `Clay__`), however, are intentionally ignored.

The primary purpose of introspection is to detect capability changes between Clay versions. Newly discovered features, removed APIs, or modified declarations can then be reviewed and acknowledged by a maintainer before being integrated into Clay Sculptor’s higher-level semantic systems.

### Semantic Capability Registry

The semantic capability registry acts as the canonical metadata layer describing how Clay features map onto Clay Sculptor’s authoring model.

The registry defines:

* layout capabilities
* style properties
* supported value types
* enums and flags
* implementation status

This registry serves as the foundation for multiple systems within Clay Sculptor, allowing validators, documentation, generated code, tests, and CI tooling to derive behavior from a single source of truth.

### Hybrid Synchronization Model

The **capability registry is not generated automatically** from introspection results alone.

Instead, Clay Sculptor uses a hybrid synchronization model:

1. Clay’s source code is parsed and introspected automatically.
2. Relevant API changes are surfaced to maintainers.
3. Maintainers semantically integrate those changes into the capability registry according to Clay Sculptor’s terminology and design patterns.

This distinction is intentional!

While introspection can reliably detect structural API changes, semantic interpretation requires human review. This prevents accidental exposure of incomplete or poorly mapped features while ensuring the registry remains consistent and maintainable over time.

## Disclaimers

* The README of this repository is made with the assistance of an LLM to aid with the headache of having to write perfect grammar and sentence flow.

## License

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software. Permission is granted to anyone to use this software for any purpose under the terms of the zlib license.
