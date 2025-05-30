# Frontend Components Documentation (`src/app/components/`)

This document outlines the structure and purpose of the custom Angular components located within the `src/app/components/` directory of the Digital-i frontend application. This directory houses reusable UI elements and feature-specific views that form the core user interface of the application, distinct from the generic layout components provided by the Sakai template.

## Overview

The `src/app/components/` directory is organized into subdirectories, primarily based on the application's functional areas: `configuration` and `resource`. These components are responsible for rendering data, handling user interactions, and communicating with services to perform application-specific tasks.

## Main Component Directories

### 1. `configuration/`

This directory contains components related to the setup and management of various system configurations and master data. These are typically forms, tables, and views used by administrators or privileged users to define how the application behaves and what foundational data it uses.

-   **`absence-correction/`**: Components for managing and correcting absence records or rules.
-   **`company/`**: Components for managing company details and settings. (Example: `config.component.html` shows a "Company" panel).
-   **`config/`**: A general configuration section.
    -   **`config.component.ts` / `config.component.html` / `config.component.scss`**: This component likely serves as a dashboard or entry point for various general configuration modules. The HTML shows a "General Configuration" section with expandable panels for different settings (e.g., "Company"). It uses PrimeNG panels (`<p-panel>`) for organizing configuration items.
-   **`department/`**: Components for managing departments within the organization.
-   **`designation/`**: Components for managing employee designations or job titles.
-   **`device-config/`**: Components for configuring biometric or other hardware devices integrated with the system.
-   **`division/`**: Components for managing organizational divisions.
-   **`fixed-shift/`**: Components for defining and managing fixed work shifts for employees.
-   **`holiday-list/`**: Components for creating and managing the list of holidays.
-   **`location/`**: Components for managing different work locations or sites.
-   **`overtime-roundoff/`**: Components for configuring rules related to overtime calculation and rounding.
-   **`shift/`**: Components for general shift management (possibly including auto-shifts or more complex shift patterns beyond fixed shifts).
-   **`shopfloor/`**: Components related to shop floor configurations, possibly for manufacturing or specific operational areas.
-   **`subdivision/`**: Components for managing organizational subdivisions.

### 2. `configurations/` (Note: Plural form)

This directory appears to be distinct from `configuration/`.
-   **`logs/`**: Components for viewing or managing system logs or audit trails, specifically from a configuration perspective. The singular `configuration` might be for setting up entities, while `configurations` (plural) might be for viewing the state or history of those configurations or related system events.

### 3. `resource/`

This directory houses components related to employee data, attendance processing, reporting, and resource management. These are the primary operational interfaces for users interacting with employee and attendance-related data.

-   **`absent/`**: Components for displaying or managing information about absent employees.
-   **`attendance-regularization/`**: Components for handling requests or processes to regularize attendance discrepancies (e.g., missed punches, incorrect entries).
-   **`daily-report/`**: Components for generating and viewing daily attendance or operational reports.
-   **`early-exit/`**: Components for reporting or managing instances of employees leaving early.
-   **`employee-master/`**: Components for managing the master list of employees, including their profiles and details.
-   **`insufficient-hours-report/`**: Components for generating reports on employees who have not completed their required work hours.
-   **`interfaces/`**: This could contain UI components for managing data interfaces with other systems or for specific data import/export functionalities related to resources.
-   **`late-entry/`**: Components for reporting or managing instances of employees arriving late.
-   **`mandays/`**: Components related to "Man-days" calculations or reports, possibly for project costing or effort tracking.
-   **`missed-punch-report/`**: Components for generating reports on missed clock-in/out punches.
-   **`monthly-in-out/`**: Components for displaying or reporting monthly IN/OUT punch data for employees.
-   **`overtime/`**: Components for viewing, managing, or reporting overtime hours.
-   **`present/`**: Components for displaying or managing information about present employees.
-   **`reset-report/`**: Components for reports related to data resets or specific reset events.
-   **`resource-dashboard/`**: A dashboard component providing an overview and key metrics related to resources (employees, attendance, etc.).

## Component Implementation Example (`configuration/config/config.component.ts`)

The `ConfigComponent` provides a glimpse into how components in this directory might be structured:

-   **Selector**: `app-config`
-   **Standalone**: `false` (meaning it's declared in an Angular module, likely a shared or feature module for configurations).
-   **Template & Styles**: Uses external HTML (`./config.component.html`) and SCSS (`./config.component.scss`) files.
-   **Dependencies**:
    -   `SharedService`: Likely a custom service for sharing data or utility functions across components.
    -   `EventemitterService`: A custom service for inter-component communication using events.
    -   RxJS operators (`map`, `switchMap`, `distinctUntilChanged`, `startWith`, `interval`): Indicates reactive programming patterns are used, possibly for handling asynchronous data streams or real-time updates.
-   **Functionality**: The HTML structure with `<p-panel>` suggests it acts as a container for various configuration sections, allowing users to expand/collapse them. The SCSS `.card { cursor: pointer; }` implies interactive card-like elements.

## General Component Practices

Based on the structure and the example:
-   Components are feature-specific and organized logically.
-   PrimeNG components (`p-panel`, `p-divider`, `p-button`) are heavily utilized for building the UI.
-   Custom services (`SharedService`, `EventemitterService`) are used for shared logic and communication.
-   Reactive patterns with RxJS are employed for managing data and events.

This structured approach to component organization allows for better maintainability and scalability of the frontend application. Each subdirectory under `components/` likely corresponds to a distinct feature set or module within the Digital-i platform.