# Clay Sculptor

A lightweight **compile-time UI authoring** layer for Clay [Clay](https://github.com/nicbarker/clay).

## Description

Clay Sculptor is a tooling suite designed to help developers using the [Clay UI layout library](https://github.com/nicbarker/clay) by Nic Barker to rapidly design and iterate user interfaces within their native applications.

Just like how modern web developers benefit from UI frameworks that enable fast, declarative, and responsive interface development, Clay Sculptor brings a similar workflow to native applications built with Clay. It allows developers to author UI layouts declaratively using XML-based `.ui` files and CSS-inspired `.style` files, and then preview and generate native UI C code powered by Clay.

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
The project is designed to **integrate seamlessly with CMake-based build systems**, supporting automatic code generation, debug tooling integration, and hot-reload workflows.

Importantly, Clay Sculptor does not manage application behavior or business logic. Developers remain fully responsible for implementing interactions, callbacks, event handling, dynamic styling, and application state. The **tooling focuses solely on generating and organizing UI boilerplate** so that developers can continue using Clay exactly as intended with immediate-mode control over behavior and rendering.

In keeping with Clay’s lightweight philosophy, Clay Sculptor also aims to minimize dependencies. In most cases, developers only need a C compiler and CMake to integrate the tooling into their project.
