# Frontend Application Documentation - Digital-i

## 1. Overview

The Digital-i frontend is a modern, responsive single-page application (SPA) built using Angular (v17). It leverages the PrimeNG (v17) UI component library and is based on the Sakai Angular application template. This combination provides a rich set of pre-built components, a flexible layout system, and robust theming capabilities, enabling a consistent and high-quality user experience.

The frontend is designed to interact with the backend services to display data, manage user interactions, and provide a comprehensive interface for the Digital-i platform's features.

## 2. Project Structure

The primary frontend code resides within the `frontend/sakai-ng/` directory. Below is a breakdown of its structure:

-   **`frontend/`**
    -   **`.dockerignore`**: Specifies files to be ignored by Docker during the image build process.
    -   **`Dockerfile`**: Instructions for building the frontend Docker image, typically using Nginx to serve the application.
    -   **`access_keys/`**: Contains SSL/TLS private key (`digitali_private.key`), public key (`digitali_public.key`), and a self-signed certificate (`digitali_self_signed.crt`). These might be for securing direct access or for reference.
    -   **`nginx/`**: Nginx-specific configuration files.
        -   `digitali_private.key`, `digitali_self_signed.crt`: SSL certificate and key used by the Nginx configuration.
        -   `nginx.conf`: Nginx server block configuration for serving the Angular application, including SSL setup and SPA routing.
    -   **`sakai-ng/`**: The root directory of the Angular CLI project.
        -   **`.editorconfig`**: Configuration for code editor consistency.
        -   **`.eslintrc.json`**: ESLint configuration for code linting.
        -   **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.
        -   **`angular.json`**: Angular CLI workspace configuration file. Defines project settings, build configurations, architect targets (build, serve, test), assets, styles, and more.
        -   **`bun.lockb`**: Lock file for dependencies managed by Bun package manager. (Alternatively, `package-lock.json` for npm or `yarn.lock` for Yarn).
        -   **`CHANGELOG.md`**: Tracks changes across different versions of the Sakai template.
        -   **`LICENSE.md`**: License information for the Sakai template.
        -   **`ngsw-config.json`**: Angular Service Worker configuration file, enabling Progressive Web App (PWA) features like offline caching.
        -   **`package.json`**: Lists project dependencies (Angular, PrimeNG, etc.), devDependencies, and npm/bun scripts (e.g., `ng serve`, `ng build`).
        -   **`README.md`**: General information about the Sakai Angular template, including CLI commands.
        -   **`tsconfig.app.json`**: TypeScript configuration specific to the application.
        -   **`tsconfig.json`**: Root TypeScript configuration for the project.
        -   **`tsconfig.spec.json`**: TypeScript configuration for unit tests.
        -   **`.angular/`**: Angular CLI cache directory.
        -   **`src/`**: Contains the main application source code.
            -   `favicon.ico`: Application icon.
            -   `index.html`: The main HTML page that bootstraps the Angular application. It includes links to global stylesheets and the root application tag (`<app-root>`).
            -   `main.ts`: The main entry point for the Angular application. It bootstraps the root `AppModule`.
            -   `manifest.webmanifest`: Web App Manifest for PWA capabilities.
            -   `styles.scss`: Global SASS/CSS styles for the application.
            -   `test.ts`: Main entry point for Karma unit tests.
            -   **`app/`**: Contains the core application modules, components, services, and routing.
                -   `app.module.ts`: The root module of the application.
                -   `app-routing.module.ts`: The root routing module defining top-level navigation.
                -   `app.component.ts/html/scss`: The root Angular component.
                -   **`layout/`**: Contains components related to the Sakai application layout (e.g., `app.layout.component.ts`, `app.menu.component.ts`, `app.topbar.component.ts`, `app.sidebar.component.ts`, `app.footer.component.ts`).
                -   **`components/`**: Intended for custom, application-specific reusable components (e.g., `configuration/config/config.component.html` is a custom component).
                -   **`demo/`**: Contains demo pages and components provided by the Sakai template, showcasing PrimeNG components and various UI patterns (e.g., `landing/`, `primeblocks/`, `uikit/`, `documentation/`). These serve as excellent examples and starting points.
            -   **`assets/`**: Static assets used by the application.
                -   `assets/demo/`: Assets used by the demo pages.
                -   `assets/layout/`: Assets specific to the Sakai layout, including images, fonts, and crucially, themes.
                    -   `assets/layout/styles/theme/`: Contains various PrimeNG themes (e.g., `lara-light-indigo/theme.css`).
            -   **`environments/`**: Contains environment-specific configuration files (e.g., `environment.ts` for development, `environment.prod.ts` for production).

## 3. Key Technologies & Libraries

-   **Angular (v17)**: The core framework providing a component-based architecture, dependency injection, routing, forms handling, and more.
-   **PrimeNG (v17)**: A comprehensive suite of UI components for Angular, offering a wide range of widgets like tables, forms, charts, overlays, menus, etc.
-   **Sakai Angular Template**: A pre-built application template based on Angular and PrimeNG, providing the overall structure, a responsive layout system, and several demo pages.
-   **PrimeFlex**: A lightweight, responsive CSS utility library, similar to Tailwind CSS, used for creating flexible and responsive layouts with ease. (Referenced in `index.html`).
-   **Font Awesome (v6.4.2)**: A popular icon library providing a wide range of scalable vector icons. (Referenced in `index.html`).
-   **TypeScript**: The primary programming language for Angular development, adding static typing to JavaScript.
-   **SASS/SCSS**: A CSS preprocessor used for writing more maintainable and powerful stylesheets. Global styles are in `styles.scss`.
-   **Nginx**: A high-performance web server, reverse proxy, and load balancer, used here to serve the built Angular application in a Docker container.
-   **Docker**: A platform for developing, shipping, and running applications in containers, ensuring consistency across environments.

## 4. Core Concepts

### Angular CLI
The Angular Command Line Interface (CLI) is used extensively for:
-   Generating components, modules, services, directives, pipes, etc. (`ng generate component component-name`)
-   Running the development server (`ng serve`)
-   Building the application for development or production (`ng build`, `ng build --configuration production`)
-   Running unit tests (`ng test`) and end-to-end tests (`ng e2e`)
(Refer to `frontend/sakai-ng/README.md` for more CLI commands).

### Modularity
The application is structured into Angular Modules (`@NgModule`).
-   **`AppModule` (`src/app/app.module.ts`)**: The root module that bootstraps the application.
-   **Feature Modules**: For organizing code related to specific features or sections of the application (e.g., `src/app/demo/components/documentation/documentation.module.ts`).
-   **Routing Modules**: Separate modules for defining navigation paths (e.g., `src/app/app-routing.module.ts`, `src/app/demo/components/documentation/documentation-routing.module.ts`).

### Component-Based Architecture
The UI is built as a tree of reusable components. Each component encapsulates its HTML template, styles, and logic (TypeScript class).

### Routing
Navigation within the SPA is handled by Angular's `RouterModule`.
-   Routes are defined in routing modules, mapping URL paths to components.
-   The Sakai template includes routing for its demo pages and a base structure for application routes.

### Services
Services are used for:
-   Encapsulating business logic.
-   Sharing data and functionality across components.
-   Interacting with external APIs (e.g., fetching data from the backend).
-   The `LayoutService` (`src/app/layout/service/app.layout.service.ts`) from Sakai is a key service for managing layout configurations like theme, color scheme, menu mode, and ripple effect.

### Theming
-   The Sakai template provides excellent theming support through PrimeNG themes.
-   The default theme is linked in `src/index.html` (e.g., `assets/layout/styles/theme/lara-light-indigo/theme.css`).
-   Themes can be switched dynamically using the `LayoutService` and the configuration UI provided by Sakai.
-   PrimeNG themes are SASS-based, allowing for deep customization of colors, fonts, and component styles.

### Layout System (Sakai)
The Sakai template provides a flexible and responsive application layout:
-   **`AppLayoutComponent`** (likely `src/app/layout/app.layout.component.ts`): The main component orchestrating the overall page structure.
-   **Topbar (`app.topbar.component.ts`)**: Typically contains the application title/logo, user profile information, and quick access actions.
-   **Sidebar/Menu (`app.menu.component.ts`, `app.sidebar.component.ts`)**: The main navigation area. Menu items are defined using the PrimeNG MenuModel API in `app.menu.component.ts`.
-   **Footer (`app.footer.component.ts`)**: Contains copyright information or other footer content.
-   The layout can be configured (e.g., static vs. overlay menu) via the `LayoutService`.

### Forms
-   Angular supports both **Template-Driven Forms** and **Reactive Forms** for handling user input.
-   PrimeNG offers a rich set of form components (`pInputText`, `pInputTextarea`, `pDropdown`, `pCalendar`, `pCheckbox`, `pRadioButton`, etc.) that integrate seamlessly with Angular forms and provide enhanced styling and functionality. Examples can be found in `src/app/demo/components/uikit/formlayout/formlayoutdemo.component.html`.

### API Interaction
-   Angular's `HttpClientModule` and `HttpClient` service are used for making HTTP requests to the backend API.
-   Typically, dedicated services are created to encapsulate API calls for different resources, making the code more modular and testable.

## 5. Development Setup

1.  Navigate to the Angular project directory: `cd frontend/sakai-ng`
2.  Install dependencies:
    -   If using Bun (due to `bun.lockb`): `bun install`
    -   If using npm: `npm install`
    -   If using Yarn: `yarn install`
3.  Start the development server: `ng serve`
4.  Open your browser and navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## 6. Build Process

-   **Development Build**: `ng build`
-   **Production Build**: `ng build --configuration production` (or `ng build --prod` for older Angular CLI versions).
    This command optimizes the application for production by enabling Ahead-of-Time (AOT) compilation, minification, tree-shaking, and other performance enhancements.
-   The build artifacts will be stored in the `frontend/sakai-ng/dist/` directory (usually `dist/sakai-ng/`).

## 7. Deployment

The frontend application is designed to be deployed using Docker and Nginx.

### Docker
-   The `frontend/Dockerfile` defines the steps to build a Docker image for the frontend.
-   **Build Stages**:
    1.  A Node.js-based stage to build the Angular application using `npm install` (or `bun install`) and `ng build --configuration production`.
    2.  An Nginx-based stage to serve the built application. It copies the compiled static files from the `dist/` directory of the previous stage into Nginx's webroot (e.g., `/usr/share/nginx/html`).
    3.  It also copies the custom Nginx configuration (`frontend/nginx/nginx.conf`) and SSL certificates into the image.

### Nginx Configuration (`frontend/nginx/nginx.conf`)
The `nginx.conf` file configures the Nginx server within the Docker container:
-   **Server Blocks**: Defines listeners, typically on port 80 (HTTP) and 443 (HTTPS).
-   **SSL/TLS Termination**: Configured to use the SSL certificate (`digitali_self_signed.crt`) and private key (`digitali_private.key`) found in the `frontend/nginx/` directory within the Docker image.
-   **Web Root**: Sets the `root` directive to the directory containing the built Angular static files (e.g., `/usr/share/nginx/html`).
-   **Index File**: Specifies `index.html` as the default file.
-   **SPA Routing**: Includes a `location /` block with `try_files $uri $uri/ /index.html;` to ensure that all routes are directed to `index.html`, allowing Angular's router to handle client-side navigation.
-   **Caching**: May include directives for browser caching of static assets (`css`, `js`, `images`).
-   **Compression**: May enable gzip compression to reduce the size of transferred files.

## 8. Key Directories and Files Explained (Detailed)

-   **`frontend/sakai-ng/src/index.html`**:
    -   The single HTML page served to the browser.
    -   Contains the `<app-root></app-root>` tag where the main Angular application component is rendered.
    -   Links the default PrimeNG theme CSS (e.g., `assets/layout/styles/theme/lara-light-indigo/theme.css`). This can be changed to use a different theme.
    -   Links PrimeFlex CSS for utility classes.
    -   Links Font Awesome CSS for icons.
    -   Includes `<meta name="viewport" ...>` for responsiveness.
-   **`frontend/sakai-ng/src/main.ts`**:
    -   The entry point that bootstraps the Angular application.
    -   Imports the root `AppModule` and uses `platformBrowserDynamic().bootstrapModule(AppModule)` to start the application.
    -   May include enabling production mode (`enableProdMode()`) based on the environment.
-   **`frontend/sakai-ng/src/styles.scss`**:
    -   Global SASS file where application-wide styles or SASS variable overrides can be defined.
    -   Styles defined here affect the entire application.
-   **`frontend/sakai-ng/angular.json`**:
    -   A crucial configuration file for the Angular CLI.
    -   Defines projects within the workspace (here, likely just "sakai-ng").
    -   Specifies architect targets:
        -   `build`: Configures how the application is built (output path, `index.html` location, `main.ts` entry point, `tsconfig.app.json`, assets to include, global styles, scripts). Different configurations (e.g., "production") can override these settings.
        -   `serve`: Configures the development server.
        -   `test`: Configures Karma for unit testing.
        -   `lint`: Configures ESLint.
-   **`frontend/sakai-ng/package.json`**:
    -   Lists all project dependencies (e.g., `@angular/core`, `primeng`, `primeicons`, `primeflex`) and development dependencies (e.g., `@angular/cli`, `@types/node`, `typescript`).
    -   Defines `scripts` for common tasks like `start` (usually `ng serve`), `build` (`ng build`), `test` (`ng test`).
-   **`frontend/sakai-ng/src/app/layout/service/app.layout.service.ts`**:
    -   A service provided by the Sakai template to manage and communicate layout state changes.
    -   Allows components to react to or modify layout properties such as:
        -   Current theme (`theme`)
        -   Color scheme (`colorScheme`: 'light' or 'dark')
        -   Menu mode (`menuMode`: 'static', 'overlay')
        -   Input style (`inputStyle`: 'outlined', 'filled')
        -   Ripple effect (`ripple`)
        -   Scale (font size)
    -   Uses RxJS Subjects or BehaviorSubjects to broadcast state changes. (As seen in `documentation.component.html` code example for `LayoutService.config.set(config)`).

## 9. Customization

### Themes
1.  **Changing Pre-built Themes**:
    -   Modify the `href` of the theme link in `src/index.html` to point to a different theme CSS file from `src/assets/layout/styles/theme/`.
    -   Alternatively, use the `LayoutService` to change themes dynamically if the application supports it through a UI (like the Sakai demo's config sidebar).
2.  **Customizing Themes**:
    -   PrimeNG themes are SASS-based. To deeply customize a theme, you would typically import the theme's SASS source files into your project's `styles.scss` or a dedicated theme SASS file, override SASS variables (colors, fonts, spacing, etc.), and then compile it.

### Layout
-   Modify the HTML templates and TypeScript logic of components within `src/app/layout/` (e.g., `app.topbar.component.html`, `app.menu.component.html`).
-   Change menu items by editing the `model` array in `src/app/layout/app.menu.component.ts`.

### Components
-   Add new application-specific components within `src/app/components/` or other feature-specific directories.
-   Modify or extend existing PrimeNG components using their APIs and templates, or by wrapping them in custom components.

## 10. Security (SSL/TLS)

-   The frontend deployment setup includes SSL/TLS configuration for secure HTTPS communication.
-   The `frontend/nginx/nginx.conf` file is configured to use:
    -   `ssl_certificate /etc/nginx/ssl/digitali_self_signed.crt;`
    -   `ssl_certificate_key /etc/nginx/ssl/digitali_private.key;`
    (The paths `/etc/nginx/ssl/` are typical locations within an Nginx Docker container where certificates are copied).
-   The `digitali_self_signed.crt` is a self-signed certificate, suitable for development or internal testing. For production, a certificate issued by a trusted Certificate Authority (CA) should be used.
-   The `frontend/access_keys/` directory also contains key and certificate files, possibly as a backup or for other services. Ensure the correct and intended files are used by Nginx.

This documentation provides a comprehensive overview of the Digital-i frontend application, its structure, technologies, and operational aspects.