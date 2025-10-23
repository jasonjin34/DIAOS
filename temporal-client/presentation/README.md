# Industrial-Grade Agent Orchestration Presentation

This package contains a self-contained HTML presentation about "Formalizing Durability and Verifiability in Autonomous Agent Systems."

## Features

- Interactive slide navigation with Previous/Next buttons
- Keyboard navigation (Arrow keys and Spacebar)
- Responsive design optimized for presentation displays
- Professional RWTH Aachen University styling
- 10 comprehensive slides covering:
  - Current state of agent capabilities
  - Reliability challenges in production
  - Formal requirements for mission-critical systems
  - Proposed State-Centric Orchestration (SCO) framework
  - Architecture and implementation details
  - Empirical validation scenarios
  - Comparative analysis

## Usage

### Simple Local Server

To view the presentation, simply open the `index.html` file in a web browser or serve it with a local HTTP server:

```bash
# Using Python
cd temporal-client/presentation
python3 -m http.server 8080

# Using Node.js (if you have http-server installed)
npx http-server -p 8080

# Using any other local server
# Then navigate to http://localhost:8080
```

### Integration with Next.js (Optional)

If you want to integrate this presentation into the main Next.js application, you can:

1. Move the HTML content to a Next.js page component
2. Add the presentation as a static route in the Next.js public directory
3. Create an iframe embed within the existing application

## Navigation

- **Next Slide**: Click "Next" button, press Right Arrow, or press Spacebar
- **Previous Slide**: Click "Previous" button or press Left Arrow
- **Slide Counter**: Shows current slide position (e.g., "3 / 10")

## Customization

The presentation uses CSS custom properties for easy theming:

- `--rwth-blue`: Primary brand color
- `--light-grey`: Background color
- `--dark-grey`: Text color
- `--alert-red`: Error/warning color
- `--accent-green`: Success color

Edit the CSS variables in the `<style>` section to customize the appearance.