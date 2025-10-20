# Web Assets

This directory contains static assets for the Petting Zootopia web interface.

## 📁 Directory Structure

```
assets/
├── images/
│   ├── petting_zoo_hero.png    # Main landing page image
│   ├── sad_cat.jpg             # Error fallback for cat requests
│   ├── sad_dog.jpg             # Error fallback for dog requests
│   └── sad_duck.jpg            # Error fallback for duck requests
└── README.md                   # This file
```

## 🖼️ Image Usage

### Landing Page
- **File**: `images/petting_zoo_hero.png`
- **Usage**: Main hero image on the landing page
- **Fallback**: SVG placeholder if image fails to load

### Error Handling
- **Sad Cat**: `images/sad_cat.jpg` - Displayed when cat requests fail
- **Sad Dog**: `images/sad_dog.jpg` - Displayed when dog requests fail  
- **Sad Duck**: `images/sad_duck.jpg` - Displayed when duck requests fail

## 🔧 Adding Images

1. **Place images** in the `images/` directory
2. **Reference them** in HTML as `assets/images/filename.jpg`
3. **Update JavaScript** if adding new error images
4. **Test locally** to ensure images load correctly

## 📝 Image Requirements

- **Format**: JPG, PNG, or WebP
- **Size**: Optimized for web (under 500KB recommended)
- **Dimensions**: Appropriate for display context
- **Fallbacks**: Always provide fallback for critical images

## 🚀 Deployment

Images are served statically by FastAPI at `/assets/images/` and can be accessed at:
- `http://localhost:8000/assets/images/petting_zoo_hero.png`
- `http://localhost:8000/assets/images/sad_cat.jpg`
- etc.
