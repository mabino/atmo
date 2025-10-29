# Atmo Documentation Site

This directory contains the Jekyll-based documentation website for the Atmo project, served via GitHub Pages.

## Setup GitHub Pages

To enable GitHub Pages for this repository:

1. Go to **Settings** → **Pages** in your GitHub repository
2. Under **Source**, select **GitHub Actions**
3. The site will be automatically built and deployed when you push to the `main` branch

## Local Development

### Quick Setup
Run the setup script to get started quickly:

```bash
cd docs
./setup.sh
```

This will:
- Install Jekyll dependencies
- Copy screenshots from the root directory
- Start the development server at `http://localhost:4000/atmo/`

### Manual Setup

1. **Install Ruby and Bundler** (if not already installed):
   ```bash
   # On macOS with Homebrew
   brew install ruby
   gem install bundler
   ```

2. **Install dependencies**:
   ```bash
   cd docs
   bundle install
   ```

3. **Run the development server**:
   ```bash
   bundle exec jekyll serve
   ```

4. **View the site** at `http://localhost:4000/atmo/`

## Site Structure

- `_layouts/` - Page templates
- `_includes/` - Reusable HTML components
- `_docs/` - Documentation pages
- `assets/` - CSS, JS, and images
- `index.md` - Homepage
- `_config.yml` - Jekyll configuration

## Deployment

The site is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. The site will be available at:

`https://mabino.github.io/atmo/`

## Adding Content

- **New documentation pages**: Add Markdown files to `_docs/`
- **Images**: Place in `assets/images/`
- **Styles**: Edit `assets/css/main.css`
- **JavaScript**: Edit `assets/js/main.js`

## Screenshots

Screenshots are automatically copied from the root `screenshots/` directory to `assets/images/` during the build process.