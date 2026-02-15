# Owen Queen - Minimalist Personal Website

A clean, modern, single-page website showcasing Owen Queen's academic profile and research work, with **automatic publication management** from BibTeX.

## 🚀 **Automatic Build System**

This website uses a **dynamic build system** that automatically generates the HTML from your BibTeX file. This means:

- ✅ **No manual HTML editing** for publications
- ✅ **Easy to add new papers** - just update `ref.bib`
- ✅ **Automatic sorting** by year (newest first)
- ✅ **Automatic link generation** for DOIs, arXiv, and code
- ✅ **GitHub Actions integration** for automatic builds

## 📝 **How to Add Publications**

1. **Add your publication to `ref.bib`** in standard BibTeX format
2. **Run the build script**: `python3 build.py`
3. **The website updates automatically!**

### Example BibTeX Entry:
```bibtex
@article{queen2024example,
  title={Your Paper Title},
  author={Queen, Owen and Others},
  journal={Journal Name},
  year={2024},
  doi={10.1000/example}
}
```

## 🛠️ **Build System Files**

- **`build.py`** - Python script that parses BibTeX and generates HTML
- **`template.html`** - HTML template with `{{PUBLICATIONS}}` placeholder
- **`ref.bib`** - Your BibTeX bibliography file
- **`.github/workflows/build.yml`** - GitHub Actions for automatic builds

## 🎨 **Features**

- **Single-page design** with smooth scrolling navigation
- **Minimalist aesthetic** using neutral colors and clean typography
- **Fully responsive** design that works on all devices
- **Publications section** with clean listing and direct links
- **Modern CSS** with CSS variables for easy customization
- **Helvetica font** for professional typography

## 📱 **Sections**

1. **Hero** - Name, title, and brief introduction with profile picture
2. **About** - Background, education, and career highlights
3. **Research** - Research focus and interests
4. **Publications** - **Automatically generated** from BibTeX
5. **Contact** - Email and professional links

## 🎨 **Color Scheme**

The website uses a sophisticated neutral palette:
- **Primary text:** `#2a2a2a` (dark gray)
- **Secondary text:** `#666666` (medium gray)
- **Accent color:** `#6b7fd7` (soft blue)
- **Accent light:** `#e8ecff` (very light blue)
- **Accent purple:** `#9b7bb8` (soft purple)
- **Background:** `#ffffff` (white)
- **Section background:** `#f8f9ff` (very light blue tint)

## 🚀 **Usage**

### Local Development:
```bash
# Build the website
python3 build.py

# Open in browser
open index.html
```

### GitHub Pages Deployment:
1. Push changes to `ref.bib`
2. GitHub Actions automatically builds and deploys
3. Website updates automatically!

## 🔧 **Customization**

- **Colors:** Edit CSS variables in `template.html`
- **Layout:** Modify `template.html` structure
- **Publications:** Update `ref.bib` and run `build.py`
- **Build logic:** Modify `build.py` for custom parsing

## 📋 **Supported BibTeX Fields**

The build system automatically generates links for:
- **DOI:** Creates `https://doi.org/{doi}` links
- **arXiv:** Creates `https://arxiv.org/abs/{eprint}` links
- **URL:** Uses direct URLs if provided
- **Code:** Links to code repositories (if `code` field present)

## 🎯 **Benefits of This System**

1. **Maintainability** - No need to manually edit HTML for publications
2. **Consistency** - All publications follow the same format
3. **Automation** - GitHub Actions handles builds automatically
4. **Extensibility** - Easy to add new publication types
5. **Version Control** - BibTeX is the single source of truth 