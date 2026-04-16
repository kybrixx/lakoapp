#!/bin/bash

echo "🚀 Creating Lako Structure in current directory..."
echo ""

# ============================================
# BACKEND
# ============================================
echo "📦 Creating Backend..."

mkdir -p backend/{routes,models,services,database/{migrations,seeds},uploads/{thumbnails,compressed,originals,profiles,products,posts,chat},logs,backups}

# Backend root files
touch backend/{__init__.py,main.py,config.py,database.py,auth.py,utils.py,image_handler.py}

# Routes
touch backend/routes/{__init__.py,auth_routes.py,customer_routes.py,vendor_routes.py,admin_routes.py,guest_routes.py,chat_routes.py,sync_routes.py,upload_routes.py}

# Models
touch backend/models/{__init__.py,user.py,vendor.py,product.py,review.py,post.py,chat.py,traffic.py,activity.py,sync_metadata.py,media.py}

# Services
touch backend/services/{__init__.py,auth_service.py,map_service.py,traffic_service.py,feed_service.py,analytics_service.py,chat_service.py,sync_service.py,image_service.py}

# Database
touch backend/database/schema.sql
touch backend/database/migrations/001_initial.sql
touch backend/database/seeds/admin_user.sql

# Config files
touch backend/{requirements.txt,.env.example,render.yaml,run.py}

# Keep directories
touch backend/logs/.gitkeep
touch backend/backups/.gitkeep
for dir in thumbnails compressed originals profiles products posts chat; do
    touch backend/uploads/$dir/.gitkeep
done

# ============================================
# FRONTEND
# ============================================
echo "🎨 Creating Frontend..."

mkdir -p frontend/{css,js,pages/{customer,vendor,admin,guest},components,assets/images}

# CSS
touch frontend/css/{main.css,auth.css,dashboard.css,components.css,guest.css}

# JS
touch frontend/js/{app.js,api.js,auth.js,map.js,heatmap.js,chart.js,chat.js,sync.js,localDB.js,imageHandler.js,utils.js}

# Main pages
touch frontend/index.html
touch frontend/pages/{landing.html,login.html,register.html,reset-password.html}

# Customer pages
touch frontend/pages/customer/{dashboard.html,news-feed.html,map.html,suggestions.html,search.html,shortlist.html,activities.html,vendor-profile.html,product-detail.html,chat.html,chat-list.html,profile.html}

# Vendor pages
touch frontend/pages/vendor/{dashboard.html,traffic.html,feed-preview.html,posts.html,catalog.html,reviews.html,inquiries.html,analytics.html,profile.html,settings.html}

# Admin pages
touch frontend/pages/admin/{login.html,dashboard.html,users.html,vendors.html,products.html,reviews.html,posts.html,reports.html,media.html,settings.html}

# Guest pages
touch frontend/pages/guest/{browse.html,map.html,vendor-profile.html,product-detail.html}

# Components
touch frontend/components/{header.html,footer.html,bottom-nav.html,sidebar.html,feed-card.html,vendor-card.html,product-card.html,review-card.html,chat-widget.html,image-uploader.html,image-viewer.html,modal.html}

# Assets - Images only
touch frontend/assets/images/{placeholder.jpg,default-avatar.png,default-vendor.png}

# Package.json
touch frontend/package.json

# ============================================
# ROOT
# ============================================
touch .gitignore README.md

echo ""
echo "✅ Structure created successfully in current directory!"
echo ""
echo "📁 Structure:"
ls -la
echo ""
echo "📁 backend/"
ls -la backend/
echo ""
echo "📁 frontend/"
ls -la frontend/